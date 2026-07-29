import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
cmd = 'docker exec fastgpt find /app -name "*.js" -path "*/pages/api/*" 2>/dev/null | head -60'
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
for line in r.stdout.strip().split(chr(10)):
    if line.strip():
        api_path = line.replace("/app/projects/app", "").replace("/app/packages", "").replace(".js", "").replace("index", "")
        print(f"  {api_path}")
