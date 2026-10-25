import asyncio
import sys

SCAN = "import time; time.sleep(1.5); print('scan done')"  # stands in for a slow external scanner


async def scan() -> str:
    # Same child process, but the loop awaits it instead of waiting on it.
    proc = await asyncio.create_subprocess_exec(sys.executable, "-c", SCAN, stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    return out.decode().strip()
