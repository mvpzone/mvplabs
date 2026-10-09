"""Pick which checkout.py the tests import: KATA=broken (default) or KATA=fixed."""
import os
import sys
from pathlib import Path

variant = os.environ.get("KATA", "broken")
if variant not in ("broken", "fixed"):
    raise SystemExit(f"KATA must be 'broken' or 'fixed', not {variant!r}")
sys.path.insert(0, str(Path(__file__).parent / variant))
