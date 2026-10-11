"""Publish sanitised APEX paper-trading data."""

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

portfolio = json.loads(
    (DOCS / "portfolio.json").read_text()
)

report = json.loads(
    (DOCS / "engine_report.json").read_text()
)

history = portfolio.get("history", [])

snapshots_file = DOCS / "portfolio_history.json"

if snapshots_file.exists():
    snapshots = json.loads(
        snapshots_file.read_text()
    )
else:
    snapshots = []

equity = report.get("equity")

if equity is not None:
    snapshots.append({
        "time": datetime.now(
            timezone.utc
        ).isoformat(),
        "equity": equity
    })

snapshots = snapshots[-1000:]

snapshots_file.write_text(
    json.dumps(snapshots, indent=2)
)

dashboard = {
    "mode": "PAPER",
    "updated_at": report.get("updated_at"),
    "equity": equity,
    "cash": report.get("cash"),
    "positions": [
        {
            "symbol": p.get("symbol"),
            "entry_price": p.get("entry_price"),
            "quantity": p.get("quantity"),
            "cost": p.get("cost")
        }
        for p in portfolio.get("positions", [])
    ],
    "history": [
        {
            "time": t.get("time"),
            "side": t.get("side"),
            "symbol": t.get("symbol"),
            "price": t.get("price"),
            "total": t.get("total"),
            "profit": t.get("profit")
        }
        for t in history[-100:]
    ],
    "portfolio_history": snapshots,
    "workers": {
        "hunter": "ACTIVE",
        "analyst": "ACTIVE",
        "trader": "PAPER",
        "supervisor": (
            "HALTED"
            if report.get("halted")
            else "ACTIVE"
        )
    }
}

(DOCS / "dashboard_data.json").write_text(
    json.dumps(dashboard, indent=2)
)

print("Dashboard data prepared.")
