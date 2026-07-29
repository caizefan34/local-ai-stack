"""Run a local code-generation benchmark and fail on a configured regression."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.request


def generate(url: str, model: str, prompt: str) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0, "num_predict": 512}}).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response).get("response", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a local Ollama code model against JSON prompts")
    parser.add_argument("benchmark", type=Path, help="JSON list: prompt and expected_substring fields")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/generate")
    parser.add_argument("--baseline", type=Path, help="Prior JSON result to compare")
    parser.add_argument("--max-regression", type=float, default=0.03)
    parser.add_argument("--output", type=Path, default=Path("codegen-eval.json"))
    args = parser.parse_args()
    cases = json.loads(args.benchmark.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        answer = generate(args.url, args.model, case["prompt"])
        results.append({"id": case.get("id", ""), "passed": case["expected_substring"] in answer, "response": answer})
    score = sum(item["passed"] for item in results) / len(results) if results else 0
    report = {"model": args.model, "score": score, "results": results}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.baseline:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        if baseline["score"] - score > args.max_regression:
            raise SystemExit(f"Regression: {baseline['score']:.3f} -> {score:.3f}")
    print(f"Code benchmark score: {score:.3f} ({sum(item['passed'] for item in results)}/{len(results)})")


if __name__ == "__main__":
    main()
