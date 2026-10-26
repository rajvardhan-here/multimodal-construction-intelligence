import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="Multimodal Construction Intelligence API",
    description="Prototype endpoints for safety observations, crack review, estimates, weather guidance, and a site assistant.",
    version="0.1.0",
)

MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}


class EstimateRequest(BaseModel):
    structure_type: str = "Residential"
    built_up_area_sq_ft: float = Field(ge=0, le=10_000_000)
    assumed_cost_per_sq_ft_inr: float = Field(ge=0, le=100_000)
    completion_percent: float = Field(default=0, ge=0, le=100)
    assumed_market_value_per_sq_ft_inr: float = Field(default=0, ge=0, le=200_000)
    planning_steel_kg_per_sq_ft: float = Field(default=0, ge=0, le=100)
    planning_cement_bags_per_sq_ft: float = Field(default=0, ge=0, le=10)
    location_tier: str = "Not specified"


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    history: List[Dict[str, str]] = Field(default_factory=list)


class WeatherRequest(BaseModel):
    condition: str


def parse_json_response(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    try:
        result = json.loads(cleaned)
        return result if isinstance(result, dict) else {"result": result}
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


def gemini_image_review(image_data: bytes, mime_type: str, prompt: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {
            "mode": "demo",
            "notice": "GEMINI_API_KEY is not configured. No AI image analysis was performed.",
            "manual_review_required": True,
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=[prompt, types.Part.from_bytes(data=image_data, mime_type=mime_type)],
        )
        return {
            "mode": "gemini",
            "result": parse_json_response(response.text or ""),
            "manual_review_required": True,
        }
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Image-analysis service failed. Check API key, model setting, quota, and availability.",
        )


@app.get("/")
def root() -> Dict[str, str]:
    return {"name": "Multimodal Construction Intelligence API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "mode": "gemini-enabled" if os.getenv("GEMINI_API_KEY") else "demo"}


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


@app.post("/api/site-safety")
async def analyze_site_safety(file: UploadFile = File(...)) -> Dict[str, Any]:
    image_data = await read_image(file)
    prompt = """
Review the construction-site image conservatively. Return a JSON object with:
safety_score (0-100 or null), overall_status, ppe_detection (helmet, high_visibility_vest,
safety_footwear, safety_harness values Observed/Not observed/Unclear/Not applicable),
hazards (array of objects with hazard, severity Low/Medium/High/Critical/Unknown, and corrective_remedy),
observations (array), limitations (array). Do not claim code compliance or certify safety.
Explain uncertainty and require qualified human review.
"""
    return gemini_image_review(image_data, file.content_type or "image/jpeg", prompt)


@app.post("/api/crack-analysis")
async def analyze_crack(file: UploadFile = File(...)) -> Dict[str, Any]:
    image_data = await read_image(file)
    prompt = """
Review this wall/concrete image conservatively. Return JSON with defect_type (Hairline, Settlement,
Structural Shear, Thermal Expansion, Spalling, Other, or Unclear), estimated_crack_width_mm (number or null;
use null if no visible scale), root_causes (hypotheses array), recommended_engineering_repairs (options for
a qualified engineer to assess, not instructions), urgency, observations, and limitations. Do not diagnose
structural safety or claim the structure is safe.
"""
    return gemini_image_review(image_data, file.content_type or "image/jpeg", prompt)


@app.post("/api/site-assistant")
def site_assistant(payload: AssistantRequest) -> Dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return {
            "mode": "demo",
            "answer": "Demo mode: set GROQ_API_KEY in the local backend/.env file for model responses. For safety-critical decisions, consult a qualified site safety lead or engineer.",
        }

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        messages: List[Dict[str, str]] = [{
            "role": "system",
            "content": (
                "You are a cautious construction documentation assistant. Provide general information only. "
                "Do not certify safety or structural integrity or replace qualified professionals. "
                "Follow site-specific procedures and official alerts."
            ),
        }]
        for item in payload.history[-8:]:
            role = item.get("role", "")
            item_content = item.get("content", "")
            if role in {"user", "assistant"} and item_content:
                messages.append({"role": role, "content": item_content[:4000]})
        messages.append({"role": "user", "content": payload.question})
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=0.2,
        )
        return {"mode": "groq", "answer": response.choices[0].message.content or ""}
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Assistant service failed. Check Groq API key, model setting, quota, and availability.",
        )


@app.post("/api/weather-advisory")
def weather_advisory(payload: WeatherRequest) -> Dict[str, str]:
    guidance = {
        "normal": "Follow the approved site safety plan and routine checks.",
        "high wind": "Follow equipment limits and site rules; pause lifting or work-at-height activities when required.",
        "heavy rain": "Check slips, excavation stability, drainage, and electrical exposure. Stop affected work if unsafe.",
        "extreme heat": "Follow the heat-stress plan, including hydration, shade, rest breaks, and symptom monitoring.",
        "lightning": "Suspend exposed work and follow the site's shelter and emergency procedures.",
        "unknown": "Check official weather information and consult the site safety lead before weather-dependent work.",
    }
    key = payload.condition.strip().lower()
    if key not in guidance:
        raise HTTPException(
            status_code=422,
            detail="Choose normal, high wind, heavy rain, extreme heat, lightning, or unknown.",
        )
    return {
        "condition": key,
        "guidance": guidance[key],
        "notice": "General guidance only; this API does not fetch live weather or replace official alerts.",
    }
