# Kata: decision router

A router asks a decision model which route fits a request, and acts on the answer. The model always picks
something, so a request that fits no route still gets one. Add a confidence threshold, watch the stray
request fall back to the normal path, and keep the confident ones routed.

**Walkthrough:** [A Router That Always Answers Will Misroute](https://devnull.fyi/labs/a-router-that-always-answers-will-misroute/) (15 min)

## Files

| File | What it is |
|---|---|
| `decisions.py` | A stand-in for a decision-model API: one probability per route, no generated text |
| `broken/router.py` | Takes the highest-scoring route, however weak |
| `fixed/router.py` | Acts only at or above `THRESHOLD`; below it, falls back to the normal path |
| `test_router.py` | One test: a confident request is routed, an off-topic one is not |
| `conftest.py` | Picks `broken/` or `fixed/` from the `KATA` environment variable |

## Run it

Python 3.12 or later (tested on 3.13).

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

KATA=broken python -m pytest -q test_router.py   # 1 failed — AssertionError: routed a poem to 'catalogue' at confidence 0.54
KATA=fixed  python -m pytest -q test_router.py   # 1 passed
```

*A model that must choose will always choose. Decide what happens when it should not.*

## Going further

The same router, run against a real decision endpoint, taught three more things. None are needed for the kata:

- Question IDs are validated by the API: 1 to 64 characters of `[A-Za-z0-9_-]`. An ID with a colon in it came back as HTTP 400.
- Questions in one call are scored independently, so a parameter question cannot depend on the chosen route. Drop the parameters of unchosen routes in code.
- Treat any API failure like a low-confidence answer: fall back, do not raise.
