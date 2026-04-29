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

create table if not exists users (
    user_id varchar(36) primary key,
    email varchar(255) unique not null,
    password_hash varchar(255) not null,
    account_type account_type_enum not null default 'personal',
    share_code varchar(6) unique,
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
    customer_name varchar(100),
    share_enabled boolean not null default false,
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
    cv_wellness double precision,
    wb_wellness double precision,
    brk_wellness double precision,
    bat_wellness double precision,
    alt_wellness double precision,
    sta_wellness double precision,
    coolant_wellness double precision,
    ignition_wellness double precision,
    fuel_wellness double precision,
    calculated_at timestamp with time zone default now()
);

alter table users add column if not exists business_name varchar(255);
alter table users add column if not exists full_name varchar(255);
alter table users add column if not exists share_code varchar(6);
alter table vehicles add column if not exists customer_name varchar(100);
alter table vehicles add column if not exists share_enabled boolean not null default false;
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

create table if not exists business_customer_links (
    id varchar(36) primary key,
    business_user_id varchar(36) not null references users(user_id) on delete cascade,
    customer_user_id varchar(36) not null references users(user_id) on delete cascade,
    created_at timestamp with time zone default now()
);

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'uq_business_customer_link'
          and conrelid = 'business_customer_links'::regclass
    ) then
        alter table business_customer_links
            add constraint uq_business_customer_link unique (business_user_id, customer_user_id);
    end if;
end $$;

do $$
declare
    r record;
    new_code varchar(6);
begin
    for r in select user_id from users where share_code is null loop
        loop
            new_code := lpad(floor(random() * 1000000)::int::text, 6, '0');
            exit when not exists (select 1 from users where share_code = new_code);
        end loop;
        update users set share_code = new_code where user_id = r.user_id;
    end loop;
end $$;

create unique index if not exists idx_users_share_code on users(share_code);
create index if not exists idx_vehicles_owner_id on vehicles(owner_id);
create index if not exists idx_vehicles_share_enabled on vehicles(share_enabled);
create index if not exists idx_predictions_vehicle_id on wellness_predictions(vehicle_id);
create index if not exists idx_predictions_calculated_at on wellness_predictions(calculated_at desc);
create index if not exists idx_scheduled_maintenance_vehicle_id on scheduled_maintenance(vehicle_id);
create index if not exists idx_component_replacements_vehicle_id on component_replacements(vehicle_id);
create index if not exists idx_business_customer_links_business on business_customer_links(business_user_id);
create index if not exists idx_business_customer_links_customer on business_customer_links(customer_user_id);

create table if not exists service_proposals (
    id varchar(36) primary key,
    business_user_id varchar(36) not null references users(user_id) on delete cascade,
    customer_user_id varchar(36) not null references users(user_id) on delete cascade,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    proposal_type varchar(20) not null,
    task_key varchar(50) not null,
    service_mileage integer not null,
    notes varchar(500),
    status varchar(20) not null default 'pending',
    created_at timestamp with time zone default now(),
    resolved_at timestamp with time zone
);

create index if not exists idx_service_proposals_customer on service_proposals(customer_user_id);
create index if not exists idx_service_proposals_business on service_proposals(business_user_id);
create index if not exists idx_service_proposals_vehicle  on service_proposals(vehicle_id);
create index if not exists idx_service_proposals_status   on service_proposals(status);

alter table service_proposals add column if not exists replacement_info varchar(500);
alter table service_proposals add column if not exists technician_name varchar(100);
alter table service_proposals add column if not exists cost numeric(10,2);

create table if not exists service_log (
    id varchar(36) primary key,
    vehicle_id varchar(36) not null references vehicles(vehicle_id) on delete cascade,
    entry_type varchar(20) not null,
    task_key varchar(50) not null,
    service_mileage integer not null,
    replacement_info varchar(500),
    shop_name varchar(100),
    technician_name varchar(100),
    cost numeric(10,2),
    notes varchar(500),
    logged_by_user_id varchar(36) references users(user_id) on delete set null,
    logged_at timestamp with time zone default now()
);

create index if not exists idx_service_log_vehicle   on service_log(vehicle_id);

create table if not exists pairing_codes (
    user_id    varchar(36) primary key references users(user_id) on delete cascade,
    code       varchar(5)  not null,
    expires_at timestamp with time zone not null
);

create unique index if not exists idx_pairing_codes_code on pairing_codes(code);
create index if not exists idx_service_log_entry_type on service_log(entry_type);
create index if not exists idx_service_log_task_key  on service_log(task_key);
create index if not exists idx_service_log_logged_at on service_log(logged_at desc);
