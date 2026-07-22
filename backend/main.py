"""FastAPI entry point for the TrueFit backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import auth, communications, cv, matching, profile, recruiter, security

app = FastAPI(
    title="Fydara API",
    description="Backend API for the Fydara recruiter and candidate experiences.",
    version="0.1.0",
)
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "Fydara API"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(cv.router, prefix="/api")
app.include_router(security.router, prefix="/api")
app.include_router(recruiter.router, prefix="/api")
app.include_router(communications.router, prefix="/api")


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "fydara-api"}
