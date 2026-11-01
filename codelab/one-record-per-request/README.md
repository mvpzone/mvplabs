# one-record-per-request

The code for the codelab
[One Record per Request, Reconciled](https://devnull.fyi/labs/one-record-per-request-reconciled/).

Envoy runs in a container with the `ext_proc` filter in front of a small backend on your laptop. A decision service
that decides (and records) when the request body arrives never sees a request without one: `GET /admin` walks past a
policy that denies `/admin`, and leaves no record. Three counts expose it; the fixed service decides at the last
request phase each stream will see and writes exactly one record per stream, even when the client hangs up.

```
envoy.yaml         listener :10000 -> ext_proc (host :50051) -> backend (host :8081); admin :9901; JSON access log
backend.py         answers GET / HEAD / POST / DELETE on any path with 200
decide.py          the policy (deny /admin) and the record writer (records.jsonl), shared by both processors
broken/extproc.py  decides and records in the request_body phase only
fixed/extproc.py   decides at end_of_stream (headers or body); a finally block records streams that end undecided
traffic.sh         ten requests, four without a body
hangup.py          promises 100 bytes, sends 10, hangs up
reconcile.py       access-log requests = ext_proc streams (Envoy stats) = decision records, joined on x-request-id
requirements.txt   grpcio, xds-protos and protobuf, pinned together
```

## Run it

Needs Docker (or colima with `nerdctl`, see below), Python 3.12 or later, and three terminals.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python backend.py                         # terminal 1
python broken/extproc.py                  # terminal 2 (later: python fixed/extproc.py)

docker run -d --name l5-envoy -p 10000:10000 -p 9901:9901 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro" envoyproxy/envoy:v1.39.4 \
  -c /etc/envoy/envoy.yaml --file-flush-interval-msec 200     # terminal 3
./traffic.sh
docker logs l5-envoy 2>/dev/null | python reconcile.py
docker rm -f l5-envoy
```

Restart Envoy (and `rm records.jsonl`) between the broken and fixed runs so the three counts start from zero.

On colima use `--add-host=host.docker.internal:192.168.5.2` (`host-gateway` resolves to the VM, not your Mac), run each
`docker` command as `colima nerdctl -- ` with the same flags, and keep this folder under your home directory (colima
shares only `~` with the VM). The walkthrough has every step and its output.
