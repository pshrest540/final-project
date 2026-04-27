-- Supabase/PostgreSQL schema for the MIA vehicle maintenance app.
-- This matches supabase/schema.sql.

do $$
begin
    create type account_type_enum as enum ('personal', 'business', 'admin');
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type service_category_enum as enum ('engine', 'drivetrain', 'electrical', 'routine');
exception
    when duplicate_object then null;
end $$;

create table if not exists users (
    user_id varchar(36) primary key,
    email varchar(255) unique not null,
    password_hash varchar(255) not null,
    account_type account_type_enum not null default 'personal',
    business_name varchar(255),
    full_name varchar(255),
    created_at timestamp with time zone default now()
);

create table if not exists vehicles (
    vehicle_id varchar(36) primary key,
    owner_id varchar(36) not null references users(user_id) on delete cascade,
    vin varchar(17),
    brand varchar(50) not null,
    model varchar(50) not null,
    year integer not null,
    current_mileage integer not null,
    added_on timestamp with time zone default now()
);

create table if not exists vehicle_habits (
    habit_id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    rough_scale double precision default 0.0,
    torque_scale double precision default 0.0,
    stop_scale double precision default 0.0,
    temp_scale double precision default 0.0,
    habit_scale double precision default 0.0,
    idle_scale double precision default 0.0,
    last_updated timestamp with time zone default now()
);

create table if not exists maintenance_logs (
    log_id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    service_category service_category_enum not null,
    component_replaced varchar(100) not null,
    mileage_at_service integer not null,
    service_date date not null,
    performed_by varchar(100),
    service_notes text
);

create table if not exists wellness_predictions (
    prediction_id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    overall_score double precision not null,
    engine_score double precision not null,
    drivetrain_score double precision not null,
    electrical_score double precision not null,
    calculated_at timestamp with time zone default now()
);

create index if not exists idx_vehicles_owner_id on vehicles(owner_id);
create index if not exists idx_predictions_vehicle_id on wellness_predictions(vehicle_id);
create index if not exists idx_predictions_calculated_at on wellness_predictions(calculated_at desc);
