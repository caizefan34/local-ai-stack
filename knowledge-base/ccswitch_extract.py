#!/usr/bin/env python3
"""Extract conversation records from CC Switch LevelDB for QA training."""
import struct, sys, os, json, glob
LOCAL_APP_DATA = os.path.expandvars("%LOCALAPPDATA%")
DB_PATH = os.path.join(LOCAL_APP_DATA, "com.ccswitch.desktop", "EBWebView", "Default", "Local Storage", "leveldb")

def find_log_file():
    if not os.path.isdir(DB_PATH):
        print(f"[ERR] Not found: {DB_PATH}", file=sys.stderr); return None
    logs = glob.glob(os.path.join(DB_PATH, "*.log"))
    return max(logs, key=os.path.getsize) if logs else None

def extract(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    pos, records = 0, []
    while pos + 7 <= len(data):
        length = struct.unpack("<H", data[pos+4:pos+6])[0]
        rtype = data[pos+6]
        rd = data[pos+7:pos+7+length]
        pos += 7 + length
        if rtype == 1:
            parts = rd.split(b"\x00", 1)
            if len(parts) == 2:
                records.append((parts[0].decode("utf-8", errors="replace"),
                               parts[1].decode("utf-8", errors="replace")))
    return records

def main():
    log_file = find_log_file()
    if not log_file:
        sys.exit(1)
    print(f"Reading: {log_file}")
    records = extract(log_file)
    print(f"Records: {len(records)}")
    keywords = ["session", "chat", "message", "conv", "history", "ai", "msg", "dialog"]
    for k, v in records:
        if len(k) < 200 and any(x in k.lower() for x in keywords):
            print(f"\nKEY: {k}\nVALUE: {v[:1500]}\n---")

if __name__ == "__main__":
    main()
