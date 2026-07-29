#!/usr/bin/env python3
"""FastGPT Knowledge Base Sync Script
Usage:
  python3 fastgpt-sync.py --paper <path_to_pdf>       # Import paper into FastGPT
  python3 fastgpt-sync.py --github <repo_dir>          # Import GitHub repo README into FastGPT
  python3 fastgpt-sync.py --course <course_dir>         # Import course files into FastGPT
  python3 fastgpt-sync.py --status                      # Check sync status
"""
import sys, os, json, subprocess, glob

KB_HOME = os.path.expanduser("~/knowledge-base")

def get_fastgpt_url():
    return "http://localhost:3000"

def get_dataset_id():
    """Returns the FastGPT knowledge base dataset ID from MongoDB"""
    try:
        result = subprocess.run(
            ["docker", "exec", "-i", "fastgpt-mongo", "mongosh", "fastgpt", "--quiet", "--eval",
             'db.datasets.findOne({name:"knowledge_base"},{_id:1})._id.str'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except:
        return None

def sync_paper(meta_path):
    """Print instructions for importing a paper into FastGPT"""
    print("\n=== FastGPT Paper Import ===")
    print("To import this paper into FastGPT knowledge base:")
    print("1. Open " + get_fastgpt_url())
    print("2. Go to: ??? -> knowledge_base")
    print("3. Click: Create -> Import")
    print("4. Select the PDF: " + meta_path.replace(".meta.json", ".pdf"))
    print("Done")

def sync_github(repo_dir):
    """Print instructions for importing GitHub repo into FastGPT"""
    readme = os.path.join(repo_dir, "README.md")
    if os.path.isfile(readme):
        print("\n=== FastGPT GitHub Import ===")
        print("README found at: " + readme + " (" + str(os.path.getsize(readme)) + " bytes)")
        print("To import into FastGPT knowledge base:")
        print("1. Open " + get_fastgpt_url())
        print("2. Go to: ??? -> knowledge_base")
        print("3. Click: Import -> File/Text")
        print("4. Upload: " + readme)
    else:
        print("No README found in " + repo_dir)

def sync_course(course_dir):
    """Print instructions for importing course files into FastGPT"""
    meta_file = os.path.join(course_dir, "course.meta.json")
    if os.path.isfile(meta_file):
        with open(meta_file, "r") as f:
            meta = json.load(f)
        print("\n=== FastGPT Course Import ===")
        print("Course: " + meta.get("course_name", "") + " (" + str(meta.get("file_count", 0)) + " files)")
        print("To import into FastGPT knowledge base:")
        print("1. Open " + get_fastgpt_url())
        print("2. Go to: ??? -> knowledge_base")
        print("3. Click: Import -> Folder (multiple files)")

def check_status():
    """Show sync status between file system and FastGPT"""
    print("\n=== Knowledge Base Sync Status ===\n")
    # Count local files
    papers = glob.glob(os.path.join(KB_HOME, "02_research/active/*.meta.json"))
    repos = glob.glob(os.path.join(KB_HOME, "02_research/active/_repos/*/repo.meta.json"))
    courses = glob.glob(os.path.join(KB_HOME, "01_courses/*/course.meta.json"))
    print("Local filesystem:")
    print("  Papers: " + str(len(papers)))
    print("  GitHub repos: " + str(len(repos)))
    print("  Courses: " + str(len(courses)))
    # Check FastGPT via MongoDB
    try:
        result = subprocess.run(
            ["docker", "exec", "-i", "fastgpt-mongo", "mongosh", "fastgpt", "--quiet", "--eval",
             'db.datasets.findOne({name:"knowledge_base"})._id.str'],
            capture_output=True, text=True, timeout=10
        )
        ds_id = result.stdout.strip()
        if ds_id:
            result2 = subprocess.run(
                ["docker", "exec", "-i", "fastgpt-mongo", "mongosh", "fastgpt", "--quiet", "--eval",
                 'db.dataset_collections.find({datasetId:ObjectId("' + ds_id + '")}).count()'],
                capture_output=True, text=True, timeout=10
            )
            count = result2.stdout.strip()
            print("\nFastGPT knowledge base:")
            print("  Collections: " + count)
    except:
        print("\nFastGPT: (unable to query - docker not available)")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "--status":
        check_status()
    elif cmd == "--paper" and len(sys.argv) > 2:
        sync_paper(os.path.abspath(sys.argv[2]))
    elif cmd == "--github" and len(sys.argv) > 2:
        sync_github(os.path.abspath(sys.argv[2]))
    elif cmd == "--course" and len(sys.argv) > 2:
        sync_course(os.path.abspath(sys.argv[2]))
    else:
        print("Unknown command. See --help")
        sys.exit(1)

if __name__ == "__main__":
    main()
