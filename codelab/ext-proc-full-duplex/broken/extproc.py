from concurrent import futures

import grpc
from envoy.service.ext_proc.v3 import external_processor_pb2 as pb
from envoy.service.ext_proc.v3 import external_processor_pb2_grpc as pb_grpc


class ChangeNothing(pb_grpc.ExternalProcessorServicer):
    """A stub: answer every phase, change nothing. Or so it looks."""

    def Process(self, requests, context):
        for req in requests:
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
                    yield pb.ProcessingResponse(request_body=pb.BodyResponse())    # "continue"?
                case "response_body":
                    yield pb.ProcessingResponse(response_body=pb.BodyResponse())   # "continue"?
                case "request_trailers":
                    yield pb.ProcessingResponse(request_trailers=pb.TrailersResponse())
                case "response_trailers":
                    yield pb.ProcessingResponse(response_trailers=pb.TrailersResponse())


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_ExternalProcessorServicer_to_server(ChangeNothing(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    print("ext_proc listening on :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
