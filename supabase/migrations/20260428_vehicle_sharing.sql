-- Adds customer-to-business vehicle sharing.
-- Safe to run more than once.

alter table users add column if not exists share_code varchar(6);

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

        update users
        set share_code = new_code
        where user_id = r.user_id;
    end loop;
end $$;

create unique index if not exists idx_users_share_code on users(share_code);

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'chk_users_share_code_digits'
          and conrelid = 'users'::regclass
    ) then
        alter table users
            add constraint chk_users_share_code_digits
            check (share_code is null or share_code ~ '^[0-9]{6}$');
    end if;
end $$;

alter table vehicles add column if not exists share_enabled boolean not null default false;

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
            add constraint uq_business_customer_link
            unique (business_user_id, customer_user_id);
    end if;
end $$;

create index if not exists idx_business_customer_links_business on business_customer_links(business_user_id);
create index if not exists idx_business_customer_links_customer on business_customer_links(customer_user_id);
create index if not exists idx_vehicles_share_enabled on vehicles(share_enabled);
