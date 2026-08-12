import pandas as pd
from app.analytics import analyze, assessment, latest_assessments


def sample():
    return pd.DataFrame([
        {"timestamp":"2026-01-01","asset_id":"A","asset_type":"Pump","temperature_c":55,"vibration_mm_s":1.5,"pressure_bar":6.5,"rpm":1500,"operating_hours":1000},
        {"timestamp":"2026-01-02","asset_id":"A","asset_type":"Pump","temperature_c":90,"vibration_mm_s":7.0,"pressure_bar":4.5,"rpm":2100,"operating_hours":9000},
        {"timestamp":"2026-01-01","asset_id":"B","asset_type":"Motor","temperature_c":58,"vibration_mm_s":1.8,"pressure_bar":6.2,"rpm":1450,"operating_hours":1500},
        {"timestamp":"2026-01-02","asset_id":"B","asset_type":"Motor","temperature_c":59,"vibration_mm_s":1.9,"pressure_bar":6.2,"rpm":1455,"operating_hours":1504},
    ])


def test_analysis_adds_anomaly_fields():
    result = analyze(sample(), .25)
    assert {"anomaly", "anomaly_score"}.issubset(result.columns)


def test_high_stress_has_higher_risk():
    result = analyze(sample(), .25)
    low = assessment(result.iloc[0])
    high = assessment(result.iloc[1])
    assert high.failure_risk > low.failure_risk
    assert high.estimated_rul_hours < low.estimated_rul_hours


def test_one_latest_assessment_per_asset():
    assert len(latest_assessments(analyze(sample(), .25))) == 2
