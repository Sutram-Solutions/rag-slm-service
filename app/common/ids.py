"""Request and entity identifier helpers."""

from uuid import UUID, uuid4


def new_id() -> UUID:
    return uuid4()
