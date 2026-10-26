import json
import math
import os
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, ValidationError

# Load local secrets from backend/.env when run from the repository root.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(
    title="Multimodal Construction Intelligence API",
    description=(
        "Capstone prototype APIs for construction safety and crack observations, "
        "project planning, real-estate valuation, context-aware AI, daily site plans, and weather guidance."
    ),
    version="0.3.0",
)

MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}

PPEStatus = Literal["Observed", "Not observed", "Unclear", "Not applicable"]
Severity = Literal["Low", "Medium", "High", "Critical", "Unknown"]


class PPEChecklist(BaseModel):
    helmet: PPEStatus = "Unclear"
    high_visibility_vest: PPEStatus = "Unclear"
    safety_footwear: PPEStatus = "Unclear"
    safety_harness: PPEStatus = "Unclear"


class HazardItem(BaseModel):
    hazard: str = "Unspecified hazard"
    severity: Severity = "Unknown"
    corrective_remedy: str = "Ask the qualified site safety lead to review."


class SafetyAnalysisResult(BaseModel):
    safety_score: Optional[int] = Field(default=None, ge=0, le=100)
    overall_status: Literal[
        "Potential hazards visible", "No obvious hazard visible", "Unable to determine"
    ] = "Unable to determine"
    worker_positioning_and_access: str = "Not determined"
    ppe_detection: PPEChecklist = Field(default_factory=PPEChecklist)
    hazards: List[HazardItem] = Field(default_factory=list)
    recommended_ppe: List[str] = Field(default_factory=list)
    safety_guidelines: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class RiskItem(BaseModel):
    risk: str = "Unspecified risk"
    severity: Severity = "Unknown"
    mitigation: str = "Seek qualified professional review."


class CrackAnalysisResult(BaseModel):
    crack_type: Literal[
        "Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling", "Other", "Unclear"
    ] = "Unclear"
    estimated_crack_width_mm: Optional[float] = Field(default=None, ge=0)
    severity_level: Literal["Minor", "Moderate", "Severe", "Unknown"] = "Unknown"
    possible_structural_causes: List[str] = Field(default_factory=list)
    potential_risks: List[RiskItem] = Field(default_factory=list)
    recommended_repair_methods: List[str] = Field(default_factory=list)
    urgency: Literal[
        "Routine review", "Prompt professional inspection", "Immediate hazard suspected", "Unable to determine"
    ] = "Unable to determine"
    observations: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class EstimateRequest(BaseModel):
    structure_type: str = "Residential"
    built_up_area_sq_ft: float = Field(ge=0, le=10_000_000)
    assumed_cost_per_sq_ft_inr: float = Field(ge=0, le=100_000)
    completion_percent: float = Field(default=0, ge=0, le=100)
    assumed_market_value_per_sq_ft_inr: float = Field(default=0, ge=0, le=200_000)
    planning_steel_kg_per_sq_ft: float = Field(default=0, ge=0, le=100)
    planning_cement_bags_per_sq_ft: float = Field(default=0, ge=0, le=10)
    location_tier: str = "Not specified"


class ProjectPlanningRequest(BaseModel):
    project_brief: str = Field(default="", max_length=3000)
    structure_type: str = "Residential"
    city_or_location: str = "Not specified"
    built_up_area_sq_ft: float = Field(gt=0, le=10_000_000)
    floors: int = Field(default=1, ge=1, le=100)
    completion_percent: float = Field(default=0, ge=0, le=100)
    duration_weeks: int = Field(default=24, ge=1, le=520)
    cement_bags_per_sq_ft: float = Field(default=0.4, ge=0, le=5)
    sand_tons_per_sq_ft: float = Field(default=0.02, ge=0, le=1)
    aggregate_tons_per_sq_ft: float = Field(default=0.02, ge=0, le=1)
    steel_kg_per_sq_ft: float = Field(default=4.0, ge=0, le=100)
    cement_price_inr_per_bag: float = Field(default=0, ge=0, le=100_000)
    sand_price_inr_per_ton: float = Field(default=0, ge=0, le=1_000_000)
    aggregate_price_inr_per_ton: float = Field(default=0, ge=0, le=1_000_000)
    steel_price_inr_per_kg: float = Field(default=0, ge=0, le=100_000)
    labour_cost_inr_per_sq_ft: float = Field(default=0, ge=0, le=100_000)
    finishing_cost_inr_per_sq_ft: float = Field(default=0, ge=0, le=100_000)
    contingency_percent: float = Field(default=0, ge=0, le=50)


class ValuationRequest(BaseModel):
    property_location: str = Field(default="Not specified", max_length=300)
    property_type: str = Field(default="Residential", max_length=100)
    built_up_area_sq_ft: float = Field(gt=0, le=10_000_000)
    building_age_years: Optional[float] = Field(default=None, ge=0, le=500)
    amenities: List[str] = Field(default_factory=list, max_length=100)
    assumed_market_rate_per_sq_ft_inr: Optional[float] = Field(default=None, ge=0, le=2_000_000)
    estimated_monthly_rent_inr: Optional[float] = Field(default=None, ge=0, le=100_000_000)
    expected_annual_appreciation_percent: Optional[float] = Field(default=None, ge=-50, le=100)
    projection_years: int = Field(default=5, ge=1, le=100)


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    history: List[Dict[str, str]] = Field(default_factory=list)


class ContextAwareRequest(BaseModel):
    feature: Literal[
        "project_planning", "real_estate_valuation", "construction_chatbot",
        "daily_site_assistant", "weather_advisory"
    ]
    question: str = Field(min_length=1, max_length=5000)
    context: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, str]] = Field(default_factory=list)


class WeatherRequest(BaseModel):
    condition: Literal["normal", "high wind", "heavy rain", "extreme heat", "lightning", "unknown"]
    planned_activity: str = Field(default="General site work", max_length=300)
    forecast_summary: str = Field(default="", max_length=1000)
    site_notes: str = Field(default="", max_length=2000)


class DailySitePlanRequest(BaseModel):
    planned_activity: str = Field(default="General construction", min_length=1, max_length=300)
    labour_count: int = Field(default=10, ge=0, le=10000)
    shift_hours: float = Field(default=8, ge=1, le=24)
    site_condition: Literal["normal", "high wind", "heavy rain", "extreme heat", "lightning", "unknown"] = "normal"
    site_notes: str = Field(default="", max_length=2000)


class ContextAwareResult(BaseModel):
    summary: str = "No model summary available."
    observations: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


def parse_json_response(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    fence = chr(96) * 3
    if cleaned.startswith(fence):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == fence:
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else {"result": parsed}
    except json.JSONDecodeError:
        return {"model_response": cleaned}


async def read_image(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPG or PNG image.")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image is larger than the 10 MB limit.")
    return data


def gemini_image_review(
    image_data: bytes,
    mime_type: str,
    prompt: str,
    response_model: Any,
    demo_result: Dict[str, Any],
) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        safe_demo = response_model.model_validate(demo_result).model_dump()
        return {
            "mode": "demo",
            "ai_analysis_performed": False,
            "notice": "GEMINI_API_KEY is not configured; the image was accepted but no AI analysis was performed.",
            "result": safe_demo,
            "manual_review_required": True,
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=[prompt, types.Part.from_bytes(data=image_data, mime_type=mime_type)],
        )
        raw_result = parse_json_response(response.text or "")
        validated = response_model.model_validate(raw_result)
        return {
            "mode": "gemini",
            "ai_analysis_performed": True,
            "result": validated.model_dump(),
            "manual_review_required": True,
        }
    except ValidationError:
        raise HTTPException(
            status_code=502,
            detail="The AI model returned data that did not match the required JSON schema. Retry or review the image manually.",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Image-analysis service failed. Check API key, model setting, quota, and availability.",
        )


def weather_assessment(condition: str, planned_activity: str) -> Dict[str, Any]:
    activity = planned_activity.lower()
    height_or_lifting = any(term in activity for term in ("crane", "lift", "lifting", "scaffold", "height", "roof", "elevated"))
    excavation_or_concrete = any(term in activity for term in ("excavat", "trench", "foundation", "concret", "pour", "slab"))
    electrical = any(term in activity for term in ("electrical", "wiring", "power", "cable"))
    risks: List[str] = []
    precautions: List[str] = []

    if condition == "lightning":
        status = "NO-GO"
        risks.append("Lightning exposure for outdoor or elevated work.")
        precautions.extend(["Suspend exposed outdoor work.", "Follow the site shelter and emergency procedure."])
    elif condition == "high wind":
        if height_or_lifting:
            status = "NO-GO"
            risks.append("Wind-sensitive lifting or elevated work may be unsafe.")
            precautions.append("Suspend the affected task until site-specific limits and competent-person clearance permit restart.")
        else:
            status = "GO WITH CAUTION"
            risks.append("Loose materials and temporary structures may be affected by wind.")
            precautions.extend(["Secure loose materials.", "Check equipment operating limits and the site safety plan."])
    elif condition == "heavy rain":
        if excavation_or_concrete or electrical:
            status = "NO-GO"
            risks.append("Rain may affect excavation stability, concrete work, or electrical exposure.")
            precautions.append("Pause affected work until the site is assessed and conditions are controlled.")
        else:
            status = "GO WITH CAUTION"
            risks.append("Slip hazards, drainage issues, and electrical exposure.")
            precautions.extend(["Check walking surfaces and drainage.", "Keep electrical equipment protected and stop work if unsafe."])
    elif condition == "extreme heat":
        status = "GO WITH CAUTION"
        risks.append("Heat stress and dehydration.")
        precautions.extend(["Follow the heat-stress plan.", "Provide water, shade, rest breaks, and illness monitoring."])
    elif condition == "unknown":
        status = "HOLD FOR VERIFICATION"
        risks.append("Current conditions have not been verified.")
        precautions.append("Check official weather information and consult the site safety lead.")
    else:
        status = "GO SUBJECT TO SITE CHECKS"
        precautions.append("Follow the approved site safety plan and routine inspections.")

    return {
        "condition": condition,
        "planned_activity": planned_activity,
        "recommendation": status,
        "identified_risks": risks,
        "precautions": precautions,
        "notice": "Rule-based preliminary guidance only; no live weather feed is connected. Follow official alerts and site-specific stop-work authority.",
    }


def build_project_plan(payload: ProjectPlanningRequest) -> Dict[str, Any]:
    area = payload.built_up_area_sq_ft
    quantities = {
        "cement_bags_50kg": math.ceil(area * payload.cement_bags_per_sq_ft),
        "sand_tons": round(area * payload.sand_tons_per_sq_ft, 2),
        "aggregate_tons": round(area * payload.aggregate_tons_per_sq_ft, 2),
        "steel_kg": round(area * payload.steel_kg_per_sq_ft, 2),
    }
    material_costs = {
        "cement_inr": quantities["cement_bags_50kg"] * payload.cement_price_inr_per_bag,
        "sand_inr": quantities["sand_tons"] * payload.sand_price_inr_per_ton,
        "aggregate_inr": quantities["aggregate_tons"] * payload.aggregate_price_inr_per_ton,
        "steel_inr": quantities["steel_kg"] * payload.steel_price_inr_per_kg,
    }
    material_cost = sum(material_costs.values())
    labour_cost = area * payload.labour_cost_inr_per_sq_ft
    finishing_cost = area * payload.finishing_cost_inr_per_sq_ft
    subtotal = material_cost + labour_cost + finishing_cost
    contingency = subtotal * payload.contingency_percent / 100
    phases = [
        ("Planning, permits and site preparation", 0.10),
        ("Foundation and substructure", 0.20),
        ("Structure and masonry", 0.35),
        ("Electrical, plumbing and services", 0.15),
        ("Finishing, inspection and handover", 0.20),
    ]
    timeline = []
    current_week = 1.0
    for phase, fraction in phases:
        phase_weeks = round(payload.duration_weeks * fraction, 1)
        timeline.append({
            "phase": phase,
            "estimated_duration_weeks": phase_weeks,
            "start_week_approx": round(current_week, 1),
            "end_week_approx": round(current_week + phase_weeks - 0.1, 1),
        })
        current_week += phase_weeks

    cumulative_completion = 0.0
    completed_phase_count = 0
    for _, fraction in phases:
        cumulative_completion += fraction * 100
        if payload.completion_percent >= cumulative_completion:
            completed_phase_count += 1

    return {
        "project_brief": payload.project_brief,
        "structure_type": payload.structure_type,
        "city_or_location": payload.city_or_location,
        "built_up_area_sq_ft": area,
        "floors": payload.floors,
        "completion_percent": payload.completion_percent,
        "materials": quantities,
        "cost_breakdown_inr": {
            **{key: round(value, 2) for key, value in material_costs.items()},
            "materials_total": round(material_cost, 2),
            "labour": round(labour_cost, 2),
            "finishing": round(finishing_cost, 2),
            "contingency": round(contingency, 2),
            "estimated_total": round(subtotal + contingency, 2),
        },
        "timeline": timeline,
        "milestone_progress": {
            "completion_percent": payload.completion_percent,
            "completed_phase_count_estimate": completed_phase_count,
            "total_phases": len(phases),
        },
        "assumptions": [
            "Material quantities use editable user-provided per-square-foot assumptions and are illustrative only.",
            "Cost totals only include unit rates supplied in the request; a zero rate produces a zero cost for that component.",
            "Timeline durations are proportional planning estimates, not a contractor commitment.",
            "Validate quantities, rates, engineering drawings, site conditions, and local rules with qualified professionals.",
        ],
    }


def build_valuation(payload: ValuationRequest) -> Dict[str, Any]:
    area = payload.built_up_area_sq_ft
    rate = payload.assumed_market_rate_per_sq_ft_inr
    asset_value = area * rate if rate is not None else None
    annual_rent = payload.estimated_monthly_rent_inr * 12 if payload.estimated_monthly_rent_inr is not None else None
    rental_yield = None
    if asset_value and annual_rent is not None and asset_value > 0:
        rental_yield = round(annual_rent / asset_value * 100, 2)
    future_value = None
    if asset_value is not None and payload.expected_annual_appreciation_percent is not None:
        future_value = round(
            asset_value * (1 + payload.expected_annual_appreciation_percent / 100) ** payload.projection_years,
            2,
        )
    if rate is None:
        status = "market_rate_required"
    else:
        status = "user_assumption_based"
    return {
        "property_location": payload.property_location,
        "property_type": payload.property_type,
        "built_up_area_sq_ft": area,
        "building_age_years": payload.building_age_years,
        "amenities": payload.amenities,
        "assumed_market_rate_per_sq_ft_inr": rate,
        "estimated_market_value_inr": round(asset_value, 2) if asset_value is not None else None,
        "estimated_market_value_lakhs": round(asset_value / 100_000, 2) if asset_value is not None else None,
        "estimated_monthly_rent_inr": payload.estimated_monthly_rent_inr,
        "estimated_annual_rent_inr": round(annual_rent, 2) if annual_rent is not None else None,
        "gross_rental_yield_percent": rental_yield,
        "assumed_annual_appreciation_percent": payload.expected_annual_appreciation_percent,
        "projection_years": payload.projection_years,
        "projected_value_inr": future_value,
        "valuation_status": status,
        "limitations": [
            "No external live market-rate source is connected; provide a verified local rate for a useful estimate.",
            "Outputs are arithmetic estimates based on user inputs, not a professional valuation or investment advice.",
        ],
    }


def build_daily_plan(payload: DailySitePlanRequest) -> Dict[str, Any]:
    activity = payload.planned_activity.lower()
    if any(term in activity for term in ("concrete", "slab", "pour", "concreting")):
        tasks = [
            "Confirm drawings, pour sequence, formwork, reinforcement, and inspection approvals.",
            "Check concrete delivery, access route, placement equipment, and curing arrangements.",
            "Record pour start/end time and required quality checks.",
        ]
        resources = ["Approved concrete mix and delivery", "PPE", "Placement/compaction equipment", "Curing materials"]
    elif any(term in activity for term in ("excavat", "trench", "foundation")):
        tasks = [
            "Verify service locations, permits, excavation plan, and safe access.",
            "Inspect trench/excavation stability and protective systems before entry.",
            "Keep spoil and equipment clear of edges and reassess after rain.",
        ]
        resources = ["Barricades/signage", "Access ladder where required", "PPE", "Excavation inspection checklist"]
    elif any(term in activity for term in ("crane", "lifting", "lift", "scaffold", "height", "roof")):
        tasks = [
            "Review the lift/work-at-height plan, exclusion zone, and competent-person authorization.",
            "Inspect equipment, rigging, anchorage, access, and required fall protection.",
            "Stop the task if weather, equipment limits, or site conditions are unsafe.",
        ]
        resources = ["Approved lifting/height-work equipment", "Inspection records", "PPE", "Barricades"]
    else:
        tasks = [
            "Conduct the site briefing and verify today's approved work sequence.",
            "Inspect the work area, access, tools, materials, and required permits.",
            "Assign responsibilities, record progress, and report changed hazards.",
        ]
        resources = ["Task-specific materials", "PPE", "Tools/equipment inspection checklist", "Daily work permit where required"]

    weather = weather_assessment(payload.site_condition, payload.planned_activity)
    safety_checks = [
        "Confirm task-specific PPE and safe access before work starts.",
        "Check housekeeping, emergency access, first aid and communications.",
        "Brief the crew on hazards, controls, and stop-work escalation.",
    ]
    if payload.site_condition == "extreme heat":
        safety_checks.append("Plan drinking water, shade, rest breaks, and heat-illness monitoring.")
    if payload.site_condition in {"heavy rain", "lightning"}:
        safety_checks.append("Verify site condition before restart and follow official alerts.")
    return {
        "planned_activity": payload.planned_activity,
        "labour_count": payload.labour_count,
        "shift_hours": payload.shift_hours,
        "site_condition": payload.site_condition,
        "execution_recommendation": weather["recommendation"],
        "tasks": tasks,
        "required_materials_and_equipment": resources,
        "safety_checks": safety_checks,
        "potential_risk_alerts": weather["identified_risks"],
        "weather_precautions": weather["precautions"],
        "site_notes": payload.site_notes,
        "limitations": ["Planning aid only; confirm the method statement, permits, site rules, and competent-person instructions."],
    }


FEATURE_INSTRUCTIONS = {
    "project_planning": "Create a practical, high-level construction project plan using only supplied assumptions. Highlight unknown material rates and schedule uncertainty.",
    "real_estate_valuation": "Discuss property valuation inputs and calculation limitations. Never invent local market prices; distinguish user assumptions from verified data.",
    "construction_chatbot": "Answer general construction documentation questions clearly. Do not certify safety or structural integrity.",
    "daily_site_assistant": "Produce a concise daily action plan, materials/equipment, safety checks, and risk alerts from the context.",
    "weather_advisory": "Provide cautious weather-sensitive work guidance. Do not claim live weather is available.",
}


def contextual_groq_response(feature: str, question: str, context: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return {
            "mode": "demo",
            "feature": feature,
            "result": {
                "summary": f"Demo response for {feature.replace('_', ' ')}. No AI model call was made because GROQ_API_KEY is not configured.",
                "observations": [f"Received context keys: {', '.join(sorted(context.keys()))}" if context else "No structured context was supplied."],
                "risks": [],
                "recommendations": ["Configure GROQ_API_KEY to enable model-based reasoning.", "Verify any safety-critical decision with a qualified professional."],
                "next_steps": ["Review inputs and assumptions.", "Use the feature-specific API for deterministic calculations where available."],
                "limitations": ["Demonstration fallback; this is not a generated AI assessment."],
            },
            "ai_analysis_performed": False,
        }

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        messages: List[Dict[str, str]] = [{
            "role": "system",
            "content": (
                "You are a construction-domain decision-support assistant. " + FEATURE_INSTRUCTIONS[feature] +
                " Return only a JSON object with keys summary (string), observations (array of strings), risks "
                "(array of strings), recommendations (array of strings), next_steps (array of strings), and "
                "limitations (array of strings). Explicitly identify missing information. Do not represent "
                "assumptions as verified facts and do not replace a licensed/qualified professional."
            ),
        }]
        for item in history[-8:]:
            role = item.get("role", "")
            item_content = item.get("content", "")
            if role in {"user", "assistant"} and item_content:
                messages.append({"role": role, "content": item_content[:4000]})
        messages.append({
            "role": "user",
            "content": json.dumps({"question": question, "context": context}, ensure_ascii=False),
        })
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=0.2,
        )
        parsed = parse_json_response(response.choices[0].message.content or "")
        validated = ContextAwareResult.model_validate(parsed)
        return {
            "mode": "groq",
            "feature": feature,
            "result": validated.model_dump(),
            "ai_analysis_performed": True,
        }
    except ValidationError:
        raise HTTPException(status_code=502, detail="AI response failed the required JSON data contract.")
    except Exception:
        raise HTTPException(status_code=502, detail="AI assistant failed. Check the Groq API key, model, quota, and availability.")


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "name": "Multimodal Construction Intelligence API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "mode": "gemini-enabled" if os.getenv("GEMINI_API_KEY") else "demo",
    }


@app.post("/api/estimate")
def estimate_project(payload: EstimateRequest) -> Dict[str, Any]:
    area = payload.built_up_area_sq_ft
    total = area * payload.assumed_cost_per_sq_ft_inr
    incurred = total * payload.completion_percent / 100
    asset_value = area * payload.assumed_market_value_per_sq_ft_inr
    return {
        "structure_type": payload.structure_type,
        "built_up_area_sq_ft": area,
        "location_tier": payload.location_tier,
        "completion_percent": payload.completion_percent,
        "indicative_total_budget_inr": round(total, 2),
        "indicative_cost_incurred_inr": round(incurred, 2),
        "indicative_remaining_budget_inr": round(total - incurred, 2),
        "indicative_asset_value_inr": round(asset_value, 2),
        "planning_steel_kg": round(area * payload.planning_steel_kg_per_sq_ft, 2),
        "planning_cement_bags_50kg": round(area * payload.planning_cement_bags_per_sq_ft, 2),
        "notice": "Estimates use user-provided assumptions; they are not professional valuation or bill-of-quantities figures.",
    }


@app.post("/api/project-planning")
def project_planning(payload: ProjectPlanningRequest) -> Dict[str, Any]:
    return build_project_plan(payload)


@app.post("/api/real-estate-valuation")
def real_estate_valuation(payload: ValuationRequest) -> Dict[str, Any]:
    return build_valuation(payload)


@app.post("/api/context-aware-reasoning")
def context_aware_reasoning(payload: ContextAwareRequest) -> Dict[str, Any]:
    return contextual_groq_response(payload.feature, payload.question, payload.context, payload.history)


@app.post("/api/daily-site-assistant")
def daily_site_assistant(payload: DailySitePlanRequest) -> Dict[str, Any]:
    result = build_daily_plan(payload)
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if api_key:
        # Optional AI enrichment; keep deterministic site plan if model is unavailable.
        question = "Review this daily plan and add concise construction-specific observations, risks, and next steps."
        try:
            enrichment = contextual_groq_response(
                "daily_site_assistant",
                question,
                result,
                [],
            )
            result["ai_enrichment"] = enrichment
        except HTTPException as exc:
            result["ai_enrichment"] = {"mode": "unavailable", "notice": exc.detail}
    else:
        result["ai_enrichment"] = {
            "mode": "demo",
            "notice": "Deterministic daily plan returned; set GROQ_API_KEY for optional AI enrichment.",
        }
    return result


@app.post("/api/ai/query")
async def unified_ai_query(
    feature: str = Form(...),
    question: str = Form(default=""),
    context_json: str = Form(default="{}"),
    file: Optional[UploadFile] = File(default=None),
) -> Dict[str, Any]:
    allowed = {
        "site_safety", "crack_analysis", "project_planning", "real_estate_valuation",
        "construction_chatbot", "daily_site_assistant", "weather_advisory",
    }
    if feature not in allowed:
        raise HTTPException(status_code=422, detail=f"feature must be one of: {', '.join(sorted(allowed))}")
    try:
        context = json.loads(context_json or "{}")
        if not isinstance(context, dict):
            raise ValueError("context must be a JSON object")
    except ValueError:
        raise HTTPException(status_code=422, detail="context_json must be a valid JSON object.")
    if file is not None:
        image_data = await read_image(file)
        if feature not in {"site_safety", "crack_analysis"}:
            raise HTTPException(status_code=422, detail="Image input is currently supported for site_safety and crack_analysis.")
        if feature == "site_safety":
            prompt = (
                "Return JSON with safety_score (0-100 or null), overall_status, worker_positioning_and_access, "
                "ppe_detection, hazards (hazard/severity/corrective_remedy), recommended_ppe, safety_guidelines, "
                "limitations. Do not certify site safety or compliance; require qualified human review. "
                f"User question/context: {question}\nContext JSON: {json.dumps(context, ensure_ascii=False)}"
            )
            demo_result = SafetyAnalysisResult().model_dump()
            result = gemini_image_review(image_data, file.content_type or "image/jpeg", prompt, SafetyAnalysisResult, demo_result)
        else:
            prompt = (
                "Return JSON with crack_type, estimated_crack_width_mm, severity_level, possible_structural_causes, "
                "potential_risks (risk/severity/mitigation), recommended_repair_methods, urgency, observations, limitations. "
                "Do not diagnose structural integrity. Require qualified engineer review. "
                f"User question/context: {question}\nContext JSON: {json.dumps(context, ensure_ascii=False)}"
            )
            demo_result = CrackAnalysisResult().model_dump()
            result = gemini_image_review(image_data, file.content_type or "image/jpeg", prompt, CrackAnalysisResult, demo_result)
        return {"feature": feature, "result": result}
    return contextual_groq_response(
        feature if feature not in {"site_safety", "crack_analysis"} else "construction_chatbot",
        question or "Please review the supplied structured context.",
        context,
        [],
    )


@app.post("/api/site-safety")
async def analyze_site_safety(
    file: UploadFile = File(...),
    context: str = Form(default="", description="Optional text about site context or observed conditions."),
) -> Dict[str, Any]:
    image_data = await read_image(file)
    prompt = f"""
You are supporting a construction-site documentation prototype. Review the attached construction-site image conservatively.
Optional user context: {context or "No context supplied."}
Return valid JSON with these keys: safety_score (integer 0-100, or null if photo is insufficient),
overall_status ("Potential hazards visible", "No obvious hazard visible", or "Unable to determine"),
worker_positioning_and_access (string), ppe_detection (object with helmet, high_visibility_vest,
safety_footwear, safety_harness; each value "Observed", "Not observed", "Unclear", or "Not applicable"),
hazards (array of objects with hazard, severity "Low"/"Medium"/"High"/"Critical"/"Unknown", corrective_remedy),
recommended_ppe (array), safety_guidelines (array), limitations (array).
Do not certify OSHA/IS 456 compliance or site safety. Absence from one image does not prove an item is absent.
Require qualified human review.
"""
    demo = SafetyAnalysisResult(
        worker_positioning_and_access="Not assessed in demo mode; no AI vision analysis was run.",
        safety_guidelines=["Have a qualified site safety reviewer inspect the photograph and site."],
        limitations=["Configure GEMINI_API_KEY to enable AI image analysis.", "This is a schema fallback, not an image finding."],
    ).model_dump()
    return gemini_image_review(image_data, file.content_type or "image/jpeg", prompt, SafetyAnalysisResult, demo)


@app.post("/api/crack-analysis")
async def analyze_crack(
    file: UploadFile = File(...),
    context: str = Form(default="", description="Optional context such as building age, recent movement, or water ingress."),
) -> Dict[str, Any]:
    image_data = await read_image(file)
    prompt = f"""
Review the attached wall/concrete image conservatively. Context: {context or "No context supplied."}
Return valid JSON with crack_type (Hairline/Settlement/Structural Shear/Thermal Expansion/Spalling/Other/Unclear),
estimated_crack_width_mm (number or null; use null without a scale), severity_level (Minor/Moderate/Severe/Unknown),
possible_structural_causes (array of hypotheses), potential_risks (array of risk/severity/mitigation objects),
recommended_repair_methods (options for a qualified engineer to assess), urgency
(Routine review/Prompt professional inspection/Immediate hazard suspected/Unable to determine), observations, limitations.
Do not assert that the structure is safe or diagnose structural integrity from a photograph.
"""
    demo = CrackAnalysisResult(
        observations=["No AI image review was run in demo mode."],
        limitations=["Configure GEMINI_API_KEY to enable AI image analysis.", "A photograph alone cannot establish structural integrity."],
    ).model_dump()
    return gemini_image_review(image_data, file.content_type or "image/jpeg", prompt, CrackAnalysisResult, demo)


@app.post("/api/site-assistant")
def site_assistant(payload: AssistantRequest) -> Dict[str, Any]:
    # Retained compatibility route for the original chatbot activity.
    result = contextual_groq_response(
        "construction_chatbot",
        payload.question,
        {},
        payload.history,
    )
    if result.get("mode") == "demo":
        return {
            "mode": "demo",
            "answer": result["result"]["summary"],
            "result": result["result"],
        }
    return {
        "mode": result["mode"],
        "answer": result["result"]["summary"],
        "result": result["result"],
    }


@app.post("/api/weather-advisory")
def weather_advisory(payload: WeatherRequest) -> Dict[str, Any]:
    result = weather_assessment(payload.condition, payload.planned_activity)
    result["forecast_summary_supplied_by_user"] = payload.forecast_summary
    result["site_notes"] = payload.site_notes
    return result
