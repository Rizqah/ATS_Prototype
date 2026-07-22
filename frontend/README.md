# TrueFit React Frontend

This is the supported TrueFit product frontend. It connects to the FastAPI API.

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

## Implemented Screens and Workflows

- TrueFit landing
- Role-aware sign in and sign up
- Candidate dashboard
- CV Optimizer preview
- Candidate profile
- Recruiter workspace
- Candidate matching and feedback
- Talent pool and CSV export
- Hiring reports and PDF export
- Account security, privacy, password reset and two-factor authentication
