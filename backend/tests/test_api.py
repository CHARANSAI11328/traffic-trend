import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "TRAFFIC TREND" in response.json()["platform"]

def test_system_status():
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert data["database"]["status"] == "healthy"

def test_data_freshness():
    response = client.get("/api/v1/system/data-freshness")
    assert response.status_code == 200
    data = response.json()
    assert data["live_feed_connected"] is False
    assert "Historical / Uploaded Data" in data["feed_mode"]

def test_dashboard_overview():
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert data["kpis"]["total_accidents"] > 0
    assert "top_states" in data
    assert "yearly_trend" in data

def test_dashboard_trends():
    response = client.get("/api/v1/dashboard/trends")
    assert response.status_code == 200
    data = response.json()
    assert len(data["yearly"]) > 0
    assert len(data["monthly"]) > 0
    assert len(data["day_of_week"]) > 0

def test_dashboard_geography():
    response = client.get("/api/v1/dashboard/geography")
    assert response.status_code == 200
    data = response.json()
    assert len(data["states"]) > 0
    assert len(data["map_points"]) > 0

def test_dashboard_severity():
    response = client.get("/api/v1/dashboard/severity")
    assert response.status_code == 200
    data = response.json()
    assert len(data["distribution"]) > 0
    assert len(data["by_vehicle"]) > 0

def test_analytics_accidents():
    response = client.get("/api/v1/analytics/accidents?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["records"]) == 10

def test_analytics_anomalies():
    response = client.get("/api/v1/analytics/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "regional_spikes" in data

def test_analytics_forecast():
    response = client.get("/api/v1/analytics/forecast?horizon=6")
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert len(data["forecast"]) == 6

def test_auth_login_and_me():
    response = client.post("/api/v1/auth/json-login", json={
        "email": "admin@traffictrend.io",
        "password": "TrafficTrend2026!"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

    # Test me endpoint
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "admin@traffictrend.io"

def test_report_generation():
    response = client.post("/api/v1/reports/generate", json={
        "title": "Automated Test Report",
        "report_type": "executive",
        "format": "pdf"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "pdf"
    report_id = data["id"]

    # Test download
    dl_resp = client.get(f"/api/v1/reports/{report_id}/download")
    assert dl_resp.status_code == 200
    assert len(dl_resp.content) > 1000
