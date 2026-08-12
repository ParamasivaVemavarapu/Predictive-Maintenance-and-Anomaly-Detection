# Predictive Maintenance and Anomaly Detection

A full-stack industrial analytics application that converts equipment sensor readings into anomaly alerts, explainable failure-risk scores, health trends, and maintenance recommendations.

## The Problem

Reactive maintenance can lead to unplanned downtime, while fixed schedules may service healthy equipment too early. Maintenance teams need a clear way to identify unusual operating conditions, prioritize assets, and understand why a machine has been flagged.

## The Solution

The platform ingests time-series sensor data, validates the schema, engineers operating features, and applies an Isolation Forest to identify multivariate anomalies. A transparent risk layer combines sensor stress, operating hours, and anomaly severity into a 0–100 risk score, estimated remaining useful life, maintenance priority, and recommended action. FastAPI serves the analysis to a Next.js dashboard.

## Tech Stack

**Python | pandas | NumPy | scikit-learn | FastAPI | Next.js | TypeScript | Docker | GitHub Actions**

> AWS deployment and MLflow tracking are production-roadmap items; they are not claimed as part of the current implementation.

## Architecture

```mermaid
flowchart TD
    CSV["Sensor CSV"] --> API["FastAPI API"]
    API --> VALIDATE["Schema validation"]
    VALIDATE --> FE["Feature engineering"]
    FE --> IF["Isolation Forest"]
    FE --> RISK["Risk and RUL engine"]
    IF --> RESULT["Asset assessment"]
    RISK --> RESULT
    RESULT --> UI["Next.js dashboard"]
```

## Key Features

- Display fleet-level health and maintenance KPIs
- Detect multivariate operating anomalies with Isolation Forest
- Score failure risk from temperature, vibration, pressure, RPM, hours, and anomaly severity
- Estimate remaining useful life for decision support
- Assign maintenance priority and recommended action per asset
- Visualize sensor history and health trends
- Upload replacement CSV data with schema validation
- Explore results through FastAPI endpoints and a Next.js dashboard
- Run frontend and backend with Docker Compose
- Validate the backend with tests and GitHub Actions CI

## Results

The application produces a complete assessment for every asset: anomaly state, explainable 0–100 risk score, estimated RUL, priority, and recommended action. The included dataset is synthetic, so the outputs demonstrate the engineering workflow rather than certified predictive performance. Precision, recall, alert lead time, and avoided-downtime metrics require labeled maintenance history and are not fabricated here.

## Screenshots / Demo

The local demo exposes:

- Analytics dashboard: `http://localhost:3000`
- Interactive API documentation: `http://localhost:8000/docs`

After startup, review the fleet overview, open an individual asset to inspect its sensor history and risk explanation, then upload a valid CSV to rerun the analysis.

## How to Run

### Prerequisites

- Docker and Docker Compose

### Setup

```bash
git clone https://github.com/ParamasivaVemavarapu/Predictive-Maintenance-and-Anomaly-Detection.git
cd Predictive-Maintenance-and-Anomaly-Detection
cp backend/.env.example backend/.env
docker compose up --build
```

## Dataset Schema

The uploaded CSV must contain:

```text
timestamp, asset_id, asset_type, temperature_c, vibration_mm_s,
pressure_bar, rpm, operating_hours
```

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check API health |
| `GET` | `/api/overview` | Return fleet KPIs and priority assets |
| `GET` | `/api/assets` | Return the latest assessment for each asset |
| `GET` | `/api/assets/{asset_id}` | Return asset history and assessment |
| `GET` | `/api/anomalies` | Return detected anomalous readings |
| `POST` | `/api/data/upload` | Replace the active sensor dataset |

## Model Design

Isolation Forest identifies uncommon multivariate states without requiring failure labels. The explainable risk layer then converts normalized sensor stress, equipment age, and anomaly severity into operational decision support. Risk and RUL estimates are not manufacturer-certified predictions.

## Production Roadmap

- Add screenshots and a hosted demonstration
- Train supervised failure and RUL models on labeled history
- Track experiments and register models with MLflow
- Deploy services on AWS with managed storage and monitoring
- Backtest precision, recall, alert lead time, and avoided downtime
- Add streaming ingestion, drift monitoring, CMMS integration, RBAC, and audit logs

## License

MIT
