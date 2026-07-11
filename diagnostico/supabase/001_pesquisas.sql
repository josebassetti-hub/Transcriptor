-- ============================================================================
-- Diagnóstico · Pesquisa Clínica — migração 001
-- Tabela de histórico de pesquisas + RLS (cada usuário só vê as próprias).
-- Aplicar no projeto Supabase (SQL Editor ou MCP apply_migration).
-- ============================================================================

create table if not exists public.pesquisas (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users(id) on delete cascade,
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  doenca        text not null check (char_length(doenca) between 1 and 200),
  -- LGPD: minimização — apenas iniciais/código do paciente dentro do jsonb; nunca nome completo.
  -- {iniciais, idade, sexo, queixa, sintomas, comorbidades, medicamentos, alergias, gestante, exames}
  paciente      jsonb not null default '{}'::jsonb,
  estrategia    jsonb,                                  -- saída da chamada #1 {doenca_en, sinonimos, queries...}
  fontes        jsonb not null default '[]'::jsonb,     -- [{tipo, fonte, titulo, ano, url, id}] usadas na síntese
  relatorio     text,                                   -- markdown completo do relatório
  checklist     jsonb not null default '[]'::jsonb,     -- [{i, texto, feito}]
  modelo        text,                                   -- ex.: claude-sonnet-5
  profundidade  text not null default 'padrao',         -- rapida | padrao | profunda
  status        text not null default 'concluida'       -- concluida | sem_fontes | parcial
);

alter table public.pesquisas enable row level security;

-- Políticas: dono é quem lê/escreve/atualiza/apaga a própria linha.
drop policy if exists "pesquisas_select_own" on public.pesquisas;
create policy "pesquisas_select_own" on public.pesquisas
  for select to authenticated using (auth.uid() = user_id);

drop policy if exists "pesquisas_insert_own" on public.pesquisas;
create policy "pesquisas_insert_own" on public.pesquisas
  for insert to authenticated with check (auth.uid() = user_id);

drop policy if exists "pesquisas_update_own" on public.pesquisas;
create policy "pesquisas_update_own" on public.pesquisas
  for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "pesquisas_delete_own" on public.pesquisas;
create policy "pesquisas_delete_own" on public.pesquisas
  for delete to authenticated using (auth.uid() = user_id);

create index if not exists pesquisas_user_criado on public.pesquisas (user_id, criado_em desc);

-- atualizado_em automático em qualquer update (ex.: marcar item do checklist).
create or replace function public.tg_touch() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  new.atualizado_em := now();
  return new;
end $$;

drop trigger if exists pesquisas_touch on public.pesquisas;
create trigger pesquisas_touch before update on public.pesquisas
  for each row execute function public.tg_touch();
