import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
# Check the server dir structure
for cmd in ["docker exec fastgpt ls -la /app/ 2>/dev/null", "docker exec fastgpt find /app -maxdepth 4 -name '*.js' 2>/dev/null | head -40"]:
    r = subprocess.run(cmd, capture_output=True, shell=True)
    print(r.stdout.decode("utf-8", errors="replace")[:2000])
    print("---")
