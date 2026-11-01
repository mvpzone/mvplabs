from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Backend(BaseHTTPRequestHandler):
    """Answers anything. It is not the subject here; the decision in front of it is."""

    def handle_any(self, send_body: bool = True):
        length = int(self.headers.get("content-length") or 0)
        if length:
            self.rfile.read(length)
        body = f"backend: {self.command} {self.path}\n".encode()
        self.send_response(200)
        self.send_header("content-type", "text/plain")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def do_GET(self):
        self.handle_any()

    def do_POST(self):
        self.handle_any()

    def do_DELETE(self):
        self.handle_any()

    def do_HEAD(self):
        self.handle_any(send_body=False)

    def log_message(self, fmt, *args):
        print(f"backend: {self.command} {self.path} {args[1]}", flush=True)


if __name__ == "__main__":
    print("backend listening on :8081", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8081), Backend).serve_forever()
