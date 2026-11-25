#!/usr/bin/env python3
"""Merge a fresh uTest payments export into the canonical dataset.

Usage:
    python3 scripts/merge_utest_payments.py data/raw_utest_payments.json data/utest_payments.json

Upserts by line-item `id` (a composite of paymentId-entityTypeId-entityId,
which is stable and unique per paid item). uTest payment line items never
change once issued, but re-fetching is harmless — any row with the same id
is simply overwritten with the latest copy.
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    raw_path = Path(sys.argv[1])
    canonical_path = Path(sys.argv[2])

    raw = json.loads(raw_path.read_text())
    new_entries = raw["entries"]

    if canonical_path.exists():
        canonical = json.loads(canonical_path.read_text())
        by_id = {e["id"]: e for e in canonical["entries"]}
    else:
        by_id = {}

    added = 0
    updated = 0
    for e in new_entries:
        if e["id"] not in by_id:
            added += 1
        elif by_id[e["id"]] != e:
            updated += 1
        by_id[e["id"]] = e

    merged_entries = sorted(by_id.values(), key=lambda e: e["date"], reverse=True)

    out = {
        "lastUpdated": raw["fetchedAt"],
        "totalPayoutAllTime": raw.get("totalPayoutAllTime"),
        "pendingPayout": raw.get("pendingPayout"),
        "count": len(merged_entries),
        "entries": merged_entries,
    }
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"Fetched: {len(new_entries)}  Added: {added}  Updated: {updated}  Total now: {len(merged_entries)}")


if __name__ == "__main__":
    main()
