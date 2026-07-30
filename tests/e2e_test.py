"""Opt-in live checks for a running Local AI Stack."""
import json
import os
import unittest
import urllib.request


def request_json(url, payload=None, timeout=30):
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json; charset=utf-8"} if body else {}
    request = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


class LocalStackE2ETests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("RUN_LOCAL_E2E") == "1", "set RUN_LOCAL_E2E=1 to run live local services")
    def test_services(self):
        for model, prompt in (
            ("qwen3-1.7b-stable", "What is 2+2? Output only the number."),
            ("qwen3-8b-stable", "Python list comprehension syntax? Output just one line."),
        ):
            result = request_json(
                "http://localhost:11434/api/generate",
                {"model": model, "prompt": prompt, "stream": False, "think": False, "options": {"temperature": 0, "num_predict": 32}},
            )
            self.assertTrue(result.get("response", "").strip())

        rerank = request_json(
            "http://localhost:18888/rerank_fastgpt",
            {"query": "machine learning", "passages": ["supervised learning requires labeled data", "the weather is nice today", "deep learning is a subset of machine learning"]},
        )
        self.assertEqual(len(rerank.get("results", [])), 3)
        with urllib.request.urlopen("http://localhost:3000/", timeout=5) as response:
            self.assertLess(response.status, 500)


if __name__ == "__main__":
    unittest.main()
