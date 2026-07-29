import json
import sys
import time
import urllib.request


model = sys.argv[1] if len(sys.argv) > 1 else "qwen3-8b-stable"
cases = [
    ("只输出答案：一个项目有120个任务，已完成75%，还剩多少个任务？", "30个任务"),
    ('只输出 JSON：把“姓名：李明，年龄：20”转换为 {"name":"...","age":0}', "李明"),
    ("用一句话说明 Python 列表和元组的区别。", "可变"),
]

for prompt, expected in cases:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "num_predict": 128, "num_ctx": 4096},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request) as response:
        result = json.load(response)
    elapsed = time.perf_counter() - started
    answer = result["response"].strip()
    eval_seconds = result.get("eval_duration", 0) / 1e9
    speed = result.get("eval_count", 0) / eval_seconds if eval_seconds else 0
    passed = expected in answer
    print(json.dumps({"passed": passed, "expected": expected, "response": answer, "seconds": round(elapsed, 2), "tokens_per_second": round(speed, 2)}, ensure_ascii=False))
