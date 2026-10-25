import subprocess
import sys

SCAN = "import time; time.sleep(1.5); print('scan done')"  # stands in for a slow external scanner


async def scan() -> str:
    # `async def`, but the body never awaits: subprocess.run holds the whole event loop for 1.5 s.
    out = subprocess.run([sys.executable, "-c", SCAN], capture_output=True, text=True)
    return out.stdout.strip()
