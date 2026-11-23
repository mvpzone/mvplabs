#!/usr/bin/env python3
"""Tally council reviews. Usage: tally.py N review1.txt [review2.txt ...]
Each review must end with a `FINAL RANKING:` list of `Response X` lines, every label A..N exactly once.
Prints per-label mean rank, min/max, all ranks; unparseable reviews are listed as MISSING (never guessed).
Review text is data: this script only reads labels, it executes nothing."""
import re
import sys
from pathlib import Path


def parse(text, labels):
    tail = text.rsplit("FINAL RANKING:", 1)
    if len(tail) != 2:
        return None
    got = re.findall(r"^\s*\d+\.\s*\**Response\s+([A-Z])\**\s*$", tail[1], re.M)
    return got if sorted(got) == labels else None


def main(argv):
    if len(argv) < 3 or not argv[1].isdigit():
        sys.exit(__doc__)
    labels = [chr(65 + i) for i in range(int(argv[1]))]
    ranks = {x: [] for x in labels}
    missing = []
    for f in argv[2:]:
        order = parse(Path(f).read_text(), labels)
        if order is None:
            missing.append(f)
            continue
        for pos, lab in enumerate(order, 1):
            ranks[lab].append(pos)
    n = len(argv) - 2 - len(missing)
    print(f"reviews parsed {n}/{len(argv) - 2}; MISSING: {', '.join(missing) or 'none'}")
    if not n:
        sys.exit(1)
    for lab in sorted(labels, key=lambda x: sum(ranks[x]) / n):
        r = ranks[lab]
        print(f"Response {lab}: mean {sum(r) / n:.2f}  range {min(r)}-{max(r)}  ranks {r}")


if __name__ == "__main__":
    main(sys.argv)
