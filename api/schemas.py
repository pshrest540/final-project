"""
Pydantic schemas for request validation and response serialization.
FastAPI uses these to auto-validate inputs and generate API docs.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


# ── Request ────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    # Vehicle identity
    brand: str          = Field(..., example="Toyota")
    model: str          = Field(..., example="Camry")
    year:  int          = Field(..., ge=1990, le=2025, example=2015)
    mileage: int        = Field(..., ge=0, le=500000, example=85000)

    # Drivetrain stress scales (0.0 – 1.0)
    rough_scale:  float = Field(..., ge=0.0, le=1.0, example=0.4,
                                description="Road roughness (0=smooth, 1=very rough)")
    torque_scale: float = Field(..., ge=0.0, le=1.0, example=0.3,
                                description="Towing or heavy load usage")
    stop_scale:   float = Field(..., ge=0.0, le=1.0, example=0.4,
                                description="Stop-and-go traffic frequency")

    # Electrical + Engine stress scales (0.0 – 1.0)
    temp_scale:   float = Field(..., ge=0.0, le=1.0, example=0.4,
                                description="Extreme temperature exposure")
    habit_scale:  float = Field(..., ge=0.0, le=1.0, example=0.3,
                                description="Aggressive driving habits")
    idle_scale:   float = Field(..., ge=0.0, le=1.0, example=0.3,
                                description="Extended idling frequency")
    vehicle_id:   Optional[str] = None


# ── Component scores ───────────────────────────────────────────────────────────

class DrivetrainScores(BaseModel):
    cv_wellness:  float = Field(..., description="CV joint health (0-100)")
    wb_wellness:  float = Field(..., description="Wheel bearing health (0-100)")
    brk_wellness: float = Field(..., description="Brake system health (0-100)")
    system_avg:   float = Field(..., description="Drivetrain system average")

class ElectricalScores(BaseModel):
    bat_wellness: float = Field(..., description="Battery health (0-100)")
    alt_wellness: float = Field(..., description="Alternator health (0-100)")
    sta_wellness: float = Field(..., description="Starter motor health (0-100)")
    system_avg:   float = Field(..., description="Electrical system average")

class EngineScores(BaseModel):
    coolant_wellness:   float = Field(..., description="Coolant system health (0-100)")
    ignition_wellness:  float = Field(..., description="Ignition system health (0-100)")
    fuel_wellness:      float = Field(..., description="Fuel system health (0-100)")
    system_avg:         float = Field(..., description="Engine system average")


# ── Response ───────────────────────────────────────────────────────────────────

class PredictResponse(BaseModel):
    vehicle:     str             = Field(..., example="2015 Toyota Camry — 85,000 miles")
    drivetrain:  DrivetrainScores
    electrical:  ElectricalScores
    engine:      EngineScores
    overall_avg: float           = Field(..., description="Average across all 3 systems")


# ── Brands response ────────────────────────────────────────────────────────────

class ModelEntry(BaseModel):
    model:        str
    type:         str
    elec_score:   int
    drive_score:  int
    engine_score: int

class BrandEntry(BaseModel):
    brand:  str
    models: list[ModelEntry]

class BrandsResponse(BaseModel):
    brands: list[BrandEntry]


# ── Retrain response ───────────────────────────────────────────────────────────

class RetrainResponse(BaseModel):
    status:  str
    message: str
    results: Optional[dict] = None


# ── Auth schemas ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    account_type: Optional[str] = "personal"
    business_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    email: str
    account_type: str
    business_name: Optional[str] = None
    full_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ── Vehicle schemas ────────────────────────────────────────────────────────────

class VehicleCreate(BaseModel):
    brand: str
    model: str
    year: int             = Field(..., ge=1990, le=2025)
    current_mileage: int  = Field(..., ge=0)
    vin: Optional[str]    = None


class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id:       str
    brand:            str
    model:            str
    year:             int
    current_mileage:  int
    vin:              Optional[str]      = None
    added_on:         Optional[datetime] = None


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prediction_id:      str
    overall_score:      float
    engine_score:       float
    drivetrain_score:   float
    electrical_score:   float
    calculated_at:      Optional[datetime] = None
