# blocked-event-loop

The code for the codelab
[Blocking the Loop Is a Liveness Bug](https://devnull.fyi/labs/blocking-the-loop-is-a-liveness-bug/).

A small asyncio server has a `/healthz` route and a `/scan` route that runs a slow child process. In `broken/` the scan
handler calls `subprocess.run` inside `async def`: the whole event loop waits, `/healthz` goes unanswered, and a
liveness probe would kill the instance. A one-request test stays green. In `fixed/` the loop awaits the child instead.

```
server.py                 asyncio HTTP server (GET /healthz, GET /scan); ServerThread runs it on its own loop
probe.py                  the platform's liveness check: GET /healthz every 0.1 s, 3 misses in a row = killed
loopmon.py                loop-lag monitor: prints "[loop-lag] event loop blocked for N s"
broken/handlers.py        scan() blocks the loop with subprocess.run
fixed/handlers.py         scan() awaits asyncio.create_subprocess_exec
test_single_request.py    one request, one answer (passes in both)
test_liveness.py          scan and probe at the same time (fails in broken)
test_loopmon.py           the monitor must stay quiet (fails in broken, naming the block)
conftest.py               picks broken/ or fixed/ from the CODELAB environment variable
```

## Run it

Python 3.12 or later (tested on 3.13). No Docker, no network, nothing outside `127.0.0.1`.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

CODELAB=broken python -m pytest -q test_single_request.py   # 1 passed  - green while the loop is blocked
CODELAB=broken python -m pytest -q test_liveness.py         # 1 failed  - instance killed about 1.3s in
CODELAB=broken python -m pytest -q test_loopmon.py          # 1 failed  - [loop-lag] about 1.5s blocked
CODELAB=fixed  python -m pytest -q                          # 3 passed
```

*A request that returns proves the work finished. It does not prove the loop was free while it ran.*
