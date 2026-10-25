import asyncio

import probe
from server import ServerThread


def test_scan_returns_its_result():
    """The check most suites have: one request, one answer. It cannot see a starved loop."""
    with ServerThread() as srv:
        body = asyncio.run(probe.get(srv.port, "/scan", timeout=10))
    assert body == "scan done"
