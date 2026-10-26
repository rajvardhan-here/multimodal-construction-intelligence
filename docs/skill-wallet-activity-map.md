# Skill Wallet Activity Mapping

This document maps the activities shown in the Skill Wallet workspace to the repository implementation. Status below describes code/documentation present in GitHub, not an evaluator's approval in Skill Wallet.

## Activity 1 — Requirements and environment
- **Activity 1.1: Define Functional Requirements** — `docs/requirements.md`
- **Activity 1.2: Create requirements.txt and Set Up Environment** — `backend/requirements.txt`, `backend/README.md`, `backend/main.py`; local FastAPI health check and endpoint tests were run manually by the learner and shown as HTTP 200/demo responses in screenshots.

## Epic 2 — Image-based analysis
- **Activity 2.1: Safety Image Analysis** — `POST /api/site-safety`, optional context field, Gemini image review, Pydantic `SafetyAnalysisResult` contract.
- **Activity 2.2: Crack Detection Logic** — `POST /api/crack-analysis`, optional context field, Gemini image review, Pydantic `CrackAnalysisResult` contract.

When `GEMINI_API_KEY` is absent, image endpoints return schema-shaped demo results with `ai_analysis_performed: false`. These are not AI findings.

## Epic 3 — Construction planning and valuation
- **Activity 3.1: Construction Project Planning Logic** — `POST /api/project-planning`; editable material quantity and unit-rate assumptions, cost summary, phased timeline, and milestone progress.
- **Activity 3.2: Real Estate Valuation Engine** — `POST /api/real-estate-valuation`; user-provided market rate, estimated value, optional rent/yield, and assumed appreciation projection. The Streamlit UI contains a matching valuation tab.

Market rates and material factors are user assumptions. No live property-market or material-price feed is connected.

## Epic 4 — AI integration and data contracts
- **Activity 4.1: Multimodal AI Integration Approach** — shared Gemini helper for image + text; Groq helper for context-aware text responses; `POST /api/ai/query` as a unified feature entry point.
- **Activity 4.2: Structured Output Enforcement and Data Contracts** — Pydantic models `SafetyAnalysisResult`, `CrackAnalysisResult`, `ContextAwareResult`, plus request models for planning, valuation, weather, and daily site plans. AI image JSON is parsed and validated against its selected model.
- **Activity 4.3: Context-Aware Reasoning and Feature Differentiation** — `FEATURE_INSTRUCTIONS`, per-feature instructions and `context` + `history` inputs for `POST /api/context-aware-reasoning`.

## Epic 5 — Assistant and advisory engine
- **Activity 5.1: Construction Chatbot Development** — `POST /api/site-assistant`; accepts user question and recent conversation history.
- **Activity 5.2: Daily Site Assistant Implementation** — `POST /api/daily-site-assistant`; returns task breakdown, resources, safety checks, risk alerts, and execution recommendation. The Streamlit UI contains a matching Daily Site Plan tab.
- **Activity 5.3: Weather-Aware Construction Advisory** — `POST /api/weather-advisory`; condition + planned activity produce a rule-based GO/NO-GO/CAUTION recommendation. The app states that conditions are user-reported and no live weather feed is connected.

## Epic 6 — UI, validation, deployment
- **Activity 6.1: Interface Integration and End-to-End Testing** — Streamlit UI in `app.py` and API routes in `backend/main.py`; UI includes safety, crack, planning, valuation, daily plan, weather, assistant and JSON report tabs.
- **Activity 6.2: System Validation and Edge Case Testing** — `tests/test_api.py` covers core calculation routes, demo fallbacks, weather rules, missing files and unsupported file types. GitHub Actions runs syntax checks, pytest and `pip check`.
- **Activity 6.3: Deployment Readiness and Documentation** — `README.md`, `backend/README.md`, `docs/requirements.md`, and this mapping file. Streamlit deployment details are in the root README.

## Conclusion
The repository is a capstone prototype with deterministic planning/valuation math, optional LLM integrations, explicit structured outputs, and edge-case tests. It is **not a production-certified safety or structural assessment system**. Model-backed image findings require a configured Gemini API key; model-backed text reasoning requires a configured Groq API key. Live weather and verified property market rates are not connected.

## Learner checklist before asking Skill Wallet for review
- [ ] Pull latest `main` in PyCharm.
- [ ] Run `pip install -r backend/requirements.txt` in the selected interpreter.
- [ ] Run `pytest -q` and check all tests pass.
- [ ] Run `python -m py_compile app.py backend/main.py`.
- [ ] Run the app and API endpoints locally, including edge cases.
- [ ] Confirm the deployed Streamlit app loads after GitHub updates.
- [ ] For each activity in Skill Wallet, use **Review** only after you have inspected the corresponding code/output; wait for the evaluator to approve before assuming it is complete.
- [ ] Keep all actual API keys out of GitHub; use local `backend/.env` or deployment secrets.
