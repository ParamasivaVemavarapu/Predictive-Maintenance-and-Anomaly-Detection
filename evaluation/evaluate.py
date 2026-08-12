"""Offline alert-quality, lead-time, and drift evaluation."""

import argparse
import json
import math
from datetime import datetime
from pathlib import Path


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def psi(reference: list[float], current: list[float], bins: int = 5) -> float:
    ordered = sorted(reference)
    edges = [ordered[min(len(ordered) - 1, int(i * len(ordered) / bins))] for i in range(1, bins)]

    def proportions(values: list[float]) -> list[float]:
        counts = [0] * bins
        for value in values:
            index = sum(value > edge for edge in edges)
            counts[index] += 1
        return [max(count / len(values), 1e-6) for count in counts]

    expected, actual = proportions(reference), proportions(current)
    return sum((a - e) * math.log(a / e) for e, a in zip(expected, actual))


def evaluate(payload: dict) -> dict:
    alerts = payload["alerts"]
    tp = sum(row["actual_failure"] and row["predicted_alert"] for row in alerts)
    fp = sum((not row["actual_failure"]) and row["predicted_alert"] for row in alerts)
    fn = sum(row["actual_failure"] and (not row["predicted_alert"]) for row in alerts)
    lead_hours = [
        (parse_time(row["failure_time"]) - parse_time(row["alert_time"])).total_seconds() / 3600
        for row in alerts
        if row["actual_failure"] and row["predicted_alert"]
    ]
    drift = {
        feature: psi(windows["reference"], windows["current"])
        for feature, windows in payload["drift"].items()
    }
    return {
        "precision": tp / (tp + fp),
        "recall": tp / (tp + fn),
        "mean_alert_lead_time_hours": sum(lead_hours) / len(lead_hours),
        "feature_psi": drift,
        "drifted_features": [name for name, score in drift.items() if score >= 0.20],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).with_name("maintenance_eval.json"))
    args = parser.parse_args()
    metrics = evaluate(json.loads(args.dataset.read_text(encoding="utf-8")))
    print(json.dumps(metrics, indent=2))
    assert metrics["precision"] >= 0.60
    assert metrics["recall"] >= 0.60
    assert metrics["mean_alert_lead_time_hours"] > 0


if __name__ == "__main__":
    main()
