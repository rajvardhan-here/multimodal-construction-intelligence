# Multimodal Construction Intelligence Platform

A Streamlit capstone prototype for construction-site safety observations, concrete crack observations, preliminary project-cost estimation, weather-aware site guidance, and downloadable JSON reporting.

## Features

- Upload and view construction-site photographs.
- Record a reviewer-led PPE checklist and site hazards.
- Record crack appearance, estimated length, notes, and concern level.
- Calculate an indicative construction budget from user-provided area and rate assumptions.
- View general weather-aware safety guidance based on a selected condition.
- Export saved observations and estimates as a JSON report.

## Tech stack

- Python
- Streamlit

## Run locally

1. Install Python 3.10 or newer.
2. Clone this repository.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/
2. Choose this GitHub repository and the `main` branch.
3. Set the main file path to `app.py`.
4. Deploy and copy the HTTPS app URL.

## Limitations and safety notice

This starter version is a demonstration application. It does not perform verified AI-based image recognition, does not access live weather feeds, and does not provide engineering diagnosis, certified safety inspection, or professional property valuation. PPE and crack information is entered by the user for documentation. Cost outputs are only estimates based on user-supplied assumptions. Always follow site-specific procedures and consult qualified professionals when needed.

## Capstone alignment

The app demonstrates a multi-tab UI, image upload, structured observations, budget calculations, weather condition guidance, and JSON report export. Further work may add an authenticated multimodal model, validated engineering datasets, tests, and richer deployment monitoring.
