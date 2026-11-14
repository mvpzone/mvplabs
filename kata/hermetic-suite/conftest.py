"""Pytest plugin toggling between broken (unguarded) and fixed (hermetic) modes."""

import os
import pytest

_MODE = os.environ.get("KATA", "broken")

if _MODE == "fixed":
    from fixed import hermetic_net as _net
elif _MODE == "broken":
    from broken import hermetic_net as _net
else:
    raise RuntimeError(f"Unknown KATA mode: {_MODE!r} (expected 'broken' or 'fixed')")

# Install at import time so import-phase network calls attribute to <collection>.
_net.install()


def pytest_collection_finish(session: pytest.Session) -> None:
    leaked = _net.pop_non_test_violations()
    if leaked:
        summary = ", ".join(f"{owner} -> {host} ({op})" for owner, host, op in leaked)
        raise pytest.UsageError(f"hermetic test: network used during collection: {summary}")


def pytest_runtest_setup(item: pytest.Item) -> None:
    leaked = _net.pop_non_test_violations()
    if leaked:
        summary = ", ".join(f"{owner} -> {host} ({op})" for owner, host, op in leaked)
        pytest.fail(f"hermetic test: stray network outside active test: {summary}")
    _net.begin_owner(item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        violations = _net.pop_violations(item.nodeid)
        if violations:
            hosts = ", ".join(f"{host} ({op})" for host, op in violations)
            report.outcome = "failed"
            report.longrepr = (
                f"hermetic test failed: unexpected outbound network in {item.nodeid}: {hosts}"
            )


def pytest_runtest_teardown(item: pytest.Item) -> None:
    _net.end_owner(item.nodeid)
