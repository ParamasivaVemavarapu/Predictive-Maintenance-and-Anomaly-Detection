# Predictive Maintenance Evaluation

This synthetic backtest fixture contains labeled failure outcomes, alert timestamps, failure timestamps, and two monitoring windows.

Metrics:

- **Precision:** true failure alerts divided by all alerts.
- **Recall:** detected failures divided by all labeled failures.
- **Alert lead time:** mean hours between a true-positive alert and the subsequent failure.
- **Drift monitoring:** Population Stability Index (PSI) for each sensor feature; `PSI >= 0.20` is flagged for investigation.

Run:

```bash
python evaluation/evaluate.py
```

The script prints machine-readable JSON and fails CI if alert-quality gates regress. These synthetic values verify the evaluation implementation; they do not establish field performance. Replace the fixture with time-split, labeled maintenance history for model validation.
