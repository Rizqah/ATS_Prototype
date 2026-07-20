# TrueFit React Frontend

This is the new TrueFit product frontend. It runs beside the existing
Streamlit prototype while migration is in progress.

## Run

```powershell
npm install
npm run dev
```

The frontend runs at `http://127.0.0.1:3000` and expects the FastAPI backend at
`http://127.0.0.1:8000`.

To use another backend URL:

```powershell
$env:VITE_API_URL="http://127.0.0.1:8000"
npm run dev
```

## Implemented Screens

- TrueFit landing
- Role-aware sign in and sign up
- Candidate dashboard
- CV Optimizer preview
- Candidate profile
- Recruiter workspace

These screens are the first migration slice. Streamlit remains available until
the remaining workflows are implemented and verified.
