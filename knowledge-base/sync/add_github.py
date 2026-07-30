import sys, os, json, shutil, subprocess, re
from datetime import date

KB_HOME = os.path.expanduser("~/knowledge-base")
ACTIVE_DIR = os.path.join(KB_HOME, "02_research", "active")
ARCHIVED_DIR = os.path.join(KB_HOME, "02_research", "archived")
REPOS_DIR = os.path.join(ACTIVE_DIR, "_repos")

def parse_github_url(url):
    url = url.strip().rstrip("/")
    m = re.match(r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:\/.*)?$", url)
    if not m:
        return None, None
    return m.group(1), m.group(2)

def get_latest_commit(repo_path):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%ci|%s"],
            cwd=repo_path, capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split("|", 2)
            return parts[0], parts[1], parts[2] if len(parts) > 2 else ""
    except:
        pass
    return "", "", ""

def ask_user(prompt, default=None):
    result = input(prompt + (" [" + default + "]: " if default else ": ")).strip()
    return result if result else (default or "")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add_github.py <github_url> [--tags tag1,tag2]")
        sys.exit(1)
    url = sys.argv[1]
    tags = []
    for i, arg in enumerate(sys.argv):
        if arg == "--tags" and i + 1 < len(sys.argv):
            tags = [t.strip() for t in sys.argv[i+1].split(",")]

    owner, repo = parse_github_url(url)
    if not owner or not repo:
        print("Error: Invalid GitHub URL: " + url)
        sys.exit(1)

    repo_dir_name = owner + "-" + repo
    dest_dir = os.path.join(REPOS_DIR, repo_dir_name)
    should_clone = not os.path.exists(dest_dir)
    if os.path.exists(dest_dir):
        print("Warning: Repository already exists at " + dest_dir)
        overwrite = input("Re-clone? (y/N): ").strip().lower()
        if overwrite == "y":
            shutil.rmtree(dest_dir)
            should_clone = True
        else:
            print("Using existing clone.")
    if should_clone:
        os.makedirs(REPOS_DIR, exist_ok=True)
        print("Cloning " + url + " (depth=1)...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, dest_dir],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print("Error cloning: " + result.stderr)
            sys.exit(1)
        print("Clone complete.")

    # Find README
    readme = None
    for fname in ["README.md", "readme.md", "README", "Readme.md"]:
        candidate = os.path.join(dest_dir, fname)
        if os.path.isfile(candidate):
            readme = candidate
            break

    if readme:
        readme_dest = os.path.join(dest_dir, "README.md")
        if readme != readme_dest:
            shutil.copy2(readme, readme_dest)
        print("README found and preserved.")
    else:
        print("Warning: No README found in repository.")

    # Get metadata
    commit_hash, commit_date, commit_msg = get_latest_commit(dest_dir)
    print("\n=== Repository Info ===")
    desc = ask_user("Description", repo)
    tags_str = ask_user("Tags (comma separated)", ",".join(tags))

    # Write metadata
    meta = {
        "repo_url": url,
        "owner": owner,
        "repo_name": repo,
        "local_path": dest_dir,
        "description": desc,
        "last_commit": commit_hash,
        "last_commit_date": commit_date,
        "last_commit_message": commit_msg,
        "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
        "added_date": date.today().isoformat()
    }
    meta_path = os.path.join(dest_dir, "repo.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("Metadata saved: " + meta_path)
    print("\nDone! Repository added to research/active/_repos/")

if __name__ == "__main__":
    main()
