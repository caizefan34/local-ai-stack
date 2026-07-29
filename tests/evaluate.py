#!/usr/bin/env python3
"""Evaluate Ollama model accuracy on standard test cases."""
import json, sys, time, urllib.request

def test_model(model, cases):
    results = []
    for prompt, expected in cases:
        payload = json.dumps({
            "model": model, "prompt": prompt,
            "stream": False, "think": False,
            "options": {"temperature": 0, "num_predict": 128, "num_ctx": 4096}
        }, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request("http://localhost:11434/api/generate",
            data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
        elapsed = time.perf_counter() - t0
        answer = result["response"].strip()
        eval_s = result.get("eval_duration", 0) / 1e9
        speed = result.get("eval_count", 0) / eval_s if eval_s else 0
        passed = expected.lower() in answer.lower()
        results.append({"passed": passed, "expected": expected,
            "response": answer[:80], "seconds": round(elapsed, 2),
            "tokens_per_second": round(speed, 2)})
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {expected[:30]:30s} -> {answer[:50]:50s}  ({speed:.1f} tok/s)")
    return results

def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen3-8b-stable"
    cases = [
        ("Output only the number: 120 tasks, 75% complete. How many remaining?", "30"),
        ("Output only JSON: convert \"Name: Alice, Age: 25\" to {\"name\":...,\"age\":...}", "Alice"),
        ("Explain Python list vs tuple in one sentence. Include the word 'mutable'.", "mutable"),
    ]
    print(f"Evaluating: {model}")
    results = test_model(model, cases)
    passed = sum(1 for r in results if r["passed"])
    print(f"\nResults: {passed}/{len(results)} passed")

if __name__ == "__main__":
    main()
