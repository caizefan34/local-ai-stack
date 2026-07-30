"""FastAPI control plane with role-based dashboard access."""
from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import urllib.error
import urllib.request

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .actions import ActionError, run_action
from .models import ModelError, ModelManager
from .security import new_token
from .store import Store, StoreError


ROOT = Path(__file__).resolve().parents[1]


class LoginRequest(BaseModel):
    username: str
    password: str


class SetupRequest(BaseModel):
    username: str = "admin"
    password: str = Field(min_length=12)


class UserCreateRequest(BaseModel):
    username: str
    password: str = Field(min_length=12)
    role: str


class UserUpdateRequest(BaseModel):
    role: str | None = None
    active: bool | None = None


def _probe(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status < 500
    except (urllib.error.URLError, TimeoutError):
        return False


def create_app(database: Path | None = None, root: Path = ROOT, model_manager: ModelManager | None = None) -> FastAPI:
    store = Store(database or Path(os.getenv("CONTROL_PLANE_DB", root / "data" / "control-plane.sqlite3")))
    manager = model_manager or ModelManager()
    session_hours = int(os.getenv("CONTROL_PLANE_SESSION_HOURS", "8"))

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        store.initialize()
        yield

    app = FastAPI(title="Local AI Stack Control Plane", lifespan=lifespan)

    def current_user(request: Request) -> dict[str, str]:
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
        user = store.session_user(authorization.removeprefix("Bearer ").strip())
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session is invalid or expired")
        return user

    def require(*roles: str):
        def dependency(request: Request) -> dict[str, str]:
            user = current_user(request)
            if user["role"] not in roles:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient role")
            return user
        return dependency

    @app.post("/api/auth/login")
    def login(payload: LoginRequest) -> dict[str, object]:
        user = store.authenticate(payload.username, payload.password)
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")
        token = new_token()
        expires_at = store.create_session(token, user["username"], session_hours)
        return {"token": token, "user": user, "expires_at": expires_at}

    @app.get("/api/setup/status")
    def setup_status() -> dict[str, bool]:
        return {"initialized": store.has_users()}

    @app.post("/api/setup/bootstrap", status_code=status.HTTP_201_CREATED)
    def bootstrap(payload: SetupRequest) -> dict[str, str]:
        if store.has_users():
            raise HTTPException(status.HTTP_409_CONFLICT, "Administrator setup is already complete")
        try:
            store.create_user(payload.username, payload.password, "admin")
        except (StoreError, ValueError) as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        return {"username": payload.username.strip().lower(), "role": "admin"}

    @app.get("/api/auth/me")
    def me(user: dict[str, str] = Depends(current_user)) -> dict[str, str]:
        return user

    @app.get("/api/users")
    def list_users(_user: dict[str, str] = Depends(require("admin"))) -> list[dict[str, object]]:
        return store.list_users()

    @app.post("/api/users", status_code=status.HTTP_201_CREATED)
    def create_user(payload: UserCreateRequest, _user: dict[str, str] = Depends(require("admin"))) -> dict[str, str]:
        try:
            store.create_user(payload.username, payload.password, payload.role)
        except (StoreError, ValueError) as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        return {"username": payload.username.strip().lower(), "role": payload.role}

    @app.patch("/api/users/{username}")
    def update_user(username: str, payload: UserUpdateRequest, _user: dict[str, str] = Depends(require("admin"))) -> dict[str, str]:
        try:
            store.set_user(username, payload.role, payload.active)
        except StoreError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        return {"status": "updated"}

    @app.get("/api/health")
    def health(_user: dict[str, str] = Depends(require("viewer", "operator", "admin"))) -> dict[str, bool]:
        return {"ollama": _probe("http://127.0.0.1:11434/api/tags"), "fastgpt": _probe("http://127.0.0.1:3000/"), "reranker": _probe("http://127.0.0.1:18888/health")}

    @app.post("/api/actions/{name}")
    def action(name: str, _user: dict[str, str] = Depends(require("operator", "admin"))) -> dict[str, str]:
        try:
            return {"output": run_action(name, root)}
        except ActionError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    @app.get("/api/models")
    def models(_user: dict[str, str] = Depends(require("viewer", "operator", "admin"))) -> dict[str, object]:
        return {"catalog": manager.catalog(), "installed": manager.installed(), "jobs": manager.jobs()}

    @app.post("/api/models/pull/{model_id}", status_code=status.HTTP_202_ACCEPTED)
    def pull_model(model_id: str, _user: dict[str, str] = Depends(require("operator", "admin"))) -> dict[str, object]:
        try:
            return manager.start_pull(model_id)
        except ModelError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    @app.get("/")
    def dashboard() -> FileResponse:
        return FileResponse(root / "desktop-app" / "dashboard.html")

    return app


app = create_app()
