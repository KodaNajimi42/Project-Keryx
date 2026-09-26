import tempfile
import unittest
from pathlib import Path

from keryx_ai import DailyUsageLimiter, split_discord_message


class DailyUsageLimiterTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database = Path(self.temp_directory.name) / "usage.db"
        self.limiter = DailyUsageLimiter(str(database))

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_enforces_cooldown(self):
        first = self.limiter.acquire(42, 5, 60, now=100, usage_date="2026-09-26")
        second = self.limiter.acquire(42, 5, 60, now=101, usage_date="2026-09-26")

        self.assertTrue(first.allowed)
        self.assertFalse(second.allowed)
        self.assertEqual(second.reason, "cooldown")
        self.assertEqual(second.retry_after, 59)

    def test_persists_and_enforces_daily_limit(self):
        self.assertTrue(
            self.limiter.acquire(42, 2, 0, now=100, usage_date="2026-09-26").allowed
        )
        self.assertTrue(
            self.limiter.acquire(42, 2, 0, now=101, usage_date="2026-09-26").allowed
        )

        restarted = DailyUsageLimiter(str(self.limiter.database_path))
        denied = restarted.acquire(42, 2, 0, now=102, usage_date="2026-09-26")
        self.assertFalse(denied.allowed)
        self.assertEqual(denied.reason, "daily_limit")

    def test_refunds_failed_request(self):
        self.limiter.acquire(42, 1, 0, now=100, usage_date="2026-09-26")
        self.limiter.refund(42, usage_date="2026-09-26")
        retry = self.limiter.acquire(42, 1, 0, now=101, usage_date="2026-09-26")
        self.assertTrue(retry.allowed)


class DiscordMessageTests(unittest.TestCase):
    def test_splits_long_messages(self):
        chunks = split_discord_message("word " * 1000, limit=100)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))

    def test_empty_message_returns_no_chunks(self):
        self.assertEqual(split_discord_message("   "), [])


if __name__ == "__main__":
    unittest.main()
