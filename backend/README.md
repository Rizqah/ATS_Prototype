# TrueFit FastAPI Backend

This backend runs beside the existing Streamlit prototype and exposes the first
UI-neutral TrueFit services over HTTP.

## Run Locally

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Open:

- API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Current Routes

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/users/{email}`
- `PUT /api/auth/users/{email}`
- `GET /api/profile/{user_email}`
- `POST /api/profile/{user_email}`
- `PUT /api/profile/{user_email}`
- `POST /api/matching/resume/extract`
- `POST /api/matching/batch`
- `POST /api/matching/profile`
- `POST /api/matching/feedback`
- `POST /api/matching/improvements`
- `POST /api/cv/render`
- `POST /api/cv/pdf`
- `POST /api/cv/docx`
- `POST /api/cv/optimize`

## Prototype Boundaries

- Existing JSON files in `careerhub_data/` remain the data store.
- Existing password hashing/auth behavior is preserved for migration
  compatibility; this is not production-grade token authentication.
- OpenAI-backed endpoints require `OPENAI_API_KEY`.
- Streamlit pages are unchanged and can continue running during migration.
