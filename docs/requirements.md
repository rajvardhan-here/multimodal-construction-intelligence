# Functional Requirements Specification

## 1. Project overview

**Project:** Multimodal Construction Intelligence Platform  
**Category:** Generative AI / Real Estate Decision Support  
**Purpose:** Provide a prototype decision-support interface for construction-site observations, preliminary planning estimates, and weather-aware guidance.

This document follows the functional areas and terminology shown in the Skill Wallet capstone Activity 1.1 brief.

## 2. Users and intended use

- Construction site staff may record observations and upload site photographs.
- Project planners may enter area, cost, location-tier, and completion assumptions.
- Reviewers may export structured information for review.

This prototype is not a certified safety-inspection, structural-diagnosis, or professional valuation system.

## 3. Functional requirements

### FR-01 — Site safety and PPE observations
- Allow JPG/PNG construction-site photo upload.
- Provide a reviewer checklist for helmet/hard hat, high-visibility vest, safety footwear, and harness where required.
- Allow potential hazards to be recorded as separate notes.
- When a Gemini API key is provided, request a preliminary multimodal review.
- Display the result as structured information, including safety score/status when returned, PPE observations, possible hazards, severity, and suggested follow-up.
- Make uncertainty and human-review warnings visible.

### FR-02 — Crack and surface-defect observations
- Allow JPG/PNG wall or concrete image upload.
- Allow contextual notes to be entered.
- When a Gemini API key is provided, request a conservative preliminary description of visible defects.
- Where returned, show defect category, possible causes, urgency, observations, limitations, and options for a qualified engineer to evaluate.
- Do not present image-only estimates as a definitive structural diagnosis.

### FR-03 — Project planning and cost estimation
- Accept structure type, built-up area in square feet, assumed construction cost per square foot, completion percentage, and Indian city tier.
- Calculate indicative total budget, incurred amount, and remaining amount.
- Accept an assumed market value per square foot and show an indicative asset-value estimate in INR, including lakh/crore formatting.
- Accept explicit planning assumptions for steel kilograms per square foot and cement 50 kg bags per square foot, then calculate indicative quantities.
- Show a milestone/completion progress bar.
- Label all costs, material quantities, and asset values as assumption-based estimates rather than verified prices or professional quantities.

### FR-04 — Conceptual architectural visualization
- Generate a reusable prompt from selected building style, project location/setting, and approximate area.
- If a configured image-service API key is supplied, offer a request for a conceptual visualization.
- Clearly label the result as a concept image, not a construction drawing or engineering plan.
- Provide graceful error handling if the service is unavailable or rejects a request.

### FR-05 — Weather-aware daily guidance
- Let the user select a reported condition: normal, high wind, heavy rain, extreme heat, lightning/storm, or unknown.
- Show general precautions appropriate to the selected condition.
- State that the prototype does not use a live weather feed and does not replace official alerts or site-specific emergency procedures.

### FR-06 — Construction site assistant
- Provide a text input for general construction-planning and documentation questions.
- When Gemini is configured, send the question along with recent conversation context and display the response.
- Without an API key, explain that the assistant is in demonstration mode.
- Avoid claiming that the assistant certifies site safety or structural integrity.

### FR-07 — Structured JSON contract and export
- Keep key outputs in structured dictionaries/JSON to support consistent display and downstream review.
- Include saved safety observations, crack observations, cost estimates, weather guidance, assistant notes, mode, timestamp, and limitations where available.
- Provide a JSON download.

### FR-08 — Project links and deployment
- Store source code in the public GitHub repository.
- Maintain setup instructions and dependency declarations.
- Deploy the Streamlit app to a reachable HTTPS URL and submit the repository and live demo URLs on Skill Wallet after testing.

## 4. Non-functional requirements

- **Robustness:** handle missing image uploads, absent optional API keys, API errors, invalid responses, and service timeouts gracefully.
- **Usability:** present feature areas in clear tabs with labeled inputs, metric summaries, warnings, and export actions.
- **Maintainability:** keep the application modular and dependencies listed in requirements.txt.
- **Security:** never hard-code API keys or commit secrets; use password fields or the hosting provider's secret-management facility.
- **Transparency:** identify AI output as preliminary and disclose limitations.
- **Portability:** support execution with Python and Streamlit, including deployment on Streamlit Community Cloud.

## 5. Input/output summary

| Feature | Main inputs | Outputs |
|---|---|---|
| Site safety/PPE | Site photo, manual PPE checklist, hazard notes | Preliminary structured observations, score/status where returned, hazard list |
| Crack observations | Surface photo, context notes | Preliminary defect description, possible causes, urgency, limitations |
| Estimator | Structure type, area, assumed rates, completion, city tier, material assumptions | Indicative budget, incurred/remaining amount, asset-value estimate, steel/cement quantities, progress |
| Architectural visualization | Building style, location, area, optional image-service key | Prompt and, if service succeeds, conceptual image |
| Weather guidance | Reported weather condition | General safety precautions |
| Site assistant | Question, optional Gemini key | Text response or demo-mode notice |
| Report export | Saved session data | Downloadable JSON |

## 6. Acceptance checks

- The app starts with streamlit run app.py.
- Every feature tab opens and its controls are usable.
- The app functions in demo mode with no external API key.
- Image-analysis actions clearly report when the image is missing, the API is not configured, or an API call fails.
- Budget and material calculations respond to changed inputs.
- JSON export produces valid JSON.
- No API keys or secrets are committed in this repository.
- The deployed app URL and repository URL open successfully.

## 7. Known limitations

- AI vision output may be inaccurate or miss hazards.
- No live weather provider is currently connected.
- Market value and material quantities use user-entered assumptions and must be verified independently.
- Production use would require specialist validation, domain testing, access controls, monitoring, and review by qualified professionals.
