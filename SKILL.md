---
name: adversarial-finance-audit
description: >-
  Performs a red-team personal finance, tax-efficiency, and penny-exact CSV
  ledger audit: reconciles transactions for duplicates and unaccounted gaps,
  flags RSU/equity short-term vs. long-term capital gains leakage, asset
  location inefficiencies, fee drag, and cash-routing friction. Use when the
  user wants an unfiltered financial/tax audit of exported CSV ledgers or
  portfolio allocations.
---

# Adversarial Finance & Ledger Audit

## Overview

An objective, red-team personal finance and accounting ledger auditor. Reconciles exported CSV ledgers down to the exact cent (`Decimal` arithmetic — never floats), exposes hidden tax leakage (RSU statutory underwithholding, short-term vs. long-term capital gains timing, unused tax-advantaged space), and flags fee drag and cash-routing friction.

*Disclaimer: For educational and analytical auditing only—not licensed tax or fiduciary investment advice.*

## Quick Start

```bash
# Reconcile a CSV ledger (columns: date,description,amount,category) for duplicates, net cashflow, and category totals
uv run scripts/ledger_audit.py reconcile --csv /path/to/ledger.csv --output /tmp/ledger-audit.json

# Audit equity tax lots (columns: ticker,acquire_date,sell_date,cost_basis,proceeds) for STCG vs LTCG & wash-sale windows
uv run scripts/ledger_audit.py tax-lots --csv /path/to/lots.csv --output /tmp/tax-lots.json
```

## Utility Scripts

`scripts/ledger_audit.py` uses Python 3 standard library only (`csv`, `decimal`, `datetime`) with exact `Decimal` penny arithmetic.

### Subcommands
- **`reconcile --csv <file.csv> --output <path.json>`**: Sums exact inflows, outflows, net balance, category breakdown, and flags probable duplicate entries (identical date + exact amount + description).
- **`tax-lots --csv <file.csv> --output <path.json>`**: Classifies each closed lot into **Short-Term (`<= 365 days`)** vs. **Long-Term (`> 365 days`)** capital gain/loss, flags lots sold just shy of 1 year (300–365 days), and summarizes total STCG vs. LTCG.

## Workflow

1. **Penny-Exact Reconciliation:** Run `ledger_audit.py reconcile` on user-provided CSVs to verify every dollar is accounted for and flag duplicate rows or unexplained transfers.
2. **Tax Leakage Audit:** Run `ledger_audit.py tax-lots` and check for:
   - **Equity/RSU Underwithholding:** Statutory 22% federal supplemental withholding vs. higher marginal brackets.
   - **Premature STCG Sales:** Selling appreciated shares at 300–365 days instead of waiting for LTCG rates.
   - **Asset Location:** Placing tax-inefficient income/high-turnover assets in taxable brokerage instead of tax-advantaged (401k/Roth/HSA) accounts.
3. **Capital Plumbing & Fee Drag:** Identify multi-hop idle cash transfers and high-expense-ratio funds (`> 0.25%` ER where low-cost index equivalents exist).
4. **Actionable Red-Team Report:** Rank concrete dollar leaks from largest to smallest with exact remediation steps.

## Common Mistakes

- **Using floating-point math for money:** Always use `decimal.Decimal` to avoid penny rounding drift.
- **Confusing transfers with income/expenses:** Exclude internal account-to-account transfers when computing true savings rate or spending.
