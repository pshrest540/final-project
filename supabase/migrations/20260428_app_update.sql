-- Run this once against an existing Supabase/PostgreSQL database after the
-- maintenance, admin, customer, and full prediction-history app update.
-- It is safe to run more than once.

do $$
begin
    create type account_type_enum as enum ('personal', 'business', 'admin');
exception
    when duplicate_object then null;
end $$;

alter type account_type_enum add value if not exists 'personal';
alter type account_type_enum add value if not exists 'business';
alter type account_type_enum add value if not exists 'admin';

do $$
begin
    create type service_category_enum as enum ('engine', 'drivetrain', 'electrical', 'routine');
exception
    when duplicate_object then null;
end $$;

alter type service_category_enum add value if not exists 'engine';
alter type service_category_enum add value if not exists 'drivetrain';
alter type service_category_enum add value if not exists 'electrical';
alter type service_category_enum add value if not exists 'routine';

alter table users add column if not exists business_name varchar(255);
alter table users add column if not exists full_name varchar(255);

alter table vehicles add column if not exists customer_name varchar(100);

alter table wellness_predictions add column if not exists cv_wellness double precision;
alter table wellness_predictions add column if not exists wb_wellness double precision;
alter table wellness_predictions add column if not exists brk_wellness double precision;
alter table wellness_predictions add column if not exists bat_wellness double precision;
alter table wellness_predictions add column if not exists alt_wellness double precision;
alter table wellness_predictions add column if not exists sta_wellness double precision;
alter table wellness_predictions add column if not exists coolant_wellness double precision;
alter table wellness_predictions add column if not exists ignition_wellness double precision;
alter table wellness_predictions add column if not exists fuel_wellness double precision;

create table if not exists scheduled_maintenance (
    id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    task_key varchar(50) not null,
    last_service_mileage integer,
    interval_miles integer not null,
    updated_at timestamp with time zone default now()
);

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'uq_vehicle_task'
          and conrelid = 'scheduled_maintenance'::regclass
    ) then
        alter table scheduled_maintenance
            add constraint uq_vehicle_task unique (vehicle_id, task_key);
    end if;
end $$;

create table if not exists component_replacements (
    id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    component_key varchar(50) not null,
    replaced_at_mileage integer not null,
    notes varchar(255),
    replaced_on timestamp with time zone default now()
);

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'uq_vehicle_component'
          and conrelid = 'component_replacements'::regclass
    ) then
        alter table component_replacements
            add constraint uq_vehicle_component unique (vehicle_id, component_key);
    end if;
end $$;

create index if not exists idx_vehicles_owner_id on vehicles(owner_id);
create index if not exists idx_predictions_vehicle_id on wellness_predictions(vehicle_id);
create index if not exists idx_predictions_calculated_at on wellness_predictions(calculated_at desc);
create index if not exists idx_scheduled_maintenance_vehicle_id on scheduled_maintenance(vehicle_id);
create index if not exists idx_component_replacements_vehicle_id on component_replacements(vehicle_id);
