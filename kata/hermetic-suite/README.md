# Make the Suite Hermetic

> If your software under test catches `OSError` and falls back to defaults, tests stay green while making real outbound lookups — slowly failing, reaching live backends, or passing only because a machine happens to have credentials and DNS.

## The lesson

Patching `socket.getaddrinfo` alone leaves literal-IP connects (including async event loops) open, and catching `OSError` inside production code hides blocked lookups unless the test harness records every non-local destination and fails the owning test cleanly. Loopback stays allowed; known off-cloud metadata probes fail fast without faulting the test.

Walkthrough: [devnull.fyi/labs/make-the-suite-hermetic/](https://devnull.fyi/labs/make-the-suite-hermetic/)

## Layout

```
netclient.py              config client + metadata probe that degrade on OSError
conftest.py               installs broken/ or fixed/ guard via KATA env var
broken/hermetic_net.py    no-op guard (default) — sockets reach out silently
fixed/hermetic_net.py     patches getaddrinfo + connect/connect_ex, keeps owner ledger
test_suite.py             degrading suite: green in broken mode, caught in fixed mode
test_guard.py             unit checks for loopback classification, literal IPs, ledger
```

## Run

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 1. Default (broken): test_suite passes even though DNS/socket I/O ran
pytest -q test_suite.py
# 3 passed in 0.07s

# 2. Guard active (fixed): silent fallback fails and names the offending host
KATA=fixed pytest -q test_suite.py
# FAILED test_suite.py::test_fetch_config_degrades - hermetic test failed: unexpected outbound network in test_suite.py::test_fetch_config_degrades: config.example.invalid (getaddrinfo)

# 3. Direct guard unit checks pass in fixed mode
KATA=fixed pytest -q test_guard.py
# 5 passed in 0.07s
```
