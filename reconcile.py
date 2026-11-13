
#!/usr/bin/env python3
"""Payment reconciliation."""

import json
from decimal import Decimal
from datetime import datetime

# Store the latest attempt for each transaction
latest_transactions = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)

            # Ignore events without a transaction ID
            txn_id = event.get("txn_id")

            if not txn_id:
                continue

            # Convert timestamp to datetime
            timestamp = datetime.fromisoformat(
                event["ts"].replace("Z", "+00:00")
            )

            # Keep only the latest attempt
            previous = latest_transactions.get(txn_id)

            if previous is None or timestamp > previous["timestamp"]:
                latest_transactions[txn_id] = {
                    "timestamp": timestamp,
                    "status": event["status"],
                   "amount": Decimal(str(event["amount"]).replace(",", ""))
                }

        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue

# Count and sum only the latest successful attempts
successful_transactions = [
    transaction
    for transaction in latest_transactions.values()
    if transaction["status"] == "success"
]

count = len(successful_transactions)

total = sum(
    (transaction["amount"] for transaction in successful_transactions),
    Decimal("0")
)

# Compare with the expected count
with open("expected.txt", "r", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
