import sys
from concurrent import futures
from pathlib import Path

import grpc
from envoy.service.ext_proc.v3 import external_processor_pb2 as pb
from envoy.service.ext_proc.v3 import external_processor_pb2_grpc as pb_grpc
from envoy.type.v3 import http_status_pb2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from decide import decide, headers_of, write_record  # noqa: E402


def deny() -> pb.ImmediateResponse:
    return pb.ImmediateResponse(status=http_status_pb2.HttpStatus(code=http_status_pb2.Forbidden), body=b"denied\n")


class OneRecordPerStream(pb_grpc.ExternalProcessorServicer):
    """Decides at the LAST request phase this stream will see, and records exactly once per stream."""

    def Process(self, requests, context):
        rid = method = path = ""
        recorded = False
        try:
            for req in requests:
                phase = req.WhichOneof("request")
                if phase == "request_headers":
                    h = headers_of(req.request_headers)
                    rid, method, path = h.get("x-request-id", ""), h[":method"], h[":path"]
                    if not req.request_headers.end_of_stream:
                        # A body is coming: wait for it, it is part of the evidence.
                        yield pb.ProcessingResponse(request_headers=pb.HeadersResponse())
                        continue
                    # No body will ever come (GET, HEAD, an empty POST). Decide here or never.
                elif phase != "request_body":
                    continue
                verdict = decide(method, path)
                write_record(rid, method, path, verdict, phase)
                recorded = True
                if verdict == "deny":
                    yield pb.ProcessingResponse(immediate_response=deny())
                    return
                if phase == "request_headers":
                    yield pb.ProcessingResponse(request_headers=pb.HeadersResponse())
                else:
                    yield pb.ProcessingResponse(request_body=pb.BodyResponse())
        finally:
            if not recorded:
                # The stream ended before a decision (the client hung up mid-body, Envoy timed us out).
                # Still one record: an attempt with no decision is evidence too.
                write_record(rid, method, path, "none", "stream_closed")


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_ExternalProcessorServicer_to_server(OneRecordPerStream(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("ext_proc (fixed) listening on :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
