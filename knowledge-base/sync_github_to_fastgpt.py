#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, hashlib, time, subprocess
from datetime import datetime

LOG_FILE = os.path.expanduser("~/sync_github_fastgpt.log")
REPOS_DIR = os.path.expanduser("~/learning_repos")
os.makedirs(REPOS_DIR, exist_ok=True)

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def gh_api(path):
    result = subprocess.run(["gh", "api", path, "--paginate", "--jq", ".[].full_name"],
                          capture_output=True, timeout=60)
    out = result.stdout.decode("utf-8", errors="replace")
    return [x.strip() for x in out.strip().split("\n") if x.strip() and "/" in x]

def get_readme(repo):
    result = subprocess.run(["gh", "api", f"repos/{repo}/readme", "--jq", ".content"],
                          capture_output=True, timeout=15)
    if result.returncode == 0 and result.stdout.strip():
        import base64
        try:
            content = result.stdout.strip()
            if content.startswith(b'"') and content.endswith(b'"'):
                content = content[1:-1]
            return base64.b64decode(content).decode("utf-8", errors="replace")
        except: return None
    return None

def get_repo_info(repo):
    result = subprocess.run(["gh", "api", f"repos/{repo}", "--jq",
                           "{description: .description, language: .language, stars: .stargazers_count, topics: .topics}"],
                          capture_output=True, timeout=10)
    if result.returncode == 0:
        try: return json.loads(result.stdout.decode("utf-8", errors="replace"))
        except: pass
    return {}

def import_to_fastgpt(repo_name, content, info):
    try:
        from pymongo import MongoClient
        from bson.objectid import ObjectId
    except ImportError:
        log("  pymongo not installed"); return False
    try:
        client = MongoClient("mongodb://localhost:27017/fastgpt?directConnection=true", serverSelectionTimeoutMS=5000)
        client.admin.command("ping")  # Check connection
        db = client["fastgpt"]
    except Exception as e:
        log(f"  FastGPT/MongoDB not available: {str(e)[:80]}")
        return False

    kb_id = ObjectId("6a675d6c59fb544cd040db65")
    team_id = ObjectId("6a67174fa04ecda8f06e29a3")
    tmb_id = ObjectId("6a67174fa04ecda8f06e29aa")
    coll_name = repo_name.replace("/", "_")

    if db["dataset_collections"].find_one({"datasetId": kb_id, "name": coll_name}):
        client.close()
        return True  # Skip silently

    now = time.strftime("%Y-%m-%d %H:%M:%S.000000")
    coll_id = ObjectId()
    desc = info.get("description") or ""
    lang = info.get("language") or ""
    stars = info.get("stars", 0)
    topics = ", ".join(info.get("topics") or [])
    header = f"# {repo_name}\n\n**Stars:** {stars}  **Language:** {lang}\n**Topics:** {topics}\n**Description:** {desc}\n\n---\n\n"
    full_content = header + (content or "")

    db["dataset_collections"].insert_one({
        "_id": coll_id, "teamId": team_id, "tmbId": tmb_id, "datasetId": kb_id,
        "type": "file", "name": coll_name, "trainingType": "chunk",
        "chunkSize": 1000, "rawTextLength": len(full_content),
        "hashRawText": hashlib.md5(full_content.encode()).hexdigest(),
        "createTime": now, "updateTime": now, "__v": 0
    })

    paras = full_content.split("\n\n")
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) < 1000:
            cur = (cur + "\n\n" + p) if cur else p
        else:
            if cur: chunks.append(cur.strip())
            cur = p
    if cur: chunks.append(cur.strip())

    entries = [{
        "_id": ObjectId(), "teamId": team_id, "tmbId": tmb_id,
        "datasetId": kb_id, "collectionId": coll_id, "q": chunk, "a": "",
        "fullTextToken": chunk[:500], "indexes": [], "chunkIndex": str(ci),
        "updateTime": now, "__v": 0
    } for ci, chunk in enumerate(chunks) if len(chunk) >= 20]

    if entries:
        db["dataset_datas"].insert_many(entries)
        log(f"  + {repo_name}: {len(entries)} chunks")
    client.close()
    return True

def main():
    log("=== GitHub -> FastGPT Sync ===")

    # Check gh auth
    if subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=10).returncode != 0:
        log("gh not authenticated"); return

    # Check FastGPT/MongoDB
    try:
        from pymongo import MongoClient
        c = MongoClient("mongodb://localhost:27017/fastgpt?directConnection=true", serverSelectionTimeoutMS=5000)
        c.admin.command("ping")
        c.close()
    except:
        log("FastGPT/MongoDB not running, will try next time")
        return

    log("Fetching starred...")
    starred = gh_api("user/starred")
    log(f"  Starred: {len(starred)}")

    log("Fetching own repos...")
    own = gh_api("user/repos")
    log(f"  Own: {len(own)}")

    repos = list(set(starred + own))
    log(f"  Total: {len(repos)}")

    new_count = 0
    for i, repo in enumerate(repos):
        log(f"[{i+1}/{len(repos)}] {repo}...")
        readme = get_readme(repo)
        if not readme:
            log(f"  No README")
            continue

        info = get_repo_info(repo)
        local = os.path.join(REPOS_DIR, repo.replace("/", "_") + ".md")
        with open(local, "w", encoding="utf-8") as f:
            f.write(f"# {repo}\n\n**Stars:** {info.get('stars',0)}  **Language:** {info.get('language','')}\n")
            f.write(f"**Topics:** {', '.join(info.get('topics',[]) or [])}\n")
            f.write(f"**Description:** {info.get('description','')}\n\n---\n\n")
            f.write(readme)

        if import_to_fastgpt(repo, readme, info):
            new_count += 1
        time.sleep(0.3)

    log(f"=== Done. New repos: {new_count} ===")

if __name__ == "__main__":
    main()
