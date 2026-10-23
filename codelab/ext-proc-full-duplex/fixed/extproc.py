import os
from concurrent import futures

import grpc
from envoy.extensions.filters.http.ext_proc.v3.processing_mode_pb2 import ProcessingMode
from envoy.service.ext_proc.v3 import external_processor_pb2 as pb
from envoy.service.ext_proc.v3 import external_processor_pb2_grpc as pb_grpc

# DROP=request hands every request chunk back EMPTY; DROP=all does it in both directions. The quiet-failure step uses it.
DROP = os.environ.get("DROP", "")


def body_response(chunk, streamed: bool, phase: str) -> pb.BodyResponse:
    """In FULL_DUPLEX_STREAMED mode a body chunk is yours until you hand it back."""
    if not streamed:
        return pb.BodyResponse()   # buffered / streamed modes: the empty response is the continue
    drop = DROP == "all" or (DROP == "request" and phase == "request_body")
    body = b"" if drop else chunk.body
    return pb.BodyResponse(response=pb.CommonResponse(body_mutation=pb.BodyMutation(
        streamed_response=pb.StreamedBodyResponse(body=body, end_of_stream=chunk.end_of_stream))))


class EchoEveryChunk(pb_grpc.ExternalProcessorServicer):
    def Process(self, requests, context):
        request_streamed = response_streamed = True
        for i, req in enumerate(requests):
            if i == 0 and req.HasField("protocol_config"):
                # Envoy says which body mode each direction uses, once, in the first message.
                cfg = req.protocol_config
                request_streamed = cfg.request_body_mode == ProcessingMode.FULL_DUPLEX_STREAMED
                response_streamed = cfg.response_body_mode == ProcessingMode.FULL_DUPLEX_STREAMED
            phase = req.WhichOneof("request")
            if phase in ("request_body", "response_body"):
                chunk = getattr(req, phase)
                print(f"{phase}: {len(chunk.body)} bytes, end_of_stream={chunk.end_of_stream}", flush=True)
            else:
                print(phase, flush=True)
            match phase:
                case "request_headers":
                    yield pb.ProcessingResponse(request_headers=pb.HeadersResponse())
                case "response_headers":
                    yield pb.ProcessingResponse(response_headers=pb.HeadersResponse())
                case "request_body":
                    yield pb.ProcessingResponse(request_body=body_response(req.request_body, request_streamed, phase))
                case "response_body":
                    yield pb.ProcessingResponse(response_body=body_response(req.response_body, response_streamed, phase))
                case "request_trailers":
                    yield pb.ProcessingResponse(request_trailers=pb.TrailersResponse())
                case "response_trailers":
                    yield pb.ProcessingResponse(response_trailers=pb.TrailersResponse())


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_ExternalProcessorServicer_to_server(EchoEveryChunk(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("ext_proc listening on :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
