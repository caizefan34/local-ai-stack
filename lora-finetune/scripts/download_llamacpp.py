import urllib.request, os, sys

url = "https://github.com/ggml-org/llama.cpp/releases/download/b10173/llama-b10173-bin-win-cuda-13.3-x64.zip"
out = r"%USERPROFILE%\AppData\Local\Temp\llama-cpp-cuda.zip"
print(f"Downloading to {out}...")
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=600)
total = int(resp.headers.get("Content-Length", 0))
print(f"Total: {total/1e6:.1f} MB")
with open(out, "wb") as f:
    dl = 0
    while True:
        chunk = resp.read(65536)
        if not chunk: break
        f.write(chunk)
        dl += len(chunk)
        sys.stdout.write(f"\r{dl/1e6:.1f} MB / {total/1e6:.1f} MB")
        sys.stdout.flush()
print()
print("Complete!")