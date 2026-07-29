#!/usr/bin/env python3
"""Knowledge Base Maintenance Report
Usage: python3 report.py
"""
import os, json, glob, datetime

KB_HOME = os.path.expanduser("~/knowledge-base")

def main():
    print("=" * 60)
    print("  KNOWLEDGE BASE STATUS REPORT")
    print("  Generated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 60)

    # 01_courses
    courses = glob.glob(os.path.join(KB_HOME, "01_courses/*/course.meta.json"))
    total_course_files = 0
    print("\n[01_courses] University Courses")
    print("  Courses: " + str(len(courses)))
    for mf in courses:
        with open(mf, "r") as f:
            meta = json.load(f)
        print("    - " + meta.get("course_name", "?") + " (" + str(meta.get("file_count", 0)) + " files, added " + meta.get("added_date", "?") + ")")
        total_course_files += meta.get("file_count", 0)
    if not courses:
        print("    (empty)")

    # 02_research
    print("\n[02_research] Research")
    papers = glob.glob(os.path.join(KB_HOME, "02_research/active/*.meta.json"))
    print("  Papers (active): " + str(len(papers)))
    repos = glob.glob(os.path.join(KB_HOME, "02_research/active/_repos/*/repo.meta.json"))
    print("  GitHub repos: " + str(len(repos)))
    for mf in repos:
        with open(mf, "r") as f:
            meta = json.load(f)
        dt = meta.get("last_commit_date", "")[:10] if meta.get("last_commit_date") else "?"
        print("    - " + meta.get("repo_name", "?") + " (last: " + dt + ")")
    archived = glob.glob(os.path.join(KB_HOME, "02_research/archived/*"))
    print("  Archived projects: " + str(len(archived)))

    # 03_references
    refs = []
    for root, dirs, files in os.walk(os.path.join(KB_HOME, "03_references")):
        for f in files:
            if f != "README.md":
                refs.append(os.path.join(root, f))
    print("\n[03_references] References")
    print("  Files: " + str(len(refs)))

    # Disk usage
    total_size = 0
    for root, dirs, files in os.walk(KB_HOME):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except:
                pass
    print("\n[Storage]")
    print("  KB Home: " + KB_HOME)
    print("  Total size: " + str(round(total_size / (1024*1024), 1)) + " MB")

    # Summary
    print("\n[Summary]")
    print("  Total papers: " + str(len(papers)))
    print("  Total repos: " + str(len(repos)))
    print("  Total courses: " + str(len(courses)))
    print("  Total course files: " + str(total_course_files))
    print("  Total reference files: " + str(len(refs)))
    print("=" * 60)

if __name__ == "__main__":
    main()
