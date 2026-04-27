from sqlalchemy import (
    Column, String, Integer, Float, Text, Date, TIMESTAMP,
    ForeignKey, Enum
)
from sqlalchemy import text
from sqlalchemy.orm import relationship

from api.db.session import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    account_type = Column(
        Enum("personal", "business", "admin", name="account_type_enum"),
        nullable=False,
        server_default="personal",
    )
    business_name = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete")


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String(36), primary_key=True)
    owner_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    vin = Column(String(17), nullable=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    current_mileage = Column(Integer, nullable=False)
    added_on = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    owner = relationship("User", back_populates="vehicles")
    habits = relationship("VehicleHabit", back_populates="vehicle", cascade="all, delete")
    maintenance_logs = relationship("MaintenanceLog", back_populates="vehicle", cascade="all, delete")
    predictions = relationship("WellnessPrediction", back_populates="vehicle", cascade="all, delete")


class VehicleHabit(Base):
    __tablename__ = "vehicle_habits"

    habit_id = Column(String(36), primary_key=True)
    vehicle_id = Column(String(36), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False)
    rough_scale = Column(Float, default=0.0)
    torque_scale = Column(Float, default=0.0)
    stop_scale = Column(Float, default=0.0)
    temp_scale = Column(Float, default=0.0)
    habit_scale = Column(Float, default=0.0)
    idle_scale = Column(Float, default=0.0)
    last_updated = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    vehicle = relationship("Vehicle", back_populates="habits")


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    log_id = Column(String(36), primary_key=True)
    vehicle_id = Column(String(36), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False)
    service_category = Column(
        Enum("engine", "drivetrain", "electrical", "routine", name="service_category_enum"),
        nullable=False,
    )
    component_replaced = Column(String(100), nullable=False)
    mileage_at_service = Column(Integer, nullable=False)
    service_date = Column(Date, nullable=False)
    performed_by = Column(String(100), nullable=True)
    service_notes = Column(Text, nullable=True)

    vehicle = relationship("Vehicle", back_populates="maintenance_logs")


class WellnessPrediction(Base):
    __tablename__ = "wellness_predictions"

    prediction_id = Column(String(36), primary_key=True)
    vehicle_id = Column(String(36), ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, nullable=False)
    engine_score = Column(Float, nullable=False)
    drivetrain_score = Column(Float, nullable=False)
    electrical_score = Column(Float, nullable=False)
    calculated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    vehicle = relationship("Vehicle", back_populates="predictions")