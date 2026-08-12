import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from .models import AssetAssessment


FEATURES = ["temperature_c", "vibration_mm_s", "pressure_bar", "rpm", "operating_hours"]
REQUIRED = {"timestamp", "asset_id", "asset_type", *FEATURES}


def validate(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    clean = df.copy()
    clean["timestamp"] = pd.to_datetime(clean["timestamp"], errors="raise")
    clean[FEATURES] = clean[FEATURES].apply(pd.to_numeric, errors="raise")
    if clean[FEATURES].isna().any().any():
        raise ValueError("Sensor values cannot be empty")
    return clean.sort_values(["asset_id", "timestamp"])


def analyze(df: pd.DataFrame, contamination: float = 0.15) -> pd.DataFrame:
    result = validate(df)
    scaled = StandardScaler().fit_transform(result[FEATURES])
    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=150)
    prediction = model.fit_predict(scaled)
    raw = -model.score_samples(scaled)
    result["anomaly"] = prediction == -1
    span = max(float(raw.max() - raw.min()), 1e-9)
    result["anomaly_score"] = (raw - raw.min()) / span * 100
    return result


def assessment(row: pd.Series) -> AssetAssessment:
    temp_stress = np.clip((row.temperature_c - 55) / 40, 0, 1)
    vibration_stress = np.clip((row.vibration_mm_s - 1.5) / 6.5, 0, 1)
    pressure_stress = np.clip(abs(row.pressure_bar - 6.5) / 4, 0, 1)
    age_stress = np.clip(row.operating_hours / 12000, 0, 1)
    risk = float(np.clip((.28 * temp_stress + .34 * vibration_stress + .13 * pressure_stress + .15 * age_stress + .10 * row.anomaly_score / 100) * 100, 0, 100))
    health = 100 - risk
    if risk >= 75: status, recommendation = "critical", "Inspect immediately and schedule controlled shutdown"
    elif risk >= 55: status, recommendation = "warning", "Create a high-priority maintenance work order"
    elif risk >= 35: status, recommendation = "watch", "Increase inspection frequency and review trend"
    else: status, recommendation = "healthy", "Continue normal preventive maintenance schedule"
    reasons = []
    if temp_stress > .55: reasons.append("Elevated temperature")
    if vibration_stress > .5: reasons.append("High vibration")
    if pressure_stress > .45: reasons.append("Pressure outside normal band")
    if age_stress > .65: reasons.append("High accumulated operating hours")
    if bool(row.anomaly): reasons.append("Multivariate anomaly detected")
    return AssetAssessment(
        asset_id=row.asset_id, asset_type=row.asset_type, timestamp=row.timestamp,
        status=status, health_score=round(health, 1), failure_risk=round(risk, 1),
        estimated_rul_hours=max(24, int((100 - risk) / 100 * 2400)), anomaly=bool(row.anomaly),
        anomaly_score=round(float(row.anomaly_score), 1), temperature_c=float(row.temperature_c),
        vibration_mm_s=float(row.vibration_mm_s), pressure_bar=float(row.pressure_bar), rpm=float(row.rpm),
        recommendation=recommendation, reasons=reasons or ["Sensors within expected operating range"],
    )


def latest_assessments(analyzed: pd.DataFrame) -> list[AssetAssessment]:
    latest = analyzed.groupby("asset_id", as_index=False).tail(1)
    return sorted([assessment(row) for _, row in latest.iterrows()], key=lambda item: item.failure_risk, reverse=True)
