import json
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ Multimodal Construction Intelligence Platform")
st.caption("Construction safety observations • Crack observations • Budget estimation • Weather-aware guidance")
st.info(
    "Prototype/demo mode. Results are based on user inputs and simple calculations; "
    "this app does not perform verified AI image analysis or fetch live weather."
)

with st.sidebar:
    st.header("Project overview")
    st.write("**Capstone:** Multimodal Construction Intelligence Platform")
    st.write("**Mode:** Demonstration")
    st.caption("Not a substitute for a qualified engineer, safety officer, or official weather alert.")

if "report" not in st.session_state:
    st.session_state.report = {
        "generated_at": None,
        "ppe_observations": {},
        "hazards": [],
        "crack_observation": {},
        "project_estimate": {},
        "weather_advisory": {},
    }

safety_tab, crack_tab, estimate_tab, weather_tab, report_tab = st.tabs(
    ["Site Safety & PPE", "Crack Observations", "Project Estimator", "Weather Advisory", "Report"]
)

with safety_tab:
    st.subheader("Site Safety & PPE Audit")
    photo = st.file_uploader("Upload a construction-site image", type=["jpg", "jpeg", "png"], key="site_photo")
    if photo:
        st.image(photo, caption="Uploaded site image", use_container_width=True)
    st.warning("No computer-vision model is connected in this version. Use this section to record a human review.")
    st.markdown("**Reviewer checklist**")
    ppe = {}
    c1, c2 = st.columns(2)
    checks = [
        ("Helmet / hard hat", c1),
        ("High-visibility vest", c2),
        ("Safety footwear", c1),
        ("Harness where required", c2),
    ]
    for label, col in checks:
        with col:
            ppe[label] = st.selectbox(
                label,
                ["Not reviewed", "Observed", "Not observed", "Not applicable"],
                key="ppe_" + label,
            )
    hazards_text = st.text_area("Potential hazards observed (one per line)", key="hazards_input")
    if st.button("Save safety observations"):
        st.session_state.report["ppe_observations"] = ppe
        st.session_state.report["hazards"] = [x.strip() for x in hazards_text.splitlines() if x.strip()]
        st.success("Safety observations saved.")

with crack_tab:
    st.subheader("Crack Observations")
    crack_photo = st.file_uploader("Upload wall / concrete photo", type=["jpg", "jpeg", "png"], key="crack_photo")
    if crack_photo:
        st.image(crack_photo, caption="Uploaded surface image", use_container_width=True)
    st.warning("This section records observations only; it does not diagnose structural safety. Seek a qualified engineer's inspection when concerned.")
    appearance = st.selectbox(
        "Observed appearance",
        ["Not classified", "Hairline", "Settlement-like", "Diagonal / shear-like", "Expansion-like", "Spalling / material loss", "Other"],
    )
    length_cm = st.number_input("Approximate visible length (cm; optional)", min_value=0.0, value=0.0, step=1.0)
    notes = st.text_area("Context / notes")
    concern = st.selectbox(
        "Concern level (your observation)",
        ["Not assessed", "Monitor and seek advice", "Prompt professional inspection", "Immediate hazard suspected"],
    )
    if st.button("Save crack observation"):
        st.session_state.report["crack_observation"] = {
            "observed_appearance": appearance,
            "approximate_length_cm": length_cm,
            "notes": notes,
            "user_selected_concern_level": concern,
        }
        st.success("Crack observations saved.")

with estimate_tab:
    st.subheader("Preliminary Project Estimator")
    structure = st.selectbox("Structure type", ["Residential", "Commercial", "Industrial", "Other"])
    area_sqft = st.number_input("Built-up area (sq ft)", min_value=0, value=1000, step=100)
    rate = st.number_input("Assumed cost per sq ft (INR)", min_value=0, value=2000, step=100)
    completion = st.slider("Completion percentage", 0, 100, 0)
    tier = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3", "Not specified"])
    total = area_sqft * rate
    spent = total * completion / 100
    m1, m2, m3 = st.columns(3)
    m1.metric("Indicative total", f"₹{total:,.0f}")
    m2.metric("Indicative amount incurred", f"₹{spent:,.0f}")
    m3.metric("Indicative remaining", f"₹{total - spent:,.0f}")
    st.caption("Cost per sq ft is your assumption, not a verified market quote or professional valuation.")
    if st.button("Save estimate"):
        st.session_state.report["project_estimate"] = {
            "structure_type": structure,
            "built_up_area_sq_ft": area_sqft,
            "assumed_cost_per_sq_ft_inr": rate,
            "completion_percent": completion,
            "city_tier": tier,
            "indicative_total_inr": total,
            "indicative_incurred_inr": spent,
        }
        st.success("Estimate saved.")

with weather_tab:
    st.subheader("Weather-aware Site Guidance")
    condition = st.selectbox(
        "Reported condition",
        ["Normal", "High wind", "Heavy rain", "Extreme heat", "Lightning / storm", "Unknown"],
    )
    guidance = {
        "Normal": "Follow the approved site safety plan and routine checks.",
        "High wind": "Follow site rules and equipment limits; pause lifting or work-at-height activities when required.",
        "Heavy rain": "Review slip risks, excavation stability, drainage, and electrical exposure; stop affected work if unsafe.",
        "Extreme heat": "Follow the heat-stress plan, including water, rest, shade, and monitoring for illness.",
        "Lightning / storm": "Suspend exposed outdoor work and follow the site's shelter and emergency procedures.",
        "Unknown": "Check an official weather source and consult the site safety team before weather-dependent work.",
    }
    st.warning(guidance[condition])
    st.caption("This app does not fetch live weather. Follow official alerts and site-specific emergency procedures.")
    if st.button("Save weather advisory"):
        st.session_state.report["weather_advisory"] = {
            "reported_condition": condition,
            "general_guidance": guidance[condition],
        }
        st.success("Weather guidance saved.")

with report_tab:
    st.subheader("Export Project Report")
    report = dict(st.session_state.report)
    report["generated_at"] = datetime.now().isoformat(timespec="seconds")
    report["application"] = "Multimodal Construction Intelligence Platform"
    report["mode"] = "demonstration"
    report["disclaimer"] = "User-entered observations and indicative estimates only; not a professional assessment."
    st.json(report, expanded=False)
    st.download_button(
        "Download JSON report",
        data=json.dumps(report, indent=2, ensure_ascii=False),
        file_name="construction_intelligence_report.json",
        mime="application/json",
    )

st.divider()
st.caption("Skill Wallet Capstone prototype • Built with Streamlit • Demonstration mode")
