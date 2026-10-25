"""A tiny asyncio HTTP server: /healthz is the liveness probe, /scan does slow work via handlers.scan()."""
import asyncio
import threading

import handlers


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    request_line = (await reader.readline()).decode()
    while (await reader.readline()) not in (b"\r\n", b""):
        pass  # skip the headers
    path = request_line.split(" ")[1] if " " in request_line else "/"
    if path == "/healthz":
        body = "ok"
    elif path == "/scan":
        body = await handlers.scan()
    else:
        body = "not found"
    writer.write(f"HTTP/1.1 200 OK\r\ncontent-length: {len(body)}\r\nconnection: close\r\n\r\n{body}".encode())
    await writer.drain()
    writer.close()


class ServerThread:
    """Runs the server on its OWN event loop in a thread, so a test can watch it from outside."""

    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.port = 0
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start())
        self._ready.set()
        self.loop.run_forever()

    async def _start(self) -> None:
        import loopmon

        self.lags = loopmon.LAGS = []
        self.monitor = asyncio.ensure_future(loopmon.monitor(interval=0.05, threshold=0.25))
        server = await asyncio.start_server(handle, "127.0.0.1", 0)
        self.port = server.sockets[0].getsockname()[1]

    async def _stop(self) -> None:
        others = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in others:
            task.cancel()
        await asyncio.gather(*others, return_exceptions=True)

    def __enter__(self) -> "ServerThread":
        self._thread.start()
        self._ready.wait(5)
        return self

    def __exit__(self, *exc) -> None:
        asyncio.run_coroutine_threadsafe(self._stop(), self.loop).result(5)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join(5)
