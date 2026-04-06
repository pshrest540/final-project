"""
Predictive Vehicle Maintenance - FastAPI Backend
Run with: uvicorn api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import predict, brands, retrain
from api.models.loader import load_all_models

app = FastAPI(
    title="Vehicle Maintenance Predictor API",
    description="Predicts health scores for Engine, Drivetrain, and Electrical systems.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models once at startup
@app.on_event("startup")
def startup_event():
    load_all_models()

# Routers
app.include_router(predict.router)
app.include_router(brands.router)
app.include_router(retrain.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Vehicle Maintenance API is running."}
