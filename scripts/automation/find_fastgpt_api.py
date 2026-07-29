import subprocess, sys, json
sys.stdout.reconfigure(encoding="utf-8")
r = subprocess.run("docker exec fastgpt find /app -type d -path '*/api/*' 2>/dev/null", capture_output=True, text=True, shell=True)
print("API dirs:")
for line in r.stdout.strip().split(chr(10)):
    if line.strip(): print(f"  {line}")
r2 = subprocess.run("docker exec fastgpt find /app -name '*.js' -path '*/api/*' 2>/dev/null | head -30", capture_output=True, text=True, shell=True)
print("\nAPI files:")
for line in r2.stdout.strip().split(chr(10)):
    if line.strip(): print(f"  {line}")
