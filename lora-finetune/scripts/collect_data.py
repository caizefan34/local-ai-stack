"""
数据采集工具 — 支持多种来源导入训练数据

用法:
  python scripts/collect_data.py

支持的来源:
  1. JSON 文件导入（标准格式）
  2. CSV 文件导入
  3. 手动输入问答对
  4. 从 FastGPT API 导出对话
  5. 从 Markdown 对话记录提取
"""
import json, os, sys, csv, glob
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "train.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    # 合并现有数据
    existing = []
    if os.path.exists(OUTPUT_FILE):
        existing = load_json(OUTPUT_FILE)
    all_data = existing + data
    # 去重（按 instruction 去重）
    seen = set()
    unique = []
    for item in all_data:
        key = item.get("instruction", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"[OK] 已保存 {len(data)} 条新数据到 {OUTPUT_FILE}")
    print(f"    去重后总量: {len(unique)} 条")
    return unique

def convert_ccswitch_format(raw_data):
    """尝试解析 CC Switch 可能的导出格式"""
    converted = []
    for item in raw_data:
        # 支持多种 Key 命名
        q = item.get("query") or item.get("question") or item.get("user") or item.get("prompt") or ""
        a = item.get("answer") or item.get("response") or item.get("assistant") or item.get("completion") or ""
        if isinstance(q, list):
            q = " ".join(q)
        if isinstance(a, list):
            a = " ".join(a)
        if q.strip() and a.strip():
            converted.append({"instruction": q.strip(), "output": a.strip()})
    return converted

def main():
    print("=" * 60)
    print("训练数据采集工具")
    print("=" * 60)
    print()
    print("支持的输入格式:")
    print("  1. JSON 文件 (标准 Alpaca 格式)")
    print("  2. JSON 文件 (CC Switch / ChatGPT 导出)")
    print("  3. CSV 文件 (query,answer 两列)")
    print("  4. 纯文本对话记录")
    print("  5. 从 FastGPT 对话日志导入")
    print()
    path = input("输入文件路径（拖拽文件到窗口）: ").strip().strip("'\"")

    if not os.path.exists(path):
        print(f"[ERR] 文件不存在: {path}")
        return

    ext = os.path.splitext(path)[1].lower()
    data = []

    if ext == ".json":
        raw = load_json(path)
        # 自动检测格式
        if isinstance(raw, list):
            if raw and "messages" in raw[0]:
                # ShareGPT 格式
                for item in raw:
                    msgs = item.get("messages", [])
                    user = [m for m in msgs if m.get("role") == "user"]
                    asst = [m for m in msgs if m.get("role") == "assistant"]
                    for u, a in zip(user, asst):
                        data.append({"instruction": u["content"], "output": a["content"]})
            elif raw and "instruction" in raw[0]:
                data = raw  # 标准 Alpaca
            else:
                data = convert_ccswitch_format(raw)
        print(f"  解析到 {len(data)} 条问答对")

    elif ext == ".csv":
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                q = row.get("query") or row.get("question") or row.get("user") or ""
                a = row.get("answer") or row.get("response") or row.get("assistant") or ""
                if q.strip() and a.strip():
                    data.append({"instruction": q.strip(), "output": a.strip()})
        print(f"  解析到 {len(data)} 条问答对")

    elif ext == ".txt" or ext == ".md":
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        lines = text.strip().split("\n\n")
        for block in lines:
            lines_b = block.strip().split("\n")
            q = ""
            a = ""
            for line in lines_b:
                if line.startswith("Q:") or line.startswith("问:") or line.startswith("用户:"):
                    q = line.split(":", 1)[1].strip()
                elif line.startswith("A:") or line.startswith("答:") or line.startswith("AI:") or line.startswith("助手:"):
                    a = line.split(":", 1)[1].strip()
            if q and a:
                data.append({"instruction": q, "output": a})
        print(f"  解析到 {len(data)} 条问答对")
    else:
        print(f"[ERR] 不支持的文件格式: {ext}")
        return

    if data:
        # 显示前 3 条预览
        print()
        print("预览前 3 条:")
        for i, item in enumerate(data[:3]):
            print(f"  [{i+1}] Q: {item['instruction'][:60]}...")
            print(f"       A: {item['output'][:60]}...")
            print()
        confirm = input("确认导入？(Y/n): ").strip().lower() or "y"
        if confirm == "y":
            save_data(data)
        else:
            print("已取消")
    else:
        print("[WARN] 没有解析到有效的问答对")
        print("  支持的格式示例:")
        print('  [{"instruction": "问题", "output": "回答"}]')
        print('  [{"query": "问题", "answer": "回答"}]')
        print('  CSV: query,answer')

if __name__ == "__main__":
    main()
