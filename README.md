# Adversarial Finance Audit

Agent skill and Python 3 stdlib CLI for red-team personal finance auditing: penny-exact `Decimal` CSV ledger reconciliation, duplicate detection, STCG vs. LTCG tax-lot leakage checks, and asset-location/fee-drag review.

## Install as an Agent Skill

```bash
npx skills add prasadabhishek/adversarial-finance-audit
```

## Standalone CLI Usage

```bash
# Reconcile a CSV ledger (date,description,amount,category)
uv run scripts/ledger_audit.py reconcile --csv ./ledger.csv --output /tmp/ledger.json

# Audit closed equity tax lots (ticker,acquire_date,sell_date,cost_basis,proceeds)
uv run scripts/ledger_audit.py tax-lots --csv ./lots.csv --output /tmp/lots.json
```

## License

MIT

---
Built by [Abhishek Prasad](https://abhishekprasad.fyi)
