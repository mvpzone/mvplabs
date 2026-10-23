import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Backend(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/hello":
            # The control: answers without reading the request body.
            self.reply(200, b"hello from the backend\n", "text/plain")
            return
        body = self.read_body()
        self.received = len(body)
        if self.path == "/echo":
            self.reply(200, body, "application/octet-stream")
            return
        # /rpc: a JSON-RPC endpoint. Errors travel inside a 200, as JSON-RPC does.
        try:
            req = json.loads(body)
            out = {"jsonrpc": "2.0", "id": req.get("id"), "result": {"echo": req.get("params")}}
        except ValueError as e:
            out = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}}
        self.reply(200, json.dumps(out).encode() + b"\n", "application/json")

    def read_body(self) -> bytes:
        # In FULL_DUPLEX_STREAMED mode Envoy cannot know the final length (the processor may change it), so it drops
        # content-length and forwards the body chunked.
        if self.headers.get("transfer-encoding", "").lower() != "chunked":
            return self.rfile.read(int(self.headers.get("content-length") or 0))
        body = b""
        while size := int(self.rfile.readline().split(b";")[0], 16):
            body += self.rfile.read(size)
            self.rfile.readline()          # the CRLF after each chunk
        while self.rfile.readline() not in (b"\r\n", b""):
            pass                           # trailers, then the final CRLF
        return body

    def reply(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"backend: {self.command} {self.path} {args[1]} received={getattr(self, 'received', '-')}", flush=True)


if __name__ == "__main__":
    print("backend listening on :8081", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8081), Backend).serve_forever()
