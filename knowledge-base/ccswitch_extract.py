import struct, sys

with open("/home/user/AppData/Local/com.ccswitch.desktop/EBWebView/Default/Local Storage/leveldb/000003.log", "rb") as f:
    data = f.read()

pos = 0
records = []
while pos + 7 <= len(data):
    length = struct.unpack("<H", data[pos+4:pos+6])[0]
    rtype = data[pos+6]
    rd = data[pos+7:pos+7+length]
    pos += 7 + length
    if rtype == 1:
        parts = rd.split(b"\x00", 1)
        if len(parts) == 2:
            records.append((parts[0].decode("utf-8", errors="replace"), parts[1].decode("utf-8", errors="replace")))

sys.stdout.buffer.write(("Total records: " + str(len(records)) + "\n").encode("utf-8"))
for k, v in records:
    if len(k) < 200:
        sys.stdout.buffer.write(("KEY: " + k + "  len=" + str(len(v)) + "\n").encode("utf-8", errors="replace"))
        if any(x in k.lower() for x in ["session","chat","message","conv","history","ai","msg","dialog"]):
            sys.stdout.buffer.write(("VALUE: " + v[:1000] + "\n---\n").encode("utf-8", errors="replace"))
