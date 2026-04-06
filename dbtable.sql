CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    account_type ENUM('personal', 'business', 'admin') DEFAULT 'personal',
    business_name VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicles (
    vehicle_id VARCHAR(36) PRIMARY KEY,
    owner_id VARCHAR(36) NOT NULL,
    vin VARCHAR(17) NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    current_mileage INT NOT NULL,
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE vehicle_habits (
    habit_id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    rough_scale FLOAT DEFAULT 0.0,
    torque_scale FLOAT DEFAULT 0.0,
    stop_scale FLOAT DEFAULT 0.0,
    temp_scale FLOAT DEFAULT 0.0,
    habit_scale FLOAT DEFAULT 0.0,
    idle_scale FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

CREATE TABLE maintenance_logs (
    log_id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    service_category ENUM('engine', 'drivetrain', 'electrical', 'routine') NOT NULL,
    component_replaced VARCHAR(100) NOT NULL,
    mileage_at_service INT NOT NULL,
    service_date DATE NOT NULL,
    performed_by VARCHAR(100) NULL,
    service_notes TEXT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

CREATE TABLE wellness_predictions (
    prediction_id VARCHAR(36) PRIMARY KEY,
    vehicle_id VARCHAR(36) NOT NULL,
    overall_score FLOAT NOT NULL,
    engine_score FLOAT NOT NULL,
    drivetrain_score FLOAT NOT NULL,
    electrical_score FLOAT NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);