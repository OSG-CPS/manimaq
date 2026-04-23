# Manimaq

MVP de manutencao de maquinas industriais organizado em `frontend/` e `backend/`.

## Stack

- Frontend: Next.js
- Backend: FastAPI
- Banco: SQLite
- Autenticacao: JWT com hash de senha no backend

## Estrutura

- `frontend/`: tela de login, area autenticada inicial e logout
- `backend/`: API FastAPI, SQLite, auth, models centrais e seed inicial
- `docs/`: contexto do projeto e handoffs

## Como subir o backend

1. Criar ambiente virtual em `backend/`.
2. Instalar dependencias com `pip install -r requirements.txt`.
3. Copiar `backend/.env.example` para `backend/.env`.
4. Executar o seed com `python -m scripts.seed`.
5. Subir a API com `uvicorn app.main:app --reload`.

## Como subir o frontend

1. Instalar dependencias em `frontend/`.
2. Copiar `frontend/.env.example` para `frontend/.env.local`.
3. Rodar `npm run dev`.

## Seed inicial

Usuarios:

- `otavio` / `otavio@manimaq.local`
- `taina` / `taina@manimaq.local`
- `michael` / `michael@manimaq.local`
- `leonardo` / `leonardo@manimaq.local`
- `murillo` / `murillo@manimaq.local`

Senha padrao para todos: `Manimaq@123`

## Observacao

O banco SQLite padrao fica em `backend/data/manimaq.db`.
