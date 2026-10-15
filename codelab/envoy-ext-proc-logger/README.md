# envoy-ext-proc-logger

The code for the codelab
[Envoy and a Stub ext_proc That Logs Every Request](https://devnull.fyi/labs/envoy-and-a-stub-ext-proc-that-logs-every-request/).

Envoy runs in Docker with the `ext_proc` filter in front of a stand-in backend. A small Python gRPC processor logs one
line per request and, in `v2/`, applies one rule in observe or enforce mode.

```
envoy.yaml        listener :10000 -> ext_proc (host :50051) -> stand-in backend; failure_mode_allow: false
v1/extproc.py     logs every request and lets it through
v2/extproc.py     adds a rule: MODE=observe (log the verdict) | MODE=enforce (deny with 403)
requirements.txt  grpcio, xds-protos and protobuf, pinned together
```

## Run it

Needs Docker, Python 3.12 or later, and two terminals.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python v1/extproc.py                      # terminal 1 (later: python v2/extproc.py, MODE=enforce python v2/extproc.py)

docker run -d --name l1-envoy -p 10000:10000 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro" envoyproxy/envoy:v1.39.4   # terminal 2
curl -s localhost:10000/hello
docker rm -f l1-envoy
```

On colima use `--add-host=host.docker.internal:192.168.5.2`. The walkthrough has every step and its output.
