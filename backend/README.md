# FastAPI backend setup

This folder contains the FastAPI API layer for the Multimodal Construction Intelligence Platform. The Streamlit interface is the separately runnable application at repository root `app.py`.

## Set up an environment

Use the Python interpreter configured in your IDE (Python 3.10+ recommended for the application). From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

If PowerShell blocks environment activation, change the terminal to Command Prompt and use:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

## Optional API keys

Copy `backend/.env.example` to `backend/.env` and enter keys only if you have them. Never commit the real `.env` file.

- `GEMINI_API_KEY`: optional multimodal image analysis.
- `GROQ_API_KEY`: optional context-aware text responses.

Without a key, the application returns explicit demo/schema-fallback responses and reports that no AI analysis was performed.

## Start the API

From the repository root, with the environment activated:

```powershell
python -m uvicorn backend.main:app --reload
```

Open:
- Health: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs

## Important endpoints

- `POST /api/estimate`
- `POST /api/project-planning`
- `POST /api/real-estate-valuation`
- `POST /api/site-safety`
- `POST /api/crack-analysis`
- `POST /api/ai/query`
- `POST /api/context-aware-reasoning`
- `POST /api/site-assistant`
- `POST /api/daily-site-assistant`
- `POST /api/weather-advisory`

## Validate locally

```powershell
python -m py_compile app.py backend/main.py
pytest -q
```

Tests exercise health status, cost arithmetic, project planning, valuation behavior, weather decisions, assistant demo fallback, image-analysis schema fallback, and image validation.

Calculations use explicit user-provided assumptions. The API does not fetch live weather or local market prices, and image analysis must not be treated as a certified safety inspection or engineering diagnosis.
