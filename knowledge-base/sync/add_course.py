import sys, os, json, shutil, re
from datetime import date

KB_HOME = os.path.expanduser("~/knowledge-base")
COURSES_DIR = os.path.join(KB_HOME, "01_courses")

SUPPORTED = (".pdf", ".ppt", ".pptx", ".md", ".txt", ".doc", ".docx", ".zip")

def slugify(text):
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "_", text).strip("_")
    return text[:40]

def ask_user(prompt, default=None):
    result = input(prompt + (" [" + default + "]: " if default else ": ")).strip()
    return result if result else (default or "")

def main():
    print("=== Add Course Material ===\n")
    course_name = ask_user("Course name")
    if not course_name:
        print("Error: Course name is required.")
        sys.exit(1)
    course_code = ask_user("Course code (optional)")
    semester = ask_user("Semester (e.g. 2026-Spring)")
    instructor = ask_user("Instructor (optional)")
    tags_str = ask_user("Tags (comma separated, optional)")

    # Create course directory
    dir_name = (course_code + "_" if course_code else "") + slugify(course_name)
    course_dir = os.path.join(COURSES_DIR, dir_name)
    os.makedirs(course_dir, exist_ok=True)
    print("Course directory: " + course_dir)

    # Process files
    files_added = []
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            continue
        src = os.path.abspath(arg)
        if not os.path.isfile(src):
            print("Warning: Not a file, skipping: " + src)
            continue
        ext = os.path.splitext(src)[1].lower()
        if ext not in SUPPORTED:
            print("Warning: Unsupported format " + ext + ", skipping: " + src)
            continue
        dst = os.path.join(course_dir, os.path.basename(src))
        if os.path.exists(dst):
            base, ext2 = os.path.splitext(dst)
            dst = base + "_" + date.today().isoformat() + ext2
        shutil.copy2(src, dst)
        files_added.append(os.path.basename(dst))
        print("Added: " + os.path.basename(dst))

    if not files_added:
        print("No files added. You can add files later with:")
        print("  cp <files> " + course_dir + "/")

    # Generate course metadata
    meta = {
        "course_name": course_name,
        "course_code": course_code,
        "semester": semester,
        "instructor": instructor,
        "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
        "files": files_added,
        "file_count": len(files_added),
        "added_date": date.today().isoformat(),
        "directory": course_dir
    }
    meta_path = os.path.join(course_dir, "course.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("Metadata saved: " + meta_path)
    print("\nDone! Course material added to 01_courses/")

if __name__ == "__main__":
    main()
