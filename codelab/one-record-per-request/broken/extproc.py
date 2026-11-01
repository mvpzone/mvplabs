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


class DecideOnTheBody(pb_grpc.ExternalProcessorServicer):
    """Decides when the payload arrives: that is where the interesting evidence is."""

    def Process(self, requests, context):
        rid = method = path = ""
        for req in requests:
            match req.WhichOneof("request"):
                case "request_headers":
                    h = headers_of(req.request_headers)
                    rid, method, path = h.get("x-request-id", ""), h[":method"], h[":path"]
                    yield pb.ProcessingResponse(request_headers=pb.HeadersResponse())
                case "request_body":
                    verdict = decide(method, path)
                    write_record(rid, method, path, verdict, "request_body")
                    if verdict == "deny":
                        yield pb.ProcessingResponse(immediate_response=deny())
                        return
                    yield pb.ProcessingResponse(request_body=pb.BodyResponse())


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_ExternalProcessorServicer_to_server(DecideOnTheBody(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("ext_proc (broken) listening on :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
