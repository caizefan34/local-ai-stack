import subprocess, sys, time
proc = subprocess.Popen(
    [sys.executable, "/home/user/local-model-lab/reranker/server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
with open("/home/user/local-model-lab/reranker/pid.txt", "w") as f:
    f.write(str(proc.pid))
print(f"Reranker PID: {proc.pid} started")
