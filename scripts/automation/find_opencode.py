import os, sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
paths = [
    os.path.expanduser("~/.opencode"),
    os.path.expanduser("~/AppData/Roaming/opencode"),
    os.path.expanduser("~/AppData/Local/opencode"),
    os.path.expanduser("~/AppData/Local/Programs/opencode"),
]
for p in paths:
    if os.path.isdir(p):
        print(f"Found: {p}")
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                print(f"  {fp} ({os.path.getsize(fp)} bytes)")
                if f.endswith(".db"):
                    try:
                        conn = sqlite3.connect(fp)
                        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                        print(f"    Tables: {[t[0] for t in tables]}")
                        conn.close()
                    except Exception as e:
                        print(f"    Error: {str(e)[:100]}")
