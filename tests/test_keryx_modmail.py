import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from keryx_modmail import find_modmail_channel, modmail_topic, topic_user_id


class ModmailLookupTests(unittest.TestCase):
    def test_builds_and_reads_canonical_topic(self):
        topic = modmail_topic(123456789)
        self.assertEqual(topic, "User ID: 123456789")
        self.assertEqual(topic_user_id(topic), 123456789)

    def test_ignores_missing_or_invalid_topics(self):
        self.assertIsNone(topic_user_id(None))
        self.assertIsNone(topic_user_id("mail for User ID: 123"))
        self.assertIsNone(topic_user_id("User ID: not-a-number"))

    def test_finds_ticket_by_user_id_not_channel_name(self):
        oldest = SimpleNamespace(
            name="mail-meyers222",
            topic="User ID: 42",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        duplicate = SimpleNamespace(
            name="mail-meyers222",
            topic="User ID: 42",
            created_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        another_user = SimpleNamespace(
            name="mail-meyers222",
            topic="User ID: 99",
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )

        self.assertIs(find_modmail_channel([duplicate, another_user, oldest], 42), oldest)


if __name__ == "__main__":
    unittest.main()
