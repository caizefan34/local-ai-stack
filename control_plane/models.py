"""Allowlisted asynchronous Ollama model downloads for the control plane."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import subprocess
import threading
import uuid
from typing import Callable

from mcp_server import core as ollama


@dataclass(frozen=True)
class ModelSpec:
    id: str
    model: str
    title: str
    description: str


CATALOG = {
    "qwen3-fast": ModelSpec("qwen3-fast", "qwen3:0.6b", "Qwen3 0.6B", "Fast, lightweight general assistant"),
    "qwen3-main": ModelSpec("qwen3-main", "qwen3:8b", "Qwen3 8B", "Main local general-purpose model"),
    "coder-completion": ModelSpec("coder-completion", "qwen2.5-coder:1.5b", "Qwen2.5-Coder 1.5B", "Low-latency inline completion"),
    "coder-generation": ModelSpec("coder-generation", "qwen2.5-coder:7b", "Qwen2.5-Coder 7B", "Code generation, review, and fixes"),
    "embeddings": ModelSpec("embeddings", "nomic-embed-text:latest", "Nomic Embed Text", "Embeddings for knowledge-base retrieval"),
}


class ModelError(RuntimeError):
    pass


class ModelManager:
    def __init__(self, popen: Callable = subprocess.Popen):
        self._popen = popen
        self._lock = threading.Lock()
        self._jobs: dict[str, dict[str, object]] = {}

    def catalog(self) -> list[dict[str, str]]:
        return [asdict(spec) for spec in CATALOG.values()]

    def installed(self) -> dict[str, object]:
        try:
            return {"models": ollama.list_models(), "error": None}
        except Exception as error:
            return {"models": [], "error": str(error)}

    def start_pull(self, model_id: str) -> dict[str, object]:
        spec = CATALOG.get(model_id)
        if not spec:
            raise ModelError("Unknown model catalog item")
        with self._lock:
            if any(job["model_id"] == model_id and job["status"] == "running" for job in self._jobs.values()):
                raise ModelError("This model is already downloading")
            job_id = uuid.uuid4().hex
            job = {"id": job_id, "model_id": spec.id, "model": spec.model, "status": "running", "output": "Starting download...", "started_at": self._now(), "finished_at": None}
            self._jobs[job_id] = job
        thread = threading.Thread(target=self._run_pull, args=(job_id, spec), daemon=True)
        thread.start()
        return dict(job)

    def jobs(self) -> list[dict[str, object]]:
        with self._lock:
            return [dict(job) for job in sorted(self._jobs.values(), key=lambda item: str(item["started_at"]), reverse=True)[:20]]

    def _run_pull(self, job_id: str, spec: ModelSpec) -> None:
        try:
            process = self._popen(["ollama", "pull", spec.model], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            output: list[str] = []
            if process.stdout:
                for line in process.stdout:
                    output.append(line.rstrip())
                    self._update(job_id, output="\n".join(output)[-4000:])
            return_code = process.wait()
            if return_code:
                self._update(job_id, status="failed", output=("\n".join(output)[-4000:] or f"ollama pull exited with {return_code}"), finished_at=self._now())
            else:
                self._update(job_id, status="completed", output=("\n".join(output)[-4000:] or "Model downloaded"), finished_at=self._now())
        except OSError as error:
            self._update(job_id, status="failed", output=str(error), finished_at=self._now())

    def _update(self, job_id: str, **values: object) -> None:
        with self._lock:
            self._jobs[job_id].update(values)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
