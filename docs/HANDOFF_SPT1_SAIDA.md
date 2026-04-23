# HANDOFF DE SAIDA - SPRINT 1

## Resumo do objetivo da sprint

Colocar o projeto em funcionamento com base tecnica inicial, autenticacao ponta a ponta, estrutura de dados inicial e seed para ambiente local.

## Status geral

Parcial

## Entregas concluidas

- Estrutura inicial do repositorio criada com `frontend/` e `backend/`
- Backend FastAPI configurado com:
  - carregamento por `.env`
  - conexao SQLite
  - models iniciais de `users`, `teams` e `equipments`
  - schemas de autenticacao
  - login por `username` ou `email`
  - hash de senha no backend
  - emissao e validacao de JWT
  - rota autenticada de validacao (`/api/dashboard-summary`)
  - rota `/api/auth/me`
- Seed inicial implementado com:
  - usuarios base
  - equipes iniciais
  - equipamentos iniciais de teste
- Frontend Next.js estruturado com:
  - tela de login
  - integracao com backend
  - persistencia de sessao em `localStorage`
  - protecao da area autenticada
  - logout
- `.env.example` criado para backend e frontend
- `README.md` criado com passos basicos para subir o projeto

## Entregas parciais

- Frontend teve dependencias instaladas e `next build` validado com sucesso, mas o fluxo visual completo em navegador ainda nao foi exercitado nesta thread

## Itens nao iniciados

- CRUD de usuarios
- CRUD de equipes
- CRUD de equipamentos
- qualquer fluxo de ocorrencias, medicoes, OS, dashboard real ou IA

## Decisoes tecnicas tomadas

- Autenticacao com JWT e dependencia FastAPI para proteger rotas privadas
- Hash de senha usando `passlib` com `pbkdf2_sha256`
- Banco SQLite configurado em `backend/data/manimaq.db`
- Seed idempotente para popular ambiente local sem duplicar registros
- Frontend com App Router do Next.js e guarda de rota no cliente para manter a Sprint 1 simples
- Campo `email` no schema de resposta ficou como `str`, sem validacao forte nesta sprint, para nao bloquear o fluxo com dominios locais dos seeds

## Pendencias e riscos

- O frontend passou em build, mas ainda falta smoke test manual em navegador com backend rodando ao mesmo tempo
- A validacao do backend exigiu instalacao de dependencias e seed fora do sandbox
- O arquivo de banco antigo em `backend/manimaq.db` ficou travado pelo ambiente; a configuracao foi movida para `backend/data/manimaq.db`
- Validacoes mais fortes de cadastro, regras de autorizacao por perfil e testes automatizados ainda nao existem
- `next@15.3.1` acusou vulnerabilidade conhecida durante o `npm install`; convem atualizar para uma versao corrigida no inicio da Sprint 2

## Arquivos principais alterados

- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/security.py`
- `backend/app/api/deps.py`
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/protected.py`
- `backend/app/models/user.py`
- `backend/app/models/team.py`
- `backend/app/models/equipment.py`
- `backend/app/schemas/auth.py`
- `backend/scripts/seed.py`
- `frontend/app/login/page.tsx`
- `frontend/app/dashboard/page.tsx`
- `frontend/components/auth-guard.tsx`
- `frontend/components/logout-button.tsx`
- `frontend/lib/auth.ts`
- `README.md`

## Comandos de validacao executados

- `python -m pip install --target .packages -r requirements.txt`
- `python -m scripts.seed`
- `npm install`
- `next build`
- teste local com `fastapi.testclient` cobrindo:
  - login com seed
  - leitura de `/api/auth/me`
  - leitura de rota protegida com token
  - bloqueio de rota protegida sem token

## Limitacoes conhecidas

- Sem testes automatizados salvos em arquivo
- Sem middleware de permissao por perfil alem da autenticacao
- Sessao do frontend usa `localStorage`, sem cookies HTTP-only
- Sem refresh token
- Sem setup automatizado de dependencias do frontend no ambiente atual

## Recomendacao objetiva para a proxima sprint

Usar esta base para implementar os CRUDs de `users`, `teams` e `equipments`, aproveitando:

- models ja criados
- autenticao ja pronta
- seed inicial funcional
- area autenticada do frontend como ponto de entrada para os modulos de cadastro
