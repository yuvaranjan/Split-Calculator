-- Production schema for the notebook model. Run through Supabase migrations.
create extension if not exists pgcrypto;

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default 'Local profile',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table public.notebooks (
  id uuid primary key default gen_random_uuid(), owner_id uuid not null references public.profiles(id) on delete cascade,
  name text not null, type text not null default 'Custom', icon text, color text, currency text not null default 'INR',
  start_date date, end_date date, notes text, archived boolean not null default false,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table public.notebook_members (
  notebook_id uuid not null references public.notebooks(id) on delete cascade,
  user_id uuid references public.profiles(id) on delete set null,
  person_id uuid not null default gen_random_uuid(), name text not null, active boolean not null default true,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  primary key (notebook_id, person_id)
);
create table public.notebook_access (
  notebook_id uuid not null references public.notebooks(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  role text not null check (role in ('owner','editor','viewer')),
  created_at timestamptz not null default now(), primary key (notebook_id, user_id)
);
create table public.transactions (
  id uuid primary key default gen_random_uuid(), notebook_id uuid not null references public.notebooks(id) on delete cascade,
  kind text not null check (kind in ('expense','transfer')), transaction_date date not null,
  category text not null, description text not null, amount numeric(12,2) not null check (amount > 0),
  payer_id uuid not null, payer_name_snapshot text not null, split_type text not null,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table public.transaction_shares (
  transaction_id uuid not null references public.transactions(id) on delete cascade,
  person_id uuid not null, person_name_snapshot text not null, amount numeric(12,2) not null check (amount >= 0),
  primary key (transaction_id, person_id)
);
create index transactions_notebook_date_idx on public.transactions(notebook_id, transaction_date desc);
create index shares_person_idx on public.transaction_shares(person_id);

alter table public.profiles enable row level security;
alter table public.notebooks enable row level security;
alter table public.notebook_members enable row level security;
alter table public.notebook_access enable row level security;
alter table public.transactions enable row level security;
alter table public.transaction_shares enable row level security;

create policy "profile owner" on public.profiles for all using (id = auth.uid()) with check (id = auth.uid());
create policy "notebook members can read" on public.notebooks for select using (owner_id = auth.uid() or exists (select 1 from public.notebook_access a where a.notebook_id = id and a.user_id = auth.uid()));
create policy "notebook owner can write" on public.notebooks for all using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "access members" on public.notebook_access for select using (user_id = auth.uid() or exists (select 1 from public.notebooks n where n.id = notebook_id and n.owner_id = auth.uid()));
create policy "scoped members" on public.notebook_members for all using (exists (select 1 from public.notebooks n where n.id = notebook_id and (n.owner_id = auth.uid() or exists (select 1 from public.notebook_access a where a.notebook_id = n.id and a.user_id = auth.uid() and a.role in ('owner','editor'))))) with check (exists (select 1 from public.notebooks n where n.id = notebook_id and (n.owner_id = auth.uid() or exists (select 1 from public.notebook_access a where a.notebook_id = n.id and a.user_id = auth.uid() and a.role in ('owner','editor')))));
create policy "scoped transactions" on public.transactions for all using (exists (select 1 from public.notebooks n where n.id = notebook_id and (n.owner_id = auth.uid() or exists (select 1 from public.notebook_access a where a.notebook_id = n.id and a.user_id = auth.uid() and a.role in ('owner','editor','viewer'))))) with check (exists (select 1 from public.notebooks n where n.id = notebook_id and (n.owner_id = auth.uid() or exists (select 1 from public.notebook_access a where a.notebook_id = n.id and a.user_id = auth.uid() and a.role in ('owner','editor')))));
create policy "scoped shares" on public.transaction_shares for select using (exists (select 1 from public.transactions t where t.id = transaction_id));
