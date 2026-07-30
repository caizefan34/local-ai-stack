#!/usr/bin/env python3
import sys, os, json, shutil, hashlib, datetime
KB_HOME = os.path.expanduser("~/knowledge-base")
COURSES_DIR = os.path.join(KB_HOME, "01_courses")
REFS_DIR = os.path.join(KB_HOME, "03_references")
SYNC_LOG = os.path.join(KB_HOME, "_scripts", ".sync_log.json")
SOURCES = [
    {"path": os.environ.get("KB_WINDOWS_SOURCE", "/mnt/d/knowledge"), "target": COURSES_DIR, "type": "course"},
    {"path": os.environ.get("KB_WINDOWS_REF_SOURCE", "/mnt/d/references"), "target": REFS_DIR, "type": "reference"},
]
SUPPORTED_EXTS = {".md", ".pdf", ".ppt", ".pptx", ".txt", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".zip"}
def load_log():
    if os.path.isfile(SYNC_LOG):
        with open(SYNC_LOG) as f:
            return json.load(f)
    return {"last_sync": "", "files": {}}
def save_log(log):
    log["last_sync"] = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(SYNC_LOG), exist_ok=True)
    with open(SYNC_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
def sync_source(src_info, log, dry_run):
    src = src_info["path"]
    dst = src_info["target"]
    stype = src_info["type"]
    if not os.path.isdir(src):
        print("  [SKIP] " + src + " not found")
        return {"new":0,"updated":0,"skipped":0}
    os.makedirs(dst, exist_ok=True)
    stats = {"new":0,"updated":0,"skipped":0}
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SUPPORTED_EXTS:
                continue
            src_file = os.path.join(root, fname)
            rel_path = os.path.relpath(src_file, src)
            dst_file = os.path.join(dst, rel_path) if rel != "." else os.path.join(dst, fname)
            if rel != ".":
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            key = stype + ":" + rel_path
            if os.path.isfile(dst_file):
                sm = os.path.getmtime(src_file)
                dm = os.path.getmtime(dst_file)
                if abs(sm - dm) < 1:
                    stats["skipped"] += 1
                    continue
            if dry_run:
                print("  [NEW] " + rel_path)
                stats["new"] += 1
            else:
                try:
                    shutil.copy2(src_file, dst_file)
                    log["files"][key] = {"source":src_file,"dest":dst_file,"mtime":os.path.getmtime(src_file),"synced_at":datetime.datetime.now().isoformat()}
                    action = "UPD" if os.path.isfile(dst_file) else "NEW"
                    print("  [" + action + "] " + rel_path)
                    if action == "NEW":
                        stats["new"] += 1
                    else:
                        stats["updated"] += 1
                except Exception as e:
                    print("  [ERR] " + rel_path + ": " + str(e))
    return stats
def main():
    dry = "--dry-run" in sys.argv
    print("=" * 60)
    print("  KB SYNC FROM WINDOWS")
    print("  " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    if dry:
        print("  [DRY RUN]")
    print("=" * 60)
    log = load_log()
    total = {"new":0,"updated":0,"skipped":0}
    for src in SOURCES:
        name = os.path.basename(src["path"])
        print("\n[" + name + "]")
        st = sync_source(src, log, dry)
        for k in total:
            total[k] += st[k]
    if not dry:
        save_log(log)
    print("\n---")
    print("New: " + str(total["new"]) + " | Updated: " + str(total["updated"]) + " | Skipped: " + str(total["skipped"]))
    print("---")
    return total["new"] + total["updated"] > 0
if __name__ == "__main__":
    has = main()
    if not has:
        print("All up to date!")
