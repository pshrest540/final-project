-- Time-limited pairing codes for secure business-customer linking.
-- Safe to run more than once.

create table if not exists pairing_codes (
    user_id    varchar(36) primary key references users(user_id) on delete cascade,
    code       varchar(5)  not null,
    expires_at timestamp with time zone not null
);

create unique index if not exists idx_pairing_codes_code on pairing_codes(code);
