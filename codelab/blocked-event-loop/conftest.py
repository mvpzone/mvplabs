"""Pick which handlers.py the tests import: CODELAB=broken (default) or CODELAB=fixed."""
import os
import sys
from pathlib import Path

variant = os.environ.get("CODELAB", "broken")
if variant not in ("broken", "fixed"):
    raise SystemExit(f"CODELAB must be 'broken' or 'fixed', not {variant!r}")
here = Path(__file__).parent
sys.path.insert(0, str(here / variant))
sys.path.insert(0, str(here))
