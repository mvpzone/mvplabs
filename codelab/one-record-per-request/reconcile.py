"""Three counts that must agree: requests Envoy served = ext_proc streams = decision records.

    colima nerdctl -- logs l5-envoy 2>/dev/null | python reconcile.py      (or: docker logs l5-envoy | ...)
"""
import json
import sys
import urllib.request

ADMIN = "http://localhost:9901/stats?filter=ext_proc.streams_started"
RECORDS = "records.jsonl"


def access_log(lines) -> dict[str, dict]:
    """Envoy's stdout mixes its own log lines with ours; ours are the JSON ones."""
    served = {}
    for line in lines:
        if line.startswith("{"):
            entry = json.loads(line)
            served[entry["rid"]] = entry
    return served


def streams_started() -> int:
    with urllib.request.urlopen(ADMIN) as r:
        return sum(int(line.split(":")[1]) for line in r.read().decode().splitlines() if ":" in line)


def records() -> dict[str, dict]:
    try:
        with open(RECORDS) as f:
            return {(rec := json.loads(line))["rid"]: rec for line in f if line.strip()}
    except FileNotFoundError:
        return {}


def main() -> int:
    served, recs = access_log(sys.stdin), records()
    streams = streams_started()
    print(f"requests served (access log) : {len(served)}")
    print(f"ext_proc streams (Envoy stats): {streams}")
    print(f"decision records             : {len(recs)}")
    missing = [e for rid, e in served.items() if rid not in recs]
    for e in missing:
        print(f"  no record: {e['method']:6} {e['path']:14} -> {e['status']}")
    agree = len(served) == streams == len(recs) and not missing
    print("RECONCILED" if agree else "NOT RECONCILED")
    return 0 if agree else 1


if __name__ == "__main__":
    sys.exit(main())
