import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class UsageDecision:
    allowed: bool
    remaining: int
    retry_after: int = 0
    reason: str = ""


class DailyUsageLimiter:
    """Persistent per-user daily quotas with in-memory cooldowns."""

    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self._last_request: dict[int, float] = {}
        self._initialize_database()

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def _initialize_database(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_usage (
                    usage_date TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    requests INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (usage_date, user_id)
                )
                """
            )

    def acquire(
        self,
        user_id: int,
        daily_limit: int,
        cooldown_seconds: int,
        *,
        now: float | None = None,
        usage_date: str | None = None,
    ) -> UsageDecision:
        now = time.monotonic() if now is None else now
        usage_date = usage_date or datetime.now(timezone.utc).date().isoformat()
        last_request = self._last_request.get(user_id)

        if last_request is not None:
            elapsed = now - last_request
            if elapsed < cooldown_seconds:
                retry_after = max(1, int(cooldown_seconds - elapsed + 0.999))
                return UsageDecision(False, 0, retry_after, "cooldown")

        with self._connect() as connection:
            row = connection.execute(
                "SELECT requests FROM ai_usage WHERE usage_date = ? AND user_id = ?",
                (usage_date, user_id),
            ).fetchone()
            used = row[0] if row else 0

            if used >= daily_limit:
                return UsageDecision(False, 0, reason="daily_limit")

            connection.execute(
                """
                INSERT INTO ai_usage (usage_date, user_id, requests)
                VALUES (?, ?, 1)
                ON CONFLICT (usage_date, user_id)
                DO UPDATE SET requests = requests + 1
                """,
                (usage_date, user_id),
            )

        self._last_request[user_id] = now
        return UsageDecision(True, daily_limit - used - 1)

    def refund(self, user_id: int, *, usage_date: str | None = None):
        """Refund a failed Gemini request while retaining its anti-spam cooldown."""
        usage_date = usage_date or datetime.now(timezone.utc).date().isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE ai_usage
                SET requests = MAX(requests - 1, 0)
                WHERE usage_date = ? AND user_id = ?
                """,
                (usage_date, user_id),
            )


def split_discord_message(text: str, limit: int = 1900) -> list[str]:
    """Split text into Discord-safe chunks, preferring paragraph boundaries."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit + 1)
        if split_at < limit // 2:
            split_at = text.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit

        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)
    return chunks
