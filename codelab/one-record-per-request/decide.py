"""The policy and the record, shared by broken/ and fixed/. Only WHERE they are called differs."""
import json
import threading
import time

RECORDS = "records.jsonl"
_lock = threading.Lock()


def decide(method: str, path: str) -> str:
    """The whole policy: nobody reaches /admin through this door."""
    return "deny" if path.startswith("/admin") else "allow"


def write_record(rid: str, method: str, path: str, verdict: str, phase: str) -> None:
    """Count 3: one line per decision. Append-only; the reconciler reads it."""
    line = json.dumps({"rid": rid, "method": method, "path": path, "verdict": verdict, "phase": phase,
                       "at": round(time.time(), 3)})
    with _lock, open(RECORDS, "a") as f:
        f.write(line + "\n")
    print(f"record: {verdict:5} {method} {path} ({phase})", flush=True)


def headers_of(req_headers) -> dict[str, str]:
    """ext_proc sends header values as raw bytes in raw_value; fall back to value for older Envoys."""
    return {h.key: (h.raw_value.decode() if h.raw_value else h.value) for h in req_headers.headers.headers}
