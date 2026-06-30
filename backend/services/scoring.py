"""Fraud probability adjustments and alert generation."""

from __future__ import annotations

from backend.services.database import create_alert, list_transactions


def adjust_runtime_probability(
    model_probability: float,
    sender: str,
    amount: float,
    transaction_type: str,
    is_anomaly: bool,
    sender_count: int = 0,
) -> float:
    """Blend model probability with runtime graph/anomaly signals."""
    runtime_probability = 0.0

    if amount >= 500000:
        runtime_probability += 0.32
    elif amount >= 100000:
        runtime_probability += 0.18

    if transaction_type in {"TRANSFER", "CASH_OUT"}:
        runtime_probability += 0.12

    if is_anomaly:
        runtime_probability += 0.18

    if sender_count >= 3:
        runtime_probability += 0.12

    return min(0.99, max(float(model_probability), runtime_probability))


def generate_alerts(transaction: dict, is_anomaly: bool, sender_count: int = 0) -> list[dict]:
    """Create alert rows for high-risk or unusual transactions."""
    alerts = []

    if transaction["prediction"] == 1:
        alerts.append({
            "type": "High-risk transaction detected",
            "message": f"{transaction['sender']} sent {transaction['amount']:.2f} to {transaction['receiver']}.",
            "severity": "high",
        })

    if is_anomaly or transaction["amount"] >= 250000:
        alerts.append({
            "type": "Large transaction anomaly",
            "message": f"Amount {transaction['amount']:.2f} is unusual for recent runtime activity.",
            "severity": "medium",
        })

    if sender_count >= 3:
        alerts.append({
            "type": "Suspicious account cluster",
            "message": f"{transaction['sender']} has repeated transaction activity.",
            "severity": "medium",
        })

    for alert in alerts:
        create_alert(
            alert_type=alert["type"],
            message=alert["message"],
            severity=alert["severity"],
            transaction_id=transaction["id"],
            account_id=transaction["sender"],
        )

    return alerts


def get_risky_accounts() -> set[str]:
    """Return accounts to highlight in the exported graph."""
    transactions = list_transactions(limit=500)
    return {
        transaction["sender"]
        for transaction in transactions
        if transaction["prediction"] == 1 or transaction["probability"] > 0.20
    }

