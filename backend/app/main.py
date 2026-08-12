from functools import lru_cache
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .analytics import assessment, latest_assessments
from .config import get_settings
from .models import AssetAssessment, Overview
from .store import SensorStore

settings = get_settings()
app = FastAPI(title="Predictive Maintenance API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache
def store() -> SensorStore:
    return SensorStore(settings.data_path, settings.anomaly_contamination)


@app.get("/")
def root() -> dict:
    return {
        "service": "Predictive Maintenance API",
        "version": app.version,
        "status": "live",
        "health": "/health",
        "documentation": "/docs",
        "overview": "/api/overview",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/assets", response_model=list[AssetAssessment])
def assets(data: SensorStore = Depends(store)):
    return latest_assessments(data.data)


@app.get("/api/overview", response_model=Overview)
def overview(data: SensorStore = Depends(store)):
    items = latest_assessments(data.data)
    return Overview(
        total_assets=len(items), healthy_assets=sum(item.status == "healthy" for item in items),
        attention_assets=sum(item.status in {"watch", "warning"} for item in items),
        critical_assets=sum(item.status == "critical" for item in items),
        anomalies_detected=int(data.data.anomaly.sum()),
        average_health_score=round(sum(item.health_score for item in items) / len(items), 1) if items else 0,
        priority_assets=items[:5],
    )


@app.get("/api/assets/{asset_id}")
def asset_detail(asset_id: str, data: SensorStore = Depends(store)):
    rows = data.data[data.data.asset_id == asset_id]
    if rows.empty:
        raise HTTPException(404, "Asset not found")
    history = rows.assign(timestamp=rows.timestamp.astype(str)).to_dict(orient="records")
    return {"assessment": assessment(rows.iloc[-1]), "history": history}


@app.get("/api/anomalies")
def anomalies(data: SensorStore = Depends(store)):
    rows = data.data[data.data.anomaly].copy()
    rows["timestamp"] = rows.timestamp.astype(str)
    return rows.to_dict(orient="records")


@app.post("/api/data/upload", status_code=201)
async def upload(file: UploadFile = File(...), data: SensorStore = Depends(store)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(415, "Upload a CSV file")
    try:
        rows = data.replace(await file.read())
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"filename": file.filename, "rows": rows}
