"""What a platform's liveness check does: GET /healthz on a timer; N failures in a row = kill the instance."""
import asyncio
import time


async def get(port: int, path: str, timeout: float) -> str:
    async def _go() -> str:
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        writer.write(f"GET {path} HTTP/1.1\r\nhost: x\r\n\r\n".encode())
        await writer.drain()
        raw = await reader.read()
        writer.close()
        return raw.decode().split("\r\n\r\n", 1)[1]

    return await asyncio.wait_for(_go(), timeout)


async def liveness(port: int, period: float = 0.1, timeout: float = 0.3, failures: int = 3, until: asyncio.Event | None = None):
    """Return ('killed', seconds) after `failures` consecutive misses, else ('alive', seconds) once `until` is set."""
    start = time.perf_counter()
    misses = 0
    while until is None or not until.is_set():
        try:
            await get(port, "/healthz", timeout)
            misses = 0
        except (asyncio.TimeoutError, OSError):
            misses += 1
            if misses >= failures:
                return "killed", time.perf_counter() - start
        await asyncio.sleep(period)
    return "alive", time.perf_counter() - start
