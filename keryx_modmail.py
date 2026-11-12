"""Helpers for locating persistent modmail tickets by Discord user ID."""

from collections.abc import Iterable


MODMAIL_TOPIC_PREFIX = "User ID:"


def modmail_topic(user_id: int) -> str:
    """Return the canonical topic used to associate a ticket with a user."""
    return f"{MODMAIL_TOPIC_PREFIX} {user_id}"


def topic_user_id(topic: str | None) -> int | None:
    """Extract a user ID from a Keryx modmail topic, if it has one."""
    if not topic or not topic.startswith(MODMAIL_TOPIC_PREFIX):
        return None

    try:
        return int(topic.removeprefix(MODMAIL_TOPIC_PREFIX).strip())
    except ValueError:
        return None


def find_modmail_channel(channels: Iterable, user_id: int):
    """Find the oldest existing modmail ticket for a user.

    The topic holds the durable association. A channel name can change and is not
    unique, so it must never be used to decide whether a ticket already exists.
    """
    matches = [
        channel
        for channel in channels
        if topic_user_id(getattr(channel, "topic", None)) == user_id
    ]
    if not matches:
        return None

    return min(matches, key=lambda channel: getattr(channel, "created_at", 0))
