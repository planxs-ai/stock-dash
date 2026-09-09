-- One personal dashboard per deployment; access only via backend service key.
create table if not exists public.stock_dash_state (
  id text primary key,
  version bigint not null default 0,
  payload jsonb not null default '{}'::jsonb
);
alter table public.stock_dash_state enable row level security;
revoke all on public.stock_dash_state from anon, authenticated;
grant all on public.stock_dash_state to service_role;
insert into public.stock_dash_state(id, payload)
values ('personal', '{"stocks":[],"journal":[],"runs":[]}')
on conflict (id) do nothing;
