from datetime import datetime
from typing import Literal
from pydantic import BaseModel


Status = Literal["healthy", "watch", "warning", "critical"]


class AssetAssessment(BaseModel):
    asset_id: str
    asset_type: str
    timestamp: datetime
    status: Status
    health_score: float
    failure_risk: float
    estimated_rul_hours: int
    anomaly: bool
    anomaly_score: float
    temperature_c: float
    vibration_mm_s: float
    pressure_bar: float
    rpm: float
    recommendation: str
    reasons: list[str]


class Overview(BaseModel):
    total_assets: int
    healthy_assets: int
    attention_assets: int
    critical_assets: int
    anomalies_detected: int
    average_health_score: float
    priority_assets: list[AssetAssessment]
