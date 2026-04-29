-- Adds rich service history log and extends proposals with detail fields.
-- Safe to run more than once.

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

create index if not exists idx_service_log_vehicle    on service_log(vehicle_id);
create index if not exists idx_service_log_entry_type on service_log(entry_type);
create index if not exists idx_service_log_task_key   on service_log(task_key);
create index if not exists idx_service_log_logged_at  on service_log(logged_at desc);
