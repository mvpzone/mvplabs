# Kata: strict mocks

A unit test passes against a method the SDK does not have. Make the mock as strict as the real class, watch the test
fail for the right reason, fix the call, and find out what the old test was really checking.

**Walkthrough:** [Your Mock Answers Methods the SDK Doesn't Have](https://devnull.fyi/labs/your-mock-answers-methods-the-sdk-doesnt-have/) (15 min)

## Files

| File | What it is |
|---|---|
| `shopsdk.py` | A stand-in for a vendor SDK: the real surface your code depends on |
| `broken/checkout.py` | Calls `submit_order`, which `ShopClient` does not have |
| `fixed/checkout.py` | Calls `create_order`, the method the SDK actually has |
| `test_loose.py` | The usual test: a `MagicMock` that answers anything |
| `test_strict.py` | The same test on `create_autospec(ShopClient, instance=True)` |
| `conftest.py` | Picks `broken/` or `fixed/` from the `KATA` environment variable |

## Run it

Python 3.12 or later (tested on 3.12, 3.13 and 3.14).

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

KATA=broken python -m pytest -q test_loose.py                 # 1 passed   — green against a method that does not exist
KATA=broken python -m pytest -q test_strict.py                # 1 failed   — AttributeError: ... 'submit_order'
KATA=fixed  python -m pytest -q test_strict.py test_loose.py  # 1 failed, 1 passed — the loose test was written to match the bug
```

*A mock that answers anything proves only that your code asked.*
