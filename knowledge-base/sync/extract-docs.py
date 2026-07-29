#!/usr/bin/env python3
"""Extract text from PDF, DOCX, PPTX files using pure Python where possible."""
import sys, os, zipfile, xml.etree.ElementTree as ET, re, subprocess

SUPPORTED = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.md', '.txt'}

def extract_docx(path):
    """Extract text from .docx files (pure Python, no deps)"""
    try:
        with zipfile.ZipFile(path) as z:
            # Try word/document.xml first
            xml_paths = [p for p in z.namelist() if p.startswith('word/document') and p.endswith('.xml')]
            if not xml_paths:
                return None
            xml_content = z.read(sorted(xml_paths)[0])
        root = ET.fromstring(xml_content)
        ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        texts = []
        for t in root.iter('{' + ns + '}t'):
            if t.text:
                texts.append(t.text)
        return '\n'.join(texts) if texts else None
    except Exception as e:
        return None

def extract_pptx(path):
    """Extract text from .pptx files (pure Python, no deps)"""
    try:
        with zipfile.ZipFile(path) as z:
            slides = sorted([f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')])
            if not slides:
                return None
            texts = []
            ns = 'http://schemas.openxmlformats.org/drawingml/2006/main'
            for slide in slides:
                xml_content = z.read(slide)
                root = ET.fromstring(xml_content)
                slide_texts = []
                for t in root.iter('{' + ns + '}t'):
                    if t.text:
                        slide_texts.append(t.text)
                if slide_texts:
                    texts.append(' '.join(slide_texts))
        return '\n\n'.join(texts) if texts else None
    except Exception as e:
        return None

def extract_pdf(path):
    """Extract text from PDF using available tools"""
    # Try pdftotext first
    try:
        result = subprocess.run(['pdftotext', path, '-'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try Node.js pdf-parse (if available through docker)
    try:
        result = subprocess.run(
            ['docker', 'exec', '-i', 'fastgpt', 'node', '-e',
             'const fs=require("fs"); const path=' + "'" + path + "'" + '; console.log(fs.readFileSync(path, "utf8").substring(0,1000))'],
            capture_output=True, text=True, timeout=10
        )
    except:
        pass
    
    return None

def process_file(filepath, output_base):
    """Extract text from file and save as .txt next to it"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext in ('.md', '.txt'):
        return False  # Already handled
    
    if ext == '.pdf':
        text = extract_pdf(filepath)
    elif ext in ('.docx', '.doc'):
        text = extract_docx(filepath)
    elif ext in ('.pptx', '.ppt'):
        text = extract_pptx(filepath)
    else:
        return False
    
    if text and text.strip():
        # Save as .txt alongside original
        txt_path = filepath + '.extracted.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'  [EXT] {os.path.basename(filepath)} -> {os.path.basename(txt_path)} ({len(text)} chars)')
        return True
    return False

def main():
    kb_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/knowledge-base')
    if not os.path.isdir(kb_dir):
        print(f'Directory not found: {kb_dir}')
        return 1
    
    count = 0
    for root, dirs, files in os.walk(kb_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in ('.pdf', '.docx', '.doc', '.pptx', '.ppt'):
                continue
            if fname.endswith('.extracted.txt'):
                continue
            fpath = os.path.join(root, fname)
            if process_file(fpath, root):
                count += 1
    
    print(f'Extracted: {count} files')
    return 0

if __name__ == '__main__':
    sys.exit(main())
