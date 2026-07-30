"""Background, administrator-only runner for bounded local agent workflows."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import threading
import uuid
from typing import Callable

from agent_workflows.engine import AgentEngine, AgentError, AgentModel
from agent_workflows.ollama_client import OllamaAgentModel
from agent_workflows.tools import ToolError
from agent_workflows.workflows import WORKFLOWS, get_workflow


MAX_JOBS = 20


@dataclass
class AgentJob:
    id: str
    task: str
    workflow: str
    model: str
    max_steps: int
    workspace: str
    status: str = "queued"
    answer: str | None = None
    steps: int | None = None
    trace: list[dict[str, object]] | None = None
    error: str | None = None

    def public(self) -> dict[str, object]:
        return asdict(self)


class AgentManager:
    """Run one bounded workflow at a time to avoid competing for local inference."""

    def __init__(
        self,
        workspace: Path,
        *,
        model_factory: Callable[[str], AgentModel] = OllamaAgentModel,
        allowed_models: tuple[str, ...] | None = None,
    ):
        self.workspace = workspace.resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError(f"Agent workspace is not a directory: {workspace}")
        configured_models = allowed_models or tuple(
            value.strip() for value in os.getenv("CONTROL_PLANE_AGENT_MODELS", "qwen3:8b,qwen2.5-coder:7b").split(",") if value.strip()
        )
        if not configured_models:
            raise ValueError("At least one agent model must be allowed")
        self.allowed_models = configured_models
        self.model_factory = model_factory
        self._jobs: dict[str, AgentJob] = {}
        self._lock = threading.Lock()
        self._run_lock = threading.Lock()

    def config(self) -> dict[str, object]:
        return {"workspace": self.workspace.name, "models": list(self.allowed_models), "workflows": sorted(WORKFLOWS)}

    def start(self, task: str, workflow: str, model: str, max_steps: int) -> dict[str, object]:
        task = str(task).strip()
        if not 1 <= len(task) <= 4_000:
            raise ValueError("task must contain 1-4000 characters")
        if model not in self.allowed_models:
            raise ValueError("model is not in the allowed agent model list")
        if workflow not in WORKFLOWS:
            raise ValueError("unknown workflow")
        if not 1 <= max_steps <= 20:
            raise ValueError("max_steps must be between 1 and 20")
        job = AgentJob(uuid.uuid4().hex, task, workflow, model, max_steps, self.workspace.name)
        with self._lock:
            self._jobs[job.id] = job
            while len(self._jobs) > MAX_JOBS:
                self._jobs.pop(next(iter(self._jobs)))
        threading.Thread(target=self._run, args=(job.id,), daemon=True, name=f"agent-{job.id[:8]}").start()
        return job.public()

    def get(self, job_id: str) -> dict[str, object] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.public() if job else None

    def jobs(self) -> list[dict[str, object]]:
        with self._lock:
            return [job.public() for job in reversed(self._jobs.values())]

    def _run(self, job_id: str) -> None:
        with self._run_lock:
            with self._lock:
                job = self._jobs.get(job_id)
                if not job:
                    return
                job.status = "running"
            try:
                result = AgentEngine(
                    self.model_factory(job.model),
                    self.workspace,
                    get_workflow(job.workflow),
                    max_steps=job.max_steps,
                ).run(job.task)
                with self._lock:
                    job.status = "completed"
                    job.answer = result.answer
                    job.steps = result.steps
                    job.trace = [asdict(event) for event in result.trace]
            except (AgentError, ToolError, ValueError, OSError) as error:
                with self._lock:
                    job.status = "failed"
                    job.error = str(error)
