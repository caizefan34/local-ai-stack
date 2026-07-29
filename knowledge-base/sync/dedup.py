#!/usr/bin/env python3
"""Knowledge Base Cleanup & Dedup Tool

Usage:
  python3 dedup.py --check          # Quick check for duplicates
  python3 dedup.py --outdated YEARS # Find outdated courses (default: 3 years)
  python3 dedup.py --clean          # Interactive cleanup
"""
import sys, os, json, hashlib, glob
from datetime import datetime, date

KB_HOME = os.path.expanduser("~/knowledge-base")
OUTDATED_THRESHOLD_YEARS = 3

def file_hash(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates():
    """Find files with identical content (by MD5 hash)"""
    hashes = {}
    duplicates = []
    for root, dirs, files in os.walk(KB_HOME):
        # Skip _scripts and _template
        if "_scripts" in root or "_template" in root:
            continue
        for fname in files:
            if fname.endswith(".meta.json") or fname == "README.md":
                continue
            fpath = os.path.join(root, fname)
            try:
                h = file_hash(fpath)
                if h in hashes:
                    duplicates.append((hashes[h], fpath))
                else:
                    hashes[h] = fpath
            except:
                pass
    return duplicates, hashes

def find_similar_names():
    """Find files with very similar names (potential near-duplicates)"""
    files_by_name = {}
    similar = []
    for root, dirs, files in os.walk(KB_HOME):
        if "_scripts" in root or "_template" in root:
            continue
        for fname in files:
            if fname.endswith(".meta.json") or fname == "README.md":
                continue
            # Normalize name for comparison
            name = os.path.splitext(fname)[0].lower()
            name = "".join(c for c in name if c.isalnum())
            if name in files_by_name:
                similar.append((files_by_name[name], os.path.join(root, fname)))
            else:
                files_by_name[name] = os.path.join(root, fname)
    return similar

def find_outdated_courses(years=OUTDATED_THRESHOLD_YEARS):
    """Find course materials older than threshold"""
    cutoff = date.today().replace(year=date.today().year - years)
    outdated = []
    for meta_file in glob.glob(os.path.join(KB_HOME, "01_courses/*/course.meta.json")):
        with open(meta_file, "r") as f:
            meta = json.load(f)
        added = meta.get("added_date", "")
        if added:
            try:
                added_date = datetime.strptime(added, "%Y-%m-%d").date()
                if added_date < cutoff:
                    outdated.append((meta_file, meta.get("course_name", "?"), added))
            except:
                pass
    return outdated, cutoff

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "--check":
        print("=== Duplicate Check ===\n")
        duplicates, _ = find_duplicates()
        if duplicates:
            print("Identical duplicates found:")
            for orig, dup in duplicates:
                print("  Original: " + orig)
                print("  Duplicate: " + dup)
                print()
        else:
            print("No identical duplicates found.")
        
        print("\n=== Similar Names ===")
        similar = find_similar_names()
        if similar:
            print("Files with similar names:")
            for f1, f2 in similar:
                print("  " + f1)
                print("  " + f2)
                print()
        else:
            print("No similar names found.")

    elif cmd == "--outdated":
        years = int(sys.argv[2]) if len(sys.argv) > 2 else OUTDATED_THRESHOLD_YEARS
        outdated, cutoff = find_outdated_courses(years)
        print("=== Outdated Course Materials ===")
        print("Cutoff date: " + str(cutoff) + " (older than " + str(years) + " years)\n")
        if outdated:
            for meta_file, name, added in outdated:
                print("  Course: " + name)
                print("  Added: " + added)
                print("  Meta: " + meta_file)
                print()
        else:
            print("No outdated courses found.")

    elif cmd == "--clean":
        print("=== Interactive Cleanup ===\n")
        
        # Step 1: Check duplicates
        duplicates, all_hashes = find_duplicates()
        if duplicates:
            print("Found " + str(len(duplicates)) + " duplicate file(s).")
            for orig, dup in duplicates:
                print("  Duplicate: " + dup)
                ans = input("  Remove this file? (y/N): ").strip().lower()
                if ans == "y":
                    os.remove(dup)
                    print("    Removed.")
                else:
                    print("    Skipped.")
        else:
            print("No duplicates found.")
        
        # Step 2: Check similar names
        similar = find_similar_names()
        if similar:
            print("\nFound " + str(len(similar)) + " similar-name file pair(s).")
            for f1, f2 in similar:
                print("  " + os.path.basename(f1) + " <-> " + os.path.basename(f2))
                ans = input("  Review? (y/N): ").strip().lower()
                if ans == "y":
                    print("  1: " + f1)
                    print("  2: " + f2)
                    rem = input("  Remove which? (1/2/skip): ").strip()
                    if rem == "1":
                        os.remove(f1)
                        print("    Removed 1.")
                    elif rem == "2":
                        os.remove(f2)
                        print("    Removed 2.")
                    else:
                        print("    Skipped.")
        
        # Step 3: Check outdated courses
        outdated, cutoff = find_outdated_courses()
        if outdated:
            print("\nFound " + str(len(outdated)) + " outdated course(s) (before " + str(cutoff) + ").")
            for meta_file, name, added in outdated:
                ans = input("  Archive " + name + " (added " + added + ")? (y/N): ").strip().lower()
                if ans == "y":
                    course_dir = os.path.dirname(meta_file)
                    archive_dir = os.path.join(KB_HOME, "02_research", "archived", os.path.basename(course_dir))
                    os.makedirs(os.path.dirname(archive_dir), exist_ok=True)
                    os.rename(course_dir, archive_dir)
                    print("    Archived to: " + archive_dir)
        
        print("\nCleanup complete.")

if __name__ == "__main__":
    main()
