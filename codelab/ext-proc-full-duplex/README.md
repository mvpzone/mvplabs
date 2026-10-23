# ext-proc-full-duplex

The code for the codelab
[The Reply That Deleted Every Body](https://devnull.fyi/labs/the-reply-that-deleted-every-body/).

Envoy runs in a container with the `ext_proc` filter in `FULL_DUPLEX_STREAMED` mode for request and response bodies, in
front of a small backend on your laptop. A stub processor that "changes nothing" breaks every body; the fixed one hands
each chunk back.

```
envoy.yaml         listener :10000 -> ext_proc (host :50051) -> backend (host :8081); bodies FULL_DUPLEX_STREAMED
backend.py         /hello (never reads the body) · /rpc (JSON-RPC, errors inside a 200) · /echo (returns the body)
broken/extproc.py  answers every phase with an empty response
fixed/extproc.py   echoes every body chunk; DROP=request | DROP=all hands chunks back empty
canary.sh          sends 300000 random bytes through /echo and compares the hashes
requirements.txt   grpcio, xds-protos and protobuf, pinned together
```

## Run it

Needs Docker (or colima with `nerdctl`, see below), Python 3.12 or later, and three terminals.

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python backend.py                         # terminal 1
python broken/extproc.py                  # terminal 2 (later: python fixed/extproc.py, DROP=request python fixed/extproc.py)

docker run -d --name l3-envoy -p 10000:10000 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD/envoy.yaml:/etc/envoy/envoy.yaml:ro" envoyproxy/envoy:v1.39.4   # terminal 3
curl -s localhost:10000/rpc -d '{"jsonrpc":"2.0","id":1,"method":"ping","params":{"n":1}}'
./canary.sh
docker rm -f l3-envoy
```

On colima use `--add-host=host.docker.internal:192.168.5.2` (`host-gateway` resolves to the VM, not your Mac), run each
`docker` command as `colima nerdctl -- ` with the same flags, and keep this folder under your home directory (colima
shares only `~` with the VM). The walkthrough has every step and its output.
