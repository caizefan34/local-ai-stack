"""
将 FastGPT 导出的对话日志转换为 LoRA 训练数据格式。

用法:
  python scripts/prepare_data.py --input chat_logs.json --output data/train.json

输入格式（FastGPT 对话日志）:
  [{"query": "用户问题", "answer": "模型回答"}, ...]

输出格式: Alpaca JSON
"""
import json, os, sys, argparse

def parse_args():
    parser = argparse.ArgumentParser(description="将对话数据转换为训练格式")
    parser.add_argument("--input", "-i", required=True, help="输入的对话日志 JSON")
    parser.add_argument("--output", "-o", default="data/train.json", help="输出的训练数据 JSON")
    parser.add_argument("--min-length", type=int, default=5, help="最短问答长度")
    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"[ERR] 输入文件不存在: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    train_data = []
    skipped = 0
    for item in raw:
        query = (item.get("query") or item.get("instruction") or "").strip()
        answer = (item.get("answer") or item.get("output") or "").strip()
        if len(query) < args.min_length or len(answer) < args.min_length:
            skipped += 1
            continue
        train_data.append({
            "id": f"qa-{len(train_data)+1:04d}",
            "instruction": query,
            "output": answer,
        })

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] 转换完成")
    print(f"    输入: {len(raw)} 条")
    print(f"    输出: {len(train_data)} 条")
    print(f"    跳过: {skipped} 条（过短）")
    print(f"    文件: {args.output}")

if __name__ == "__main__":
    main()
