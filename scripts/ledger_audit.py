#!/usr/bin/env python3
"""Penny-exact CSV ledger reconciler and STCG/LTCG tax-lot auditor (Python 3 stdlib only)."""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


def parse_decimal(val: str) -> Decimal:
    cleaned = val.strip().replace("$", "").replace(",", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0.00")


def cmd_reconcile(csv_path: Path, output: Path) -> None:
    if not csv_path.exists():
        print(f"Error: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    inflows = Decimal("0.00")
    outflows = Decimal("0.00")
    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    seen: dict[tuple[str, str, str], int] = defaultdict(int)
    rows = 0

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows += 1
            date = (row.get("date") or row.get("Date") or "").strip()
            desc = (row.get("description") or row.get("Description") or "").strip()
            cat = (row.get("category") or row.get("Category") or "Uncategorized").strip()
            amt = parse_decimal(row.get("amount") or row.get("Amount") or "0")
            if amt >= 0:
                inflows += amt
            else:
                outflows += amt
            by_category[cat] += amt
            seen[(date, desc.lower(), str(amt))] += 1

    duplicates = [
        {"date": k[0], "description": k[1], "amount": k[2], "occurrences": v}
        for k, v in seen.items()
        if v > 1
    ]

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "csv": str(csv_path),
        "rows_processed": rows,
        "total_inflows": str(inflows.quantize(Decimal("0.01"))),
        "total_outflows": str(outflows.quantize(Decimal("0.01"))),
        "net_cashflow": str((inflows + outflows).quantize(Decimal("0.01"))),
        "probable_duplicate_count": len(duplicates),
        "probable_duplicates": duplicates[:50],
        "by_category": {k: str(v.quantize(Decimal("0.01"))) for k, v in sorted(by_category.items())},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    print(f"Success! Reconciled {rows} rows (net={report['net_cashflow']}, dups={len(duplicates)}) -> {output}")


def cmd_tax_lots(csv_path: Path, output: Path) -> None:
    if not csv_path.exists():
        print(f"Error: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    stcg = Decimal("0.00")
    ltcg = Decimal("0.00")
    near_ltcg_traps = []
    lots_count = 0

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lots_count += 1
            ticker = (row.get("ticker") or row.get("Ticker") or "UNKNOWN").strip()
            acq = datetime.strptime((row.get("acquire_date") or "").strip(), "%Y-%m-%d").date()
            sell = datetime.strptime((row.get("sell_date") or "").strip(), "%Y-%m-%d").date()
            basis = parse_decimal(row.get("cost_basis") or "0")
            proceeds = parse_decimal(row.get("proceeds") or "0")
            gain = proceeds - basis
            held_days = (sell - acq).days
            if held_days > 365:
                ltcg += gain
            else:
                stcg += gain
                if 300 <= held_days <= 365 and gain > 0:
                    near_ltcg_traps.append({
                        "ticker": ticker,
                        "acquire_date": str(acq),
                        "sell_date": str(sell),
                        "held_days": held_days,
                        "short_term_gain": str(gain.quantize(Decimal("0.01"))),
                    })

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "csv": str(csv_path),
        "lots_processed": lots_count,
        "total_short_term_gain_loss": str(stcg.quantize(Decimal("0.01"))),
        "total_long_term_gain_loss": str(ltcg.quantize(Decimal("0.01"))),
        "near_ltcg_trap_count": len(near_ltcg_traps),
        "near_ltcg_traps": near_ltcg_traps,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    print(f"Success! Audited {lots_count} tax lots (STCG={report['total_short_term_gain_loss']}, LTCG={report['total_long_term_gain_loss']}) -> {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Adversarial Finance & Penny-Exact Ledger Audit CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_r = sub.add_parser("reconcile", help="Reconcile CSV ledger using exact Decimal math")
    p_r.add_argument("--csv", required=True, type=Path)
    p_r.add_argument("--output", required=True, type=Path)

    p_t = sub.add_parser("tax-lots", help="Classify STCG vs LTCG and flag premature short-term sales")
    p_t.add_argument("--csv", required=True, type=Path)
    p_t.add_argument("--output", required=True, type=Path)

    args = parser.parse_args()
    if args.command == "reconcile":
        cmd_reconcile(args.csv, args.output)
    elif args.command == "tax-lots":
        cmd_tax_lots(args.csv, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
