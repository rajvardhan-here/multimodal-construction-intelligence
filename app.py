import json
import re
from datetime import datetime

import streamlit as st

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GENAI_AVAILABLE = False

st.set_page_config(
    page_title="Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ Multimodal Construction Intelligence Platform")
st.caption("AI-assisted construction safety • Crack observations • Cost estimation • Weather-aware guidance")
st.info(
    "Capstone prototype. AI findings are preliminary and can be wrong. "
    "They are not a substitute for a qualified structural engineer, safety officer, or official weather alerts."
)

with st.sidebar:
    st.header("AI configuration")
    api_key = st.text_input(
        "Google Gemini API key (optional)",
        type="password",
        help="Used only in this app session. Do not paste your key into source code or GitHub.",
    )
    model_name = st.text_input("Gemini model", value="gemini-3.8-flash")
    pollinations_key = st.text_input(
        "Pollinations API key (optional)",
        type="password",
        help="Used only for a render request during this session. Never commit API keys to GitHub.",
    )
    st.caption("Without Gemini key, image analysis stays in demo/manual mode. Without Pollinations key, use the generated render prompt only.")
    st.divider()
    st.markdown("**Project:** Skill Wallet Capstone")
    st.markdown("**Stack:** Python · Streamlit · Gemini API (optional)")

if "report" not in st.session_state:
    st.session_state.report = {
        "generated_at": None,
        "safety_analysis": {},
        "crack_analysis": {},
        "project_estimate": {},
        "real_estate_valuation": {},
        "daily_site_plan": {},
        "weather_advisory": {},
        "assistant_notes": [],
    }

def parse_json_response(text):
    text = text.strip()
    text = re.sub(r"^\`\`\`(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\`\`\`$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"model_response": text}

def analyze_image(prompt, uploaded_file):
    if uploaded_file is None:
        return {
            "mode": "not_run",
            "notice": "Upload an image before requesting image analysis.",
            "manual_review_required": True,
        }
    if not api_key:
        return {
            "mode": "demonstration",
            "notice": "No Gemini API key supplied; no AI image analysis was run.",
            "manual_review_required": True,
        }
    if not GENAI_AVAILABLE:
        return {
            "mode": "unavailable",
            "error": "Google Gen AI SDK is not installed. Install requirements.txt and redeploy.",
        }
    try:
        client = genai.Client(api_key=api_key)
        contents = [prompt]
        if uploaded_file is not None:
            mime = uploaded_file.type or "image/jpeg"
            contents.append(types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=mime))
        response = client.models.generate_content(model=model_name.strip() or "gemini-3.8-flash", contents=contents)
        return {
            "mode": "gemini",
            "model": model_name.strip() or "gemini-3.8-flash",
            "result": parse_json_response(response.text or ""),
            "manual_review_required": True,
        }
    except Exception as exc:
        return {
            "mode": "error",
            "error": str(exc),
            "manual_review_required": True,
        }

def image_prompt(domain, extra_rules):
    if any(term in domain.lower() for term in ("safety", "ppe", "hazard")):
        schema = """
Return a JSON object with these keys:
safety_score (integer 0-100, or null if the photo is insufficient),
overall_status (one of "Potential hazards visible", "No obvious hazard visible", "Unable to determine"),
ppe_detection (object with helmet, high_visibility_vest, safety_footwear, safety_harness; each value must be "Observed", "Not observed", "Unclear", or "Not applicable"),
hazards (array of objects, each with hazard, severity [Low/Medium/High/Critical/Unknown], and corrective_remedy),
observations (array of strings), limitations (array of strings).
Score only the visible evidence and explain uncertainty. Do not state that the site complies with OSHA or IS 456; this image review cannot certify compliance.
"""
    else:
        schema = """
Return a JSON object with these keys:
defect_type (one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, Other, or Unclear),
estimated_crack_width_mm (number or null; use null unless a scale is clearly visible),
root_causes (array of possible causes, clearly marked as hypotheses),
recommended_engineering_repairs (array of options for a qualified engineer to evaluate, not definitive instructions),
urgency (one of Routine review, Prompt professional inspection, Immediate hazard suspected, or Unable to determine),
observations (array of strings), limitations (array of strings).
Do not diagnose structural integrity or claim that a structure is safe.
"""
    return f"""
You are assisting with a construction-site documentation capstone prototype.
Task: {domain}
Analyze the attached image conservatively. Do not claim certainty when details are unclear.
Do not certify structural integrity, occupational safety, OSHA compliance, or compliance with Indian construction codes.
Do not make a final safety-critical decision. Recommend qualified human inspection for potentially dangerous findings.
{schema}
{extra_rules}
"""

safety_tab, crack_tab, estimate_tab, valuation_tab, daily_plan_tab, weather_tab, assistant_tab, report_tab = st.tabs(
    [
        "Site Safety & PPE", "Crack Diagnostics", "Project Estimator", "Real Estate Valuation",
        "Daily Site Plan", "Weather Advisory", "Site Assistant", "JSON Report"
    ]
)

with safety_tab:
    st.subheader("Multimodal Site Safety & PPE Audit")
    safety_photo = st.file_uploader("Upload a construction-site image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="safety_photo")
    if safety_photo:
        st.image(safety_photo, caption="Uploaded site image", use_container_width=True)
    st.write("**Manual PPE checklist**")
    ppe = {}
    cols = st.columns(2)
    checklist = [
        ("Helmet / hard hat", cols[0]),
        ("High-visibility vest", cols[1]),
        ("Safety footwear", cols[0]),
        ("Harness where required", cols[1]),
    ]
    for label, col in checklist:
        with col:
            ppe[label] = st.selectbox(label, ["Not reviewed", "Observed", "Not observed", "Not applicable"], key="ppe_" + label)
    hazards_text = st.text_area("Potential hazards observed by reviewer (one per line)", key="hazards_text")
    if st.button("Analyze site safety image", type="primary"):
        prompt = image_prompt(
            "Review construction site safety, PPE, and visible hazards in the construction site image.",
            "Include a ppe_observations object when possible. Mention that absence in an image does not prove an item is absent on site.",
        )
        with st.spinner("Reviewing image or preparing demo result..."):
            result = analyze_image(prompt, safety_photo)
        st.session_state.report["safety_analysis"] = {
            "image_filename": safety_photo.name if safety_photo else None,
            "manual_ppe_checklist": ppe,
            "reviewer_reported_hazards": [line.strip() for line in hazards_text.splitlines() if line.strip()],
            "ai_result": result,
        }
        payload = result.get("result", {}) if isinstance(result, dict) else {}
        if isinstance(payload, dict):
            score = payload.get("safety_score")
            status = payload.get("overall_status")
            c1, c2, c3 = st.columns(3)
            c1.metric("Preliminary safety score", f"{score}/100" if isinstance(score, (int, float)) else "Not available")
            c2.metric("Image review status", str(status or result.get("mode", "Not determined")))
            hazard_list = payload.get("hazards", [])
            c3.metric("Potential hazards listed", len(hazard_list) if isinstance(hazard_list, list) else 0)
            if isinstance(hazard_list, list) and hazard_list:
                st.markdown("**Potential hazards and suggested follow-up**")
                for item in hazard_list:
                    if isinstance(item, dict):
                        st.warning(
                            f"{item.get('severity', 'Unknown')}: {item.get('hazard', 'Unspecified hazard')} — "
                            f"{item.get('corrective_remedy', 'Ask the site safety lead to review.')}"
                        )
            ppe_findings = payload.get("ppe_detection")
            if isinstance(ppe_findings, dict) and ppe_findings:
                st.markdown("**AI PPE observations**")
                st.json(ppe_findings, expanded=True)
        st.json(result, expanded=True)
        st.success("Safety observations saved to the report. Human review is still required.")

with crack_tab:
    st.subheader("Crack Diagnostics & Structural Integrity (Preliminary)")
    crack_photo = st.file_uploader("Upload wall/concrete surface image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="crack_photo")
    if crack_photo:
        st.image(crack_photo, caption="Uploaded surface image", use_container_width=True)
    st.warning("Image-based estimates cannot establish structural safety. For growing, wide, diagonal, leaking, or displaced cracks, consult a qualified structural engineer.")
    crack_notes = st.text_area("Known context (age of building, recent changes, water ingress, etc.)")
    if st.button("Analyze crack image", type="primary"):
        prompt = image_prompt(
            "Describe visible cracks or surface defects in this concrete/wall image.",
            "Do not estimate an exact crack width from a photo unless a scale is clearly available. Never prescribe a repair as definitive; state that an engineer must determine the cause and repair.",
        ) + "\nContext supplied by user: " + (crack_notes or "None supplied")
        with st.spinner("Reviewing surface image or preparing demo result..."):
            result = analyze_image(prompt, crack_photo)
        st.session_state.report["crack_analysis"] = {
            "image_filename": crack_photo.name if crack_photo else None,
            "user_context": crack_notes,
            "ai_result": result,
        }
        payload = result.get("result", {}) if isinstance(result, dict) else {}
        if isinstance(payload, dict):
            c1, c2 = st.columns(2)
            c1.metric("Observed defect category", str(payload.get("defect_type", "Not determined")))
            c2.metric("Suggested urgency", str(payload.get("urgency", "Not determined")))
            width = payload.get("estimated_crack_width_mm")
            st.metric("Estimated width (mm)", str(width) if width is not None else "Not estimated")
            for label, key in [
                ("Possible causes (hypotheses)", "root_causes"),
                ("Options for engineer review", "recommended_engineering_repairs"),
                ("Visible observations", "observations"),
                ("Uncertainty / limitations", "limitations"),
            ]:
                values = payload.get(key)
                if isinstance(values, list) and values:
                    st.markdown(f"**{label}**")
                    for value in values:
                        st.write(f"• {value}")
        st.json(result, expanded=True)
        st.success("Preliminary observations saved. Not an engineering diagnosis.")

with estimate_tab:
    st.subheader("Planning & Indicative Real Estate/Construction Estimate")
    structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial", "Other"])
    area_sqft = st.number_input("Built-up area (sq ft)", min_value=0, max_value=10000000, value=1000, step=100)
    cost_rate = st.number_input("Assumed construction cost per sq ft (INR)", min_value=0, max_value=100000, value=2000, step=100)
    completion = st.slider("Completion percentage", 0, 100, 0)
    city_tier = st.selectbox("Indian city tier", ["Tier 1", "Tier 2", "Tier 3", "Not specified"])
    market_rate = st.number_input("Assumed local market value per sq ft (INR)", min_value=0, max_value=200000, value=3000, step=100)
    steel_kg_per_sqft = st.number_input("Planning assumption: steel (kg/sq ft)", min_value=0.0, max_value=100.0, value=4.0, step=0.5)
    cement_bags_per_sqft = st.number_input("Planning assumption: cement (50 kg bags/sq ft)", min_value=0.0, max_value=10.0, value=0.4, step=0.05)
    total = area_sqft * cost_rate
    incurred = total * completion / 100
    remaining = total - incurred
    estimated_asset_value = area_sqft * market_rate
    steel_kg = area_sqft * steel_kg_per_sqft
    cement_bags = area_sqft * cement_bags_per_sqft
    m1, m2, m3 = st.columns(3)
    m1.metric("Indicative total budget", f"₹{total:,.0f}")
    m2.metric("Indicative incurred cost", f"₹{incurred:,.0f}")
    m3.metric("Indicative remaining budget", f"₹{remaining:,.0f}")
    st.progress(completion / 100, text=f"Milestone / completion progress: {completion}%")
    v1, v2, v3 = st.columns(3)
    v1.metric("Indicative asset value", f"₹{estimated_asset_value / 100000:.2f} lakh" if estimated_asset_value < 10000000 else f"₹{estimated_asset_value / 10000000:.2f} crore")
    v2.metric("Planning steel quantity", f"{steel_kg:,.0f} kg")
    v3.metric("Planning cement quantity", f"{cement_bags:,.0f} bags")
    st.caption("Market value and material quantities are planning estimates based only on your editable assumptions—not verified market data, an engineer's bill of quantities, or a professional valuation.")
    if st.button("Save project estimate"):
        st.session_state.report["project_estimate"] = {
            "structure_type": structure,
            "built_up_area_sq_ft": area_sqft,
            "assumed_construction_cost_per_sq_ft_inr": cost_rate,
            "completion_percent": completion,
            "location_tier": city_tier,
            "assumed_market_value_per_sq_ft_inr": market_rate,
            "indicative_total_budget_inr": total,
            "indicative_cost_incurred_inr": incurred,
            "indicative_remaining_budget_inr": remaining,
            "indicative_asset_value_inr": estimated_asset_value,
            "planning_steel_kg_per_sq_ft": steel_kg_per_sqft,
            "indicative_steel_kg": steel_kg,
            "planning_cement_bags_per_sq_ft": cement_bags_per_sqft,
            "indicative_cement_bags_50kg": cement_bags,
            "assumptions_notice": "User-provided assumptions; not a market quote, professional valuation, or verified material schedule.",
        }
        st.success("Estimate saved.")

    st.divider()
    st.subheader("Conceptual 3D Architectural Render Prompt")
    render_structure = st.selectbox("Building style", ["Modern residential", "Commercial office", "Industrial shed", "Low-rise apartment", "Sustainable farmhouse"])
    render_location = st.text_input("Project location / surroundings (optional)", value="Tier 2 Indian city")
    render_area = st.number_input("Render plot / built-up area (sq ft)", min_value=100, max_value=10000000, value=max(1000, int(area_sqft)), step=100)
    render_prompt = (
        f"High-quality conceptual 3D architectural visualization of a {render_structure.lower()} in {render_location or 'India'}, "
        f"approximate built-up area {render_area} square feet; climate-aware Indian architecture, realistic materials, "
        "professional daylight render, clear site context, landscaping and access paths, wide three-quarter perspective, "
        "no text, no watermark. Concept only, not a construction drawing."
    )
    st.text_area("Generated image prompt", value=render_prompt, height=110, disabled=True)
    if st.button("Generate concept image with Pollinations"):
        if not pollinations_key:
            st.warning("Enter a Pollinations API key in the sidebar first. The prompt is ready, but no image was requested.")
        else:
            try:
                import requests
                from urllib.parse import quote
                image_url = "https://gen.pollinations.ai/image/" + quote(render_prompt, safe="")
                with st.spinner("Generating conceptual image..."):
                    response = requests.get(
                        image_url,
                        params={"model": "flux", "width": 1024, "height": 768},
                        headers={"Authorization": f"Bearer {pollinations_key}"},
                        timeout=120,
                    )
                    response.raise_for_status()
                    content_type = response.headers.get("content-type", "")
                    if not content_type.startswith("image/"):
                        raise ValueError("Image service did not return an image. Check the API key and service response.")
                    st.image(response.content, caption="Conceptual architecture image — not an engineering drawing", use_container_width=True)
                    st.session_state.report["project_estimate"]["render_prompt"] = render_prompt
                    st.session_state.report["project_estimate"]["render_model"] = "Pollinations flux"
                    st.success("Concept image generated.")
            except Exception as exc:
                st.error(f"Could not generate the concept image: {exc}")

with valuation_tab:
    st.subheader("Real Estate Valuation Engine")
    st.write("Enter a verified local market rate to calculate an indicative value. The app does not fetch live property prices.")
    valuation_location = st.text_input("Property location", value="Indore, Madhya Pradesh", key="valuation_location")
    valuation_type = st.selectbox("Property type", ["Residential", "Commercial", "Industrial", "Land / Plot"], key="valuation_type")
    valuation_area = st.number_input("Built-up / plot area (sq ft)", min_value=1, max_value=10000000, value=1000, step=100, key="valuation_area")
    valuation_age = st.number_input("Building age (years)", min_value=0, max_value=500, value=5, step=1, key="valuation_age")
    valuation_amenities = st.multiselect(
        "Amenities",
        ["Parking", "Lift", "Security", "Garden", "Gym", "Pool", "Power backup", "Road access"],
        key="valuation_amenities",
    )
    valuation_rate = st.number_input(
        "Assumed market rate (INR per sq ft)",
        min_value=0,
        max_value=2000000,
        value=0,
        step=100,
        key="valuation_rate",
        help="Enter a verified local comparable rate; leave at 0 if unknown.",
    )
    valuation_rent = st.number_input("Estimated monthly rent (INR; optional)", min_value=0, max_value=100000000, value=0, step=1000, key="valuation_rent")
    valuation_appreciation = st.number_input("Assumed annual appreciation (%)", min_value=-50.0, max_value=100.0, value=0.0, step=0.5, key="valuation_appreciation")
    valuation_years = st.slider("Projection horizon (years)", min_value=1, max_value=30, value=5, key="valuation_years")

    property_value = valuation_area * valuation_rate if valuation_rate > 0 else None
    annual_rent = valuation_rent * 12 if valuation_rent > 0 else None
    rental_yield = (annual_rent / property_value * 100) if property_value and annual_rent is not None else None
    projected_value = property_value * ((1 + valuation_appreciation / 100) ** valuation_years) if property_value is not None else None

    v1, v2, v3 = st.columns(3)
    v1.metric("Indicative market value", f"₹{property_value:,.0f}" if property_value is not None else "Rate required")
    v2.metric("Gross annual rent", f"₹{annual_rent:,.0f}" if annual_rent is not None else "Not supplied")
    v3.metric("Gross rental yield", f"{rental_yield:.2f}%" if rental_yield is not None else "N/A")
    st.metric(
        f"Illustrative value in {valuation_years} years",
        f"₹{projected_value:,.0f}" if projected_value is not None else "Rate required",
    )
    st.caption("Valuation and appreciation are simple calculations from your own assumptions—not an official market valuation, investment advice, or guaranteed forecast.")
    if st.button("Save valuation to report"):
        st.session_state.report["real_estate_valuation"] = {
            "property_location": valuation_location,
            "property_type": valuation_type,
            "built_up_area_sq_ft": valuation_area,
            "building_age_years": valuation_age,
            "amenities": valuation_amenities,
            "assumed_market_rate_per_sq_ft_inr": valuation_rate if valuation_rate > 0 else None,
            "estimated_market_value_inr": property_value,
            "estimated_monthly_rent_inr": valuation_rent if valuation_rent > 0 else None,
            "estimated_annual_rent_inr": annual_rent,
            "gross_rental_yield_percent": round(rental_yield, 2) if rental_yield is not None else None,
            "assumed_annual_appreciation_percent": valuation_appreciation,
            "projection_years": valuation_years,
            "projected_value_inr": round(projected_value, 2) if projected_value is not None else None,
            "notice": "User-entered assumptions only; verify with local market comparables and a qualified professional.",
        }
        st.success("Valuation saved to JSON report.")


with daily_plan_tab:
    st.subheader("Daily Site Assistant — Work Plan")
    activity_options = [
        "General construction", "Concreting", "Excavation / foundation",
        "Crane lifting", "Scaffolding / work at height", "Masonry", "Electrical work"
    ]
    planned_activity = st.selectbox("Planned activity", activity_options, key="daily_activity")
    labour_count = st.number_input("Crew size", min_value=0, max_value=10000, value=10, step=1, key="daily_labour")
    shift_hours = st.slider("Shift duration (hours)", min_value=1, max_value=24, value=8, key="daily_shift")
    site_condition = st.selectbox(
        "Reported site/weather condition",
        ["normal", "high wind", "heavy rain", "extreme heat", "lightning", "unknown"],
        key="daily_condition",
    )
    site_notes = st.text_area("Site notes / constraints", key="daily_site_notes")

    if st.button("Generate today's site plan", type="primary"):
        activity_l = planned_activity.lower()
        if any(term in activity_l for term in ("concrete", "slab", "pour")):
            tasks = [
                "Confirm drawings, reinforcement, formwork and inspection approvals.",
                "Check concrete delivery, access, placement equipment and curing plan.",
                "Record pour timings and required quality checks.",
            ]
            resources = ["Approved concrete mix", "PPE", "Placement/compaction equipment", "Curing materials"]
        elif any(term in activity_l for term in ("excavat", "foundation")):
            tasks = [
                "Verify service locations, permits and excavation safety plan.",
                "Inspect excavation stability, protective systems and access before entry.",
                "Keep spoil and equipment clear of excavation edges; reassess after rain.",
            ]
            resources = ["Barricades/signage", "PPE", "Safe access equipment", "Excavation inspection checklist"]
        elif any(term in activity_l for term in ("crane", "lifting", "scaffold", "height")):
            tasks = [
                "Review lift/work-at-height plan and exclusion zone.",
                "Inspect lifting gear, anchorage, access and fall protection.",
                "Stop work if weather, equipment limits or site conditions are unsafe.",
            ]
            resources = ["Approved lifting/height-work equipment", "Inspection records", "PPE", "Barricades"]
        else:
            tasks = [
                "Conduct site briefing and verify the approved work sequence.",
                "Inspect work area, access, tools, materials and permits.",
                "Assign responsibilities and record changed hazards or constraints.",
            ]
            resources = ["Task-specific materials", "PPE", "Tool/equipment checklist", "Daily permits where required"]

        has_lifting = any(term in activity_l for term in ("crane", "lifting", "scaffold", "height"))
        has_concrete_excavation_or_electrical = any(term in activity_l for term in ("concrete", "slab", "pour", "excavat", "foundation", "electrical"))
        if site_condition == "lightning":
            decision = "NO-GO"
            risks = ["Lightning exposure for outdoor or elevated work."]
            precautions = ["Suspend exposed outdoor work and follow the site's shelter procedure."]
        elif site_condition == "high wind" and has_lifting:
            decision = "NO-GO"
            risks = ["Wind-sensitive lifting or elevated activity."]
            precautions = ["Suspend the task until site-specific limits and competent-person clearance permit restart."]
        elif site_condition == "heavy rain" and has_concrete_excavation_or_electrical:
            decision = "NO-GO"
            risks = ["Rain may affect excavation stability, concrete work or electrical safety."]
            precautions = ["Pause affected work until the site is assessed and conditions are controlled."]
        elif site_condition == "unknown":
            decision = "HOLD FOR VERIFICATION"
            risks = ["Current conditions are not verified."]
            precautions = ["Check official weather information and consult the site safety lead."]
        elif site_condition in ("high wind", "heavy rain", "extreme heat"):
            decision = "GO WITH CAUTION"
            risks = ["Weather-related conditions may affect site safety."]
            precautions = ["Review controls, site-specific procedures and official alerts before work."]
        else:
            decision = "GO SUBJECT TO SITE CHECKS"
            risks = []
            precautions = ["Follow the approved method statement and routine site checks."]

        checks = [
            "Confirm task-specific PPE and safe access.",
            "Check housekeeping, emergency access and communications.",
            "Brief the crew on hazards, controls and stop-work escalation.",
        ]
        if site_condition == "extreme heat":
            checks.append("Provide water, shade, rest breaks and heat-illness monitoring.")
        if site_condition in ("heavy rain", "lightning"):
            checks.append("Verify conditions before restart; follow official alerts.")
        plan = {
            "planned_activity": planned_activity,
            "crew_size": labour_count,
            "shift_hours": shift_hours,
            "site_condition": site_condition,
            "execution_recommendation": decision,
            "tasks": tasks,
            "required_materials_and_equipment": resources,
            "safety_checks": checks,
            "potential_risk_alerts": risks,
            "precautions": precautions,
            "site_notes": site_notes,
            "limitations": ["Planning aid only; confirm project drawings, permits, method statements and competent-person instructions."],
        }
        st.session_state.report["daily_site_plan"] = plan
        st.success(f"Daily plan generated — {decision}")

    saved_plan = st.session_state.report.get("daily_site_plan", {})
    if saved_plan:
        st.subheader("Generated plan")
        st.metric("Execution recommendation", saved_plan.get("execution_recommendation", "Not generated"))
        left, right = st.columns(2)
        with left:
            st.markdown("**Tasks**")
            for item in saved_plan.get("tasks", []):
                st.write(f"• {item}")
            st.markdown("**Required materials / equipment**")
            for item in saved_plan.get("required_materials_and_equipment", []):
                st.write(f"• {item}")
        with right:
            st.markdown("**Safety checks**")
            for item in saved_plan.get("safety_checks", []):
                st.write(f"• {item}")
            st.markdown("**Risk alerts and precautions**")
            for item in saved_plan.get("potential_risk_alerts", []) + saved_plan.get("precautions", []):
                st.warning(item)
        st.caption("This is a rules-based draft, not a certified site work permit or a live weather forecast.")


with weather_tab:
    st.subheader("Weather-Aware Construction Advisory")
    condition = st.selectbox("Reported weather/site condition", ["Normal", "High wind", "Heavy rain", "Extreme heat", "Lightning / storm", "Unknown"])
    planned_weather_activity = st.selectbox(
        "Weather-sensitive planned activity",
        ["General site work", "Crane lifting", "Scaffolding / work at height", "Excavation / foundation", "Concrete pouring", "Electrical work"],
        key="weather_activity",
    )
    guidance = {
        "Normal": "Follow the approved site safety plan, routine inspections, and local forecasts.",
        "High wind": "Check equipment operating limits, secure loose materials and suspend lifting or elevated work when site rules require it.",
        "Heavy rain": "Check excavation stability, drainage, slips and electrical exposure; stop affected work if unsafe.",
        "Extreme heat": "Apply the heat-stress plan, including water, shade, rest breaks and illness monitoring.",
        "Lightning / storm": "Suspend exposed outdoor work and follow shelter, evacuation and emergency procedures.",
        "Unknown": "Verify conditions through an official weather source and consult the site safety lead.",
    }
    activity_l = planned_weather_activity.lower()
    height_or_lifting = any(term in activity_l for term in ("crane", "lifting", "scaffold", "height"))
    concrete_excavation_or_electrical = any(term in activity_l for term in ("excavation", "foundation", "concrete", "electrical"))
    if condition == "Lightning / storm" or (condition == "High wind" and height_or_lifting) or (condition == "Heavy rain" and concrete_excavation_or_electrical):
        recommendation = "NO-GO"
    elif condition == "Unknown":
        recommendation = "HOLD FOR VERIFICATION"
    elif condition in ("High wind", "Heavy rain", "Extreme heat"):
        recommendation = "GO WITH CAUTION"
    else:
        recommendation = "GO SUBJECT TO SITE CHECKS"
    st.metric("Preliminary recommendation", recommendation)
    st.warning(guidance[condition])
    st.caption("Condition is user-reported; no live weather feed is connected. Follow official alerts and site-specific stop-work authority.")
    if st.button("Save weather advisory"):
        st.session_state.report["weather_advisory"] = {
            "reported_condition": condition,
            "planned_activity": planned_weather_activity,
            "recommendation": recommendation,
            "general_guidance": guidance[condition],
            "live_weather_connected": False,
        }
        st.success("Weather advisory saved.")

with assistant_tab:
    st.subheader("Construction Site Assistant")
    st.write("Ask general questions about site planning, PPE, construction documentation, or the app's estimate.")
    for chat_item in st.session_state.report["assistant_notes"]:
        with st.chat_message("user"):
            st.write(chat_item.get("question", ""))
        with st.chat_message("assistant"):
            st.write(chat_item.get("answer", ""))
    question = st.text_input("Your message", key="assistant_question")
    if st.button("Send message", type="primary"):
        if question.strip():
            if api_key and GENAI_AVAILABLE:
                try:
                    client = genai.Client(api_key=api_key)
                    chat_context = [
                        "You are a cautious construction documentation assistant. Give general information only. "
                        "Do not certify safety or structural integrity, give definitive engineering instructions, or replace a qualified professional. "
                        "Follow site-specific policy and official alerts. If uncertain, say so."
                    ]
                    for old_item in st.session_state.report["assistant_notes"][-8:]:
                        chat_context.append("User: " + str(old_item.get("question", "")))
                        chat_context.append("Assistant: " + str(old_item.get("answer", "")))
                    chat_context.append("User: " + question.strip())
                    response = client.models.generate_content(
                        model=model_name.strip() or "gemini-3.8-flash",
                        contents="\n\n".join(chat_context),
                    )
                    answer = response.text or "No text response received."
                except Exception as exc:
                    answer = f"AI request failed: {exc}"
            else:
                answer = (
                    "Demo mode: connect a valid Gemini API key in the sidebar for AI responses. "
                    "For safety-critical decisions, consult the qualified site safety lead or engineer."
                )
            st.session_state.report["assistant_notes"].append({"question": question.strip(), "answer": answer})
            st.rerun()

with report_tab:
    st.subheader("Structured JSON Data Contract")
    report = dict(st.session_state.report)
    report["application"] = "Multimodal Construction Intelligence Platform"
    report["mode"] = "Gemini-enabled when API key is supplied; otherwise demonstration mode"
    report["generated_at"] = datetime.now().isoformat(timespec="seconds")
    report["disclaimer"] = "Preliminary documentation only; not a professional engineering, safety, or valuation assessment."
    st.json(report, expanded=False)
    st.download_button(
        "Download JSON report",
        data=json.dumps(report, indent=2, ensure_ascii=False),
        file_name="construction_intelligence_report.json",
        mime="application/json",
    )

st.divider()
st.caption("Skill Wallet Capstone prototype • Python + Streamlit • Optional Gemini multimodal model")
