import base64
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

# Small PNG payload used only to exercise request validation and the demo fallback.
TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/5s8AAAAASUVORK5CYII="
)


def test_health_reports_ok_in_demo_mode(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["mode"] == "demo"


def test_estimate_calculates_expected_values():
    response = client.post(
        "/api/estimate",
        json={
            "structure_type": "Residential",
            "built_up_area_sq_ft": 1000,
            "assumed_cost_per_sq_ft_inr": 2000,
            "completion_percent": 25,
            "assumed_market_value_per_sq_ft_inr": 3000,
            "planning_steel_kg_per_sq_ft": 4,
            "planning_cement_bags_per_sq_ft": 0.4,
            "location_tier": "Tier 2",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["indicative_total_budget_inr"] == 2_000_000
    assert payload["indicative_cost_incurred_inr"] == 500_000
    assert payload["indicative_remaining_budget_inr"] == 1_500_000
    assert payload["indicative_asset_value_inr"] == 3_000_000
    assert payload["planning_steel_kg"] == 4000
    assert payload["planning_cement_bags_50kg"] == 400


def test_project_planning_has_materials_costs_and_timeline():
    response = client.post(
        "/api/project-planning",
        json={
            "project_brief": "Small residential home",
            "structure_type": "Residential",
            "city_or_location": "Indore",
            "built_up_area_sq_ft": 1000,
            "floors": 2,
            "completion_percent": 35,
            "duration_weeks": 24,
            "cement_bags_per_sq_ft": 0.4,
            "sand_tons_per_sq_ft": 0.02,
            "aggregate_tons_per_sq_ft": 0.02,
            "steel_kg_per_sq_ft": 4,
            "cement_price_inr_per_bag": 400,
            "sand_price_inr_per_ton": 2000,
            "aggregate_price_inr_per_ton": 1500,
            "steel_price_inr_per_kg": 60,
            "labour_cost_inr_per_sq_ft": 500,
            "finishing_cost_inr_per_sq_ft": 300,
            "contingency_percent": 10,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["materials"]["cement_bags_50kg"] == 400
    assert payload["materials"]["sand_tons"] == 20
    assert payload["materials"]["steel_kg"] == 4000
    assert payload["cost_breakdown_inr"]["estimated_total"] > 0
    assert len(payload["timeline"]) == 5
    assert payload["milestone_progress"]["completion_percent"] == 35
    assert "illustrative only" in " ".join(payload["assumptions"])


def test_real_estate_valuation_requires_market_rate_for_value():
    response = client.post(
        "/api/real-estate-valuation",
        json={
            "property_location": "Indore",
            "property_type": "Residential",
            "built_up_area_sq_ft": 1000,
            "building_age_years": 5,
            "amenities": ["Parking"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["valuation_status"] == "market_rate_required"
    assert payload["estimated_market_value_inr"] is None


def test_real_estate_valuation_calculates_user_assumptions():
    response = client.post(
        "/api/real-estate-valuation",
        json={
            "property_location": "Indore",
            "property_type": "Residential",
            "built_up_area_sq_ft": 1000,
            "assumed_market_rate_per_sq_ft_inr": 3000,
            "estimated_monthly_rent_inr": 15000,
            "expected_annual_appreciation_percent": 5,
            "projection_years": 5,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["estimated_market_value_inr"] == 3_000_000
    assert payload["estimated_annual_rent_inr"] == 180_000
    assert payload["gross_rental_yield_percent"] == 6


def test_weather_advisory_returns_activity_aware_decision():
    response = client.post(
        "/api/weather-advisory",
        json={"condition": "high wind", "planned_activity": "crane lifting"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendation"] == "NO-GO"
    assert payload["identified_risks"]
    assert payload["precautions"]


def test_weather_invalid_condition_is_rejected():
    response = client.post(
        "/api/weather-advisory",
        json={"condition": "snowstorm"},
    )
    assert response.status_code == 422


def test_daily_site_assistant_generates_plan_in_demo_mode(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post(
        "/api/daily-site-assistant",
        json={
            "planned_activity": "Concreting",
            "labour_count": 10,
            "shift_hours": 8,
            "site_condition": "heavy rain",
            "site_notes": "Rain forecast supplied by site supervisor",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["execution_recommendation"] == "NO-GO"
    assert payload["tasks"]
    assert payload["safety_checks"]
    assert payload["ai_enrichment"]["mode"] == "demo"


def test_context_aware_query_returns_contract_in_demo_mode(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post(
        "/api/context-aware-reasoning",
        json={
            "feature": "project_planning",
            "question": "Summarize the key risks",
            "context": {"built_up_area_sq_ft": 1000, "city": "Indore"},
            "history": [],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["feature"] == "project_planning"
    assert set(payload["result"]) >= {
        "summary", "observations", "risks", "recommendations", "next_steps", "limitations"
    }


def test_chatbot_demo_fallback(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post(
        "/api/site-assistant",
        json={"question": "Explain site preparation", "history": []},
    )
    assert response.status_code == 200
    assert response.json()["mode"] == "demo"
    assert "answer" in response.json()


def test_site_safety_image_returns_schema_and_discloses_demo(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post(
        "/api/site-safety",
        files={"file": ("site.png", TINY_PNG, "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["ai_analysis_performed"] is False
    assert payload["result"]["safety_score"] is None
    assert "helmet" in payload["result"]["ppe_detection"]


def test_crack_analysis_image_returns_schema_and_discloses_demo(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post(
        "/api/crack-analysis",
        files={"file": ("crack.png", TINY_PNG, "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["ai_analysis_performed"] is False
    assert payload["result"]["crack_type"] == "Unclear"


def test_image_endpoint_rejects_wrong_media_type():
    response = client.post(
        "/api/site-safety",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_image_endpoint_rejects_missing_file():
    response = client.post("/api/site-safety", data={"context": "no image"})
    assert response.status_code == 422



def test_unified_ai_query_returns_feature_context_in_demo_mode(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    response = client.post(
        "/api/ai/query",
        data={
            "feature": "real_estate_valuation",
            "question": "Summarize the limits in this estimate",
            "context_json": '{"area_sq_ft": 1000, "market_rate": null}',
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["feature"] == "real_estate_valuation"
    assert payload["mode"] == "demo"
    assert payload["result"]["limitations"]


def test_unified_ai_query_requires_image_for_visual_features():
    response = client.post(
        "/api/ai/query",
        data={"feature": "site_safety", "question": "Review PPE", "context_json": "{}"},
    )
    assert response.status_code == 422



def test_streamlit_app_renders_in_demo_mode(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    from streamlit.testing.v1 import AppTest

    app_test = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=20).run()
    assert len(app_test.exception) == 0
    assert any("Multimodal Construction Intelligence Platform" in title.value for title in app_test.title)
