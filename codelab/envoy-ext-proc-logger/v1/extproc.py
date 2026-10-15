import json
import time
from concurrent import futures

import grpc
from envoy.service.ext_proc.v3 import external_processor_pb2 as pb
from envoy.service.ext_proc.v3 import external_processor_pb2_grpc as pb_grpc


def headers_of(msg) -> dict[str, str]:
    # Envoy sends header values as bytes in raw_value; older builds used value.
    return {h.key: h.value or h.raw_value.decode() for h in msg.headers.headers}


class LogEveryRequest(pb_grpc.ExternalProcessorServicer):
    def Process(self, requests, context):
        # One gRPC stream per HTTP request; one message per phase Envoy sends.
        for req in requests:
            if req.HasField("request_headers"):
                h = headers_of(req.request_headers)
                print(json.dumps({
                    "ts": round(time.time(), 3),
                    "request_id": h.get("x-request-id"),
                    "method": h.get(":method"),
                    "authority": h.get(":authority"),
                    "path": h.get(":path"),
                }), flush=True)
                # "Continue" is an explicit, empty HeadersResponse. A reply with
                # nothing set is malformed, not a no-op.
                yield pb.ProcessingResponse(request_headers=pb.HeadersResponse())


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_ExternalProcessorServicer_to_server(LogEveryRequest(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("ext_proc listening on :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
