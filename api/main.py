
#Run with: uvicorn api.main:app --reload
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import predict, brands, retrain
from api.models.loader import load_all_models
from api.routers import dbtest
import api.db.models  # noqa: F401 — registers all ORM models with Base
from api.db.session import engine, Base
from api.routers.auth import router as auth_router
from api.routers.vehicles import router as vehicles_router

app = FastAPI(
    title="Vehicle Maintenance Predictor API",
    description="Predicts health scores for Engine, Drivetrain, and Electrical systems.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep startup fast so Render can mark the service healthy quickly.
@app.on_event("startup")
def startup_event():
    if os.getenv("CREATE_DB_TABLES_ON_STARTUP", "false").lower() == "true":
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"WARNING: Could not create DB tables at startup: {e}")

    if os.getenv("LOAD_MODELS_ON_STARTUP", "false").lower() == "true":
        load_all_models()

# Routers
app.include_router(predict.router)
app.include_router(brands.router)
app.include_router(retrain.router)
app.include_router(dbtest.router)
app.include_router(auth_router)
app.include_router(vehicles_router)

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "service": "MIA Vehicle Maintenance Predictor API",
        "health": "/health",
        "docs": "/docs",
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Vehicle Maintenance API is running."}
