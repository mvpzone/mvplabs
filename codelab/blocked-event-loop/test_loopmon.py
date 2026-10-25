import asyncio

import probe
from server import ServerThread


def test_a_block_names_itself():
    """The monitor turns a mystery liveness failure into a line that says the loop was blocked, and for how long."""
    with ServerThread() as srv:
        asyncio.run(probe.get(srv.port, "/scan", timeout=10))
        lags = list(srv.lags)
    assert lags == [], f"[loop-lag] the loop was blocked: {[round(x, 2) for x in lags]}"
