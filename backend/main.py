"""FastAPI entry point for the TrueFit backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import auth, cv, matching, profile

app = FastAPI(
    title="TrueFit API",
    description="Backend API for the TrueFit recruiter and candidate experiences.",
    version="0.1.0",
)

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


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "truefit-api"}
