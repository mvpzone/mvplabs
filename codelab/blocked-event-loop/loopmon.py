"""Loop-lag monitor: sleep a short interval; whatever the loop took beyond it was spent blocked."""
import asyncio
import time

LAGS: list[float] = []


async def monitor(interval: float = 0.05, threshold: float = 0.25) -> None:
    while True:
        start = time.perf_counter()
        await asyncio.sleep(interval)
        lag = time.perf_counter() - start - interval
        if lag > threshold:
            LAGS.append(lag)
            print(f"[loop-lag] event loop blocked for {lag:.2f}s", flush=True)
