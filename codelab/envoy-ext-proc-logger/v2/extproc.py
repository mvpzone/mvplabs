import json
import os
import time
from concurrent import futures

import grpc
from envoy.service.ext_proc.v3 import external_processor_pb2 as pb
from envoy.service.ext_proc.v3 import external_processor_pb2_grpc as pb_grpc
from envoy.type.v3 import http_status_pb2

MODE = os.environ.get("MODE", "observe")      # observe | enforce


def headers_of(msg) -> dict[str, str]:
    return {h.key: h.value or h.raw_value.decode() for h in msg.headers.headers}


def decide(h: dict[str, str]) -> tuple[str, str]:
    """The whole policy: nothing under /admin. Returns (verdict, cause)."""
    if h.get(":path", "").startswith("/admin"):
        return "deny", "path_not_allowed"
    return "allow", "default_allow"


class LogEveryRequest(pb_grpc.ExternalProcessorServicer):
    def Process(self, requests, context):
        for req in requests:
            if req.HasField("request_headers"):
                h = headers_of(req.request_headers)
                verdict, cause = decide(h)
                effect = "deny" if verdict == "deny" and MODE == "enforce" else "allow"
                print(json.dumps({
                    "ts": round(time.time(), 3),
                    "request_id": h.get("x-request-id"),
                    "method": h.get(":method"),
                    "path": h.get(":path"),
                    "verdict": verdict,       # what the decider decided
                    "effect": effect,         # what happened to the request
                    "mode": MODE,
                    "cause": cause,
                }), flush=True)
                if effect == "deny":
                    yield pb.ProcessingResponse(immediate_response=pb.ImmediateResponse(
                        status=http_status_pb2.HttpStatus(code=http_status_pb2.Forbidden),
                        body=b"denied by policy\n",
                    ))
                else:
                    yield pb.ProcessingResponse(request_headers=pb.HeadersResponse())


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_ExternalProcessorServicer_to_server(LogEveryRequest(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print(f"ext_proc listening on :50051 (mode={MODE})", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
