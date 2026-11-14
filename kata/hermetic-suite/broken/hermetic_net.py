"""Broken hermetic guard: no-op placeholder, leaving sockets open."""


def install() -> None:
    """Do nothing; socket lookups and connects pass straight through."""


def begin_owner(owner: str) -> None:
    """Record nothing."""


def end_owner(owner: str) -> None:
    """Record nothing."""


def pop_violations(owner: str) -> list[tuple[str, str]]:
    """Never report violations."""
    return []


def pop_non_test_violations() -> list[tuple[str, str, str]]:
    """Never report collection or post-test violations."""
    return []
