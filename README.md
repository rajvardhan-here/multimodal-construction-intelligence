# Multimodal Construction Intelligence Platform

A Streamlit capstone prototype for documenting construction-site safety observations, reviewing potential cracks/surface defects, estimating construction budgets and assumption-based real-estate values, generating a daily site plan, providing weather-aware guidance, and exporting structured JSON.

## Features

- Site photo upload for optional Gemini multimodal review, plus a manual PPE checklist.
- Structured safety and crack-review response contracts with human-review warnings.
- Construction estimator with material assumptions, rate inputs, cost breakdown, progress and a phase-based planning timeline.
- Real-estate valuation based only on user-provided/comparable market-rate assumptions, optional monthly rent, gross yield, and appreciation projection.
- Daily site assistant with tasks, resources, safety checks, risk alerts, and activity-aware GO/NO-GO/CAUTION logic.
- Weather guidance based on a user-reported condition. **No live weather feed is connected.**
- Optional context-aware text reasoning and chatbot responses via Groq.
- Optional Gemini image analysis, with an explicit demo fallback when no Gemini key is provided.
- JSON report export.
- FastAPI backend with OpenAPI/Swagger docs and API tests.

## Tech stack

- Python 3.10+
- Streamlit (application interface)
- FastAPI + Uvicorn (optional API backend)
- Pydantic (request/response validation)
- Google Gen AI SDK (optional image analysis)
- Groq SDK (optional context-aware text reasoning)
- Pytest + FastAPI TestClient (automated API tests)

## Run the Streamlit app locally

1. Clone the repository.
2. Install root dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the interface:

   ```bash
   streamlit run app.py
   ```

## Run the FastAPI backend locally

1. Create/activate a virtual environment using your selected Python interpreter.
2. Install backend dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. Start the API server from the repository root:

   ```bash
   python -m uvicorn backend.main:app --reload
   ```

4. Open:
   - Health: http://127.0.0.1:8000/health
   - Interactive API docs: http://127.0.0.1:8000/docs

## API endpoints

- `GET /health` — health and demo/API mode.
- `POST /api/site-safety` — image-based PPE and hazard review.
- `POST /api/crack-analysis` — image-based crack/surface review.
- `POST /api/estimate` — basic cost, incurred-cost, asset-value and material calculations.
- `POST /api/project-planning` — material assumptions, cost breakdown and phased timeline.
- `POST /api/real-estate-valuation` — market-rate assumption, value, rent/yield and appreciation projection.
- `POST /api/ai/query` and `POST /api/context-aware-reasoning` — feature-aware text/image entry points.
- `POST /api/site-assistant` — construction chatbot with optional conversation history.
- `POST /api/daily-site-assistant` — daily work plan, resources, safety checks and risks.
- `POST /api/weather-advisory` — user-reported weather + planned activity advisory.

## Run automated tests

Install backend dependencies, then run:

```bash
pytest -q
python -m py_compile app.py backend/main.py
```

GitHub Actions runs syntax checks, API tests, and dependency checks for changes pushed to `main`.

## Optional AI keys

For local API runs, copy `backend/.env.example` to `backend/.env` and enter the keys you have:

- `GEMINI_API_KEY` — image analysis.
- `GROQ_API_KEY` — context-aware text reasoning and assistant answers.

Never commit the real `backend/.env` file or API keys to GitHub. If keys are missing, the API reports demo mode; it does not pretend that AI analysis occurred. The Streamlit UI accepts session-only key inputs in password fields.

## Deployment

The Streamlit app is deployed on Streamlit Community Cloud from the root `app.py`. Updates pushed to GitHub may trigger an app restart/redeploy. The FastAPI backend is a separate service when run locally; do not assume the deployed Streamlit app can reach a local `127.0.0.1` backend.

For the Streamlit deployment:
1. Sign in at https://share.streamlit.io/
2. Select this repository, branch `main`, and main file `app.py`.
3. Keep secrets out of source code. Use deployment secrets when needed.

## Limitations and safety notice

This is a capstone prototype, not a certified construction inspection system. AI may be inaccurate or miss hazards. An image cannot establish structural integrity or prove compliance with OSHA or Indian construction codes. Cost, valuation, material quantities and schedules are indicative calculations from user-editable assumptions—not a professional valuation, BOQ, or construction quote. Weather recommendations use the selected condition and do not retrieve live weather. Follow official alerts, site procedures and qualified professionals' directions.

## Activity mapping

See [docs/skill-wallet-activity-map.md](docs/skill-wallet-activity-map.md) for the mapping between Skill Wallet capstone activities, code files, endpoints, tests and remaining manual review steps.
