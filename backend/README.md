# Backend Environment Setup — Activity 1.2

This folder contains the FastAPI starter backend for the Multimodal Construction Intelligence Platform.

## Windows PowerShell setup

Run these commands from the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

## Optional API keys

Copy `backend/.env.example` to `backend/.env` and add your own keys only if you have them. Never commit the real `.env` file to GitHub.

- `GEMINI_API_KEY`: optional image analysis
- `GROQ_API_KEY`: optional assistant responses

The API returns explicit demo-mode responses when keys are not configured.

## Run the API

From the repository root, with the virtual environment activated:

```powershell
uvicorn backend.main:app --reload
```

Then open:
- Health: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs

## Basic validation

1. Confirm `/health` returns JSON with status `ok`.
2. In `/docs`, test `POST /api/estimate` with sample values.
3. Check that image endpoints clearly report demo mode if `GEMINI_API_KEY` is absent.
4. Check that `POST /api/site-assistant` returns demo mode if `GROQ_API_KEY` is absent.

The estimation values are assumption-based, not professional construction estimates. Image analysis is preliminary and must not be treated as certified safety inspection or engineering diagnosis.
