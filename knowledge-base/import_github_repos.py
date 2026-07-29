#!/usr/bin/env python3
"""Import GitHub repos as FastGPT knowledge base documents."""
import os, sys, json, tempfile, subprocess
from pathlib import Path

REPOS = [
    "https://github.com/ggml-org/llama.cpp",
    "https://github.com/labring/FastGPT",
    "https://github.com/ollama/ollama",
    "https://github.com/huggingface/transformers",
    "https://github.com/huggingface/peft",
]

def clone_and_extract(repo_url: str) -> list[dict]:
    """Clone a repo and extract text content as documents."""
    repo_name = repo_url.rstrip("/").split("/")[-1]
    print(f"  Cloning {repo_name}...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            ["git", "clone", "--depth=1", repo_url, str(Path(tmpdir) / repo_name)],
            capture_output=True, check=False
        )
        docs = []
        repo_path = Path(tmpdir) / repo_name
        for ext in [".md", ".py", ".js", ".ts", ".rs", ".go", ".java", ".cpp", ".txt"]:
            for f in repo_path.rglob(f"*{ext}"):
                if ".git" in str(f) or "node_modules" in str(f):
                    continue
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if len(content) > 100:
                        docs.append({
                            "title": f"{repo_name}/{f.relative_to(repo_path)}",
                            "content": content[:8000],
                            "source": repo_url,
                        })
                except:
                    pass
        return docs

def main():
    all_docs = []
    for repo in REPOS:
        docs = clone_and_extract(repo)
        all_docs.extend(docs)
        print(f"    {len(docs)} documents extracted")
    
    output = "knowledge_base_docs.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, ensure_ascii=False, indent=2)
    print(f"\nTotal: {len(all_docs)} documents saved to {output}")

if __name__ == "__main__":
    main()
