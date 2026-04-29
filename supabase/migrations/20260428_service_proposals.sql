-- Adds business-to-customer service proposal workflow.
-- Safe to run more than once.

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
