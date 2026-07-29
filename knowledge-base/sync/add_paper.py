import sys, os, re, json, shutil, subprocess
from datetime import date

KB_HOME = os.path.expanduser("~/knowledge-base")
ACTIVE_DIR = os.path.join(KB_HOME, "02_research", "active")
ARCHIVED_DIR = os.path.join(KB_HOME, "02_research", "archived")

def extract_metadata_pdfplumber(pdf_path):
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            meta = pdf.metadata
            text = ""
            for page in pdf.pages[:5]:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            title = (meta.get("Title") or "").strip()
            author = (meta.get("Author") or "").strip()
            if not title and text:
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if lines:
                    title = lines[0][:120]
            return {
                "title": title or os.path.splitext(os.path.basename(pdf_path))[0],
                "author": author or "",
                "year": str(meta.get("CreationDate", str(date.today().year))),
                "source": ""
            }
    except ImportError:
        return None

def extract_metadata_pypdf2(pdf_path):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        meta = reader.metadata
        title = (meta.get("/Title") or "").strip()
        author = (meta.get("/Author") or "").strip()
        return {
            "title": title or os.path.splitext(os.path.basename(pdf_path))[0],
            "author": author or "",
            "year": str(meta.get("/CreationDate", str(date.today().year))),
            "source": ""
        }
    except ImportError:
        return None

def ask_user(prompt, default=None):
    result = input(prompt + (" [" + default + "]: " if default else ": ")).strip()
    return result if result else (default or "")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add_paper.py <path_to_pdf> [--tags tag1,tag2]")
        sys.exit(1)
    pdf_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(pdf_path):
        print("Error: File not found: " + pdf_path)
        sys.exit(1)
    tags = []
    for i, arg in enumerate(sys.argv):
        if arg == "--tags" and i + 1 < len(sys.argv):
            tags = [t.strip() for t in sys.argv[i+1].split(",")]

    # Extract metadata
    meta = extract_metadata_pdfplumber(pdf_path)
    if not meta:
        meta = extract_metadata_pypdf2(pdf_path)
    if not meta:
        print("Warning: No PDF extraction library found. Install with: pip3 install pdfplumber")
        meta = {"title": "", "author": "", "year": str(date.today().year), "source": ""}

    print("\n=== Paper Metadata ===")
    title = ask_user("Title", meta["title"])
    author = ask_user("Author", meta["author"])
    year = ask_user("Year", meta["year"][:4] if meta["year"] else str(date.today().year))
    source = ask_user("Source (journal/conference/arXiv)", meta["source"])
    tags_str = ask_user("Tags (comma separated)", ",".join(tags))

    # Build filename: Year_Author_Keyword.pdf
    author_short = re.sub(r'[^a-zA-Z0-9]', '', author.split(",")[0].split()[-1] if author else "unknown")[:20]
    title_keyword = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', title[:30]) if title else "untitled"
    new_name = year + "_" + author_short + "_" + title_keyword + ".pdf"
    new_name = re.sub(r'_+', '_', new_name)

    dest = os.path.join(ACTIVE_DIR, new_name)
    if os.path.exists(dest):
        print("Warning: " + new_name + " already exists!")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Aborted.")
            sys.exit(0)

    shutil.copy2(pdf_path, dest)
    print("Copied: " + pdf_path + " -> " + dest)

    # Write metadata
    meta_data = {
        "title": title,
        "author": author,
        "year": year,
        "source": source,
        "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
        "added_date": date.today().isoformat(),
        "original_path": pdf_path,
        "stored_path": dest
    }
    meta_path = os.path.splitext(dest)[0] + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)
    print("Metadata saved: " + meta_path)
    print("\nDone! Paper added to research/active/")

if __name__ == "__main__":
    main()
