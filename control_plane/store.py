"""SQLite-backed users and short-lived sessions."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Iterator

from .security import hash_password, token_digest, verify_password


ROLES = {"viewer", "operator", "admin"}


class StoreError(RuntimeError):
    pass


class Store:
    def __init__(self, database: Path):
        self.database = database

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.database.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('viewer', 'operator', 'admin')),
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    username TEXT NOT NULL REFERENCES users(username),
                    expires_at TEXT NOT NULL
                );
            """)

    def has_users(self) -> bool:
        with self._connect() as connection:
            return connection.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None

    def create_user(self, username: str, password: str, role: str) -> None:
        username = username.strip().lower()
        if not username or len(username) > 64 or not username.replace("_", "").replace("-", "").isalnum():
            raise StoreError("Username must contain only letters, numbers, hyphens, or underscores")
        if role not in ROLES:
            raise StoreError(f"Role must be one of {', '.join(sorted(ROLES))}")
        try:
            with self._connect() as connection:
                connection.execute("INSERT INTO users(username, password_hash, role, active, created_at) VALUES (?, ?, ?, 1, ?)", (username, hash_password(password), role, self._now()))
        except sqlite3.IntegrityError as error:
            raise StoreError("Username already exists") from error

    def list_users(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT username, role, active, created_at FROM users ORDER BY username").fetchall()
        return [dict(row) for row in rows]

    def set_user(self, username: str, role: str | None = None, active: bool | None = None) -> None:
        updates, values = [], []
        if role is not None:
            if role not in ROLES:
                raise StoreError("Invalid role")
            updates.append("role = ?")
            values.append(role)
        if active is not None:
            updates.append("active = ?")
            values.append(int(active))
        if not updates:
            raise StoreError("No user update supplied")
        normalized_username = username.strip().lower()
        with self._connect() as connection:
            existing = connection.execute("SELECT role, active FROM users WHERE username = ?", (normalized_username,)).fetchone()
            if not existing:
                raise StoreError("User not found")
            removes_admin = existing["role"] == "admin" and existing["active"] and ((role is not None and role != "admin") or active is False)
            if removes_admin:
                active_admins = connection.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND active = 1").fetchone()[0]
                if active_admins <= 1:
                    raise StoreError("Cannot disable or demote the last active administrator")
            values.append(normalized_username)
            connection.execute(f"UPDATE users SET {', '.join(updates)} WHERE username = ?", values)

    def authenticate(self, username: str, password: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT username, password_hash, role, active FROM users WHERE username = ?", (username.strip().lower(),)).fetchone()
        if not row or not row["active"] or not verify_password(password, row["password_hash"]):
            return None
        return {"username": row["username"], "role": row["role"]}

    def create_session(self, token: str, username: str, hours: int) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (self._now(),))
            connection.execute("INSERT INTO sessions(token_hash, username, expires_at) VALUES (?, ?, ?)", (token_digest(token), username, expires_at.isoformat()))
        return expires_at.isoformat()

    def session_user(self, token: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute("""
                SELECT users.username, users.role FROM sessions
                JOIN users ON users.username = sessions.username
                WHERE sessions.token_hash = ? AND sessions.expires_at > ? AND users.active = 1
            """, (token_digest(token), self._now())).fetchone()
        return dict(row) if row else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
