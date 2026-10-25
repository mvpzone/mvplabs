import asyncio

import probe
from server import ServerThread


def test_healthz_stays_up_during_a_scan():
    """Run a scan and the liveness probe at the same time. A platform kills after 3 misses in a row."""

    async def scenario(port: int):
        done = asyncio.Event()
        watcher = asyncio.ensure_future(probe.liveness(port, until=done))
        await asyncio.sleep(0.2)                       # let the probe establish a baseline
        body = await probe.get(port, "/scan", timeout=10)
        done.set()
        return body, *(await watcher)

    with ServerThread() as srv:
        body, verdict, seconds = asyncio.run(scenario(srv.port))
    print(f"scan={body!r} liveness={verdict} after {seconds:.1f}s")
    assert verdict == "alive", f"instance killed {seconds:.1f}s in: /healthz missed 3 probes in a row"
