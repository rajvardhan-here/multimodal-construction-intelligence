# Multimodal Construction Intelligence Platform

A Streamlit capstone prototype for documenting construction-site safety observations, reviewing possible crack/surface defects, estimating indicative project costs, giving general weather-aware guidance, and exporting a structured JSON report.

## Features

- Upload site photographs for a multimodal review when a Google Gemini API key is supplied.
- Manual PPE checklist and reviewer-entered hazard notes.
- Preliminary image-based descriptions for visible cracks/surface defects, with uncertainty and professional-review warnings.
- Indicative construction budget calculations based on user-provided area, rate, and completion percentage.
- General weather-aware guidance based on a selected condition (no live weather feed is connected).
- A cautious construction Q&A assistant when the optional Gemini connection is configured.
- Downloadable JSON report data contract.

## Tech stack

- Python 3.10+
- Streamlit
- Google Gen AI SDK (optional runtime API use)
- Pillow

## Run locally

1. Install Python 3.10 or newer.
2. Clone this repository.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

5. Optional: add a Google Gemini API key in the app's sidebar to enable model-backed image review and assistant responses. The key is entered into a password field and is not part of the repository. Never commit API keys, credentials, or secrets.

## Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/
2. Select this repository and the `main` branch.
3. Set **Main file path** to `app.py`.
4. Deploy. Add a Gemini API key only if needed; for a public demo, use Streamlit Secrets or a runtime password field and never commit the key into source code.

## Limitations and safety notice

This is a capstone prototype, not a certified construction inspection system. AI may be inaccurate or miss hazards. Image observations cannot establish structural integrity or code compliance. Cost figures are only calculations based on user-provided assumptions, not a market quote, professional valuation, or quantity-surveyor report. The weather section uses general guidance and does not retrieve live weather. Always follow official alerts, site-specific procedures, and qualified professionals' advice.

## Capstone scope

The app demonstrates multimodal image input, structured findings, construction-specific observations, project-estimate calculations, weather guidance, a Q&A assistant, and JSON export. Production use would require test coverage, access controls, secure secrets management, validated domain datasets, observability, and expert review.
