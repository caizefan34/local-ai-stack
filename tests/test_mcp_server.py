import json
import unittest
from unittest import mock

from mcp_server import core


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size=-1):
        return json.dumps(self.payload).encode()


class MCPServerCoreTests(unittest.TestCase):
    @mock.patch("urllib.request.urlopen")
    def test_generate_uses_non_streaming_ollama_request(self, urlopen):
        urlopen.return_value = FakeResponse({"response": "four"})
        self.assertEqual(core.generate("2+2", max_tokens=16), "four")
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"]["num_predict"], 16)

    @mock.patch("urllib.request.urlopen")
    def test_list_models_returns_public_model_fields(self, urlopen):
        urlopen.return_value = FakeResponse({"models": [{"name": "qwen3:8b", "size": 42, "modified_at": "today", "digest": "secret-ish"}]})
        self.assertEqual(core.list_models(), [{"name": "qwen3:8b", "size": 42, "modified_at": "today"}])

    def test_generate_and_rerank_enforce_limits(self):
        with self.assertRaises(ValueError):
            core.generate("")
        with self.assertRaises(ValueError):
            core.rerank("query", [])
        with self.assertRaises(ValueError):
            core.rerank("query", ["one"], top_k=2)

    @mock.patch("urllib.request.urlopen")
    def test_reranker_request_preserves_top_k(self, urlopen):
        urlopen.return_value = FakeResponse({"results": [{"index": 1, "score": 0.9, "text": "b"}]})
        result = core.rerank("q", ["a", "b"], top_k=1)
        self.assertEqual(result[0]["index"], 1)
        self.assertEqual(json.loads(urlopen.call_args.args[0].data)["top_k"], 1)


if __name__ == "__main__":
    unittest.main()
