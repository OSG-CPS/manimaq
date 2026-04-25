# Manimaq

MVP de manutencao de maquinas industriais organizado em `frontend/` e `backend/`.

## Stack

- Frontend: Next.js
- Backend: FastAPI
- Banco: SQLite
- Autenticacao: JWT com hash de senha no backend
- IA analitica: OpenAI API (`gpt-5.4-mini`) com fallback local deterministico

## Estrutura

- `frontend/`: login, bootstrap inicial, dashboard, relatorios e modulos operacionais
- `backend/`: API FastAPI, SQLite, auth, models centrais, analytics e seed historica
- `docs/`: contexto do projeto e handoffs

## Como subir o backend

1. Criar ambiente virtual em `backend/`.
2. Instalar dependencias com `pip install -r requirements.txt`.
3. Copiar `backend/.env.example` para `backend/.env`.
4. Opcional: executar o seed com `python -m scripts.seed`.
5. Subir a API com `uvicorn app.main:app --reload`.

Para acesso pela LAN, subir com:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Como subir o frontend

1. Instalar dependencias em `frontend/`.
2. Copiar `frontend/.env.example` para `frontend/.env.local`.
3. Rodar `npm run dev`.

Em acesso pela LAN, o frontend tenta reescrever automaticamente `localhost` para o hostname/IP atual do navegador quando `NEXT_PUBLIC_API_BASE_URL` estiver apontando para `http://localhost:8000/api`.

## Bootstrap inicial sem seed

Se o banco estiver vazio e voce subir backend + frontend sem rodar seed:

- a tela de login entra em modo de bootstrap
- o sistema permite criar o primeiro usuario `admin`
- apos isso, o acesso segue normalmente sem depender de massa inicial

Esse e o fluxo recomendado para primeira inicializacao manual.

## Seed de demonstracao

O script `python -m scripts.seed` agora pode criar:

- equipes e usuarios base
- equipamentos com thresholds
- historico operacional de aproximadamente 6 meses
- ocorrencias, medicoes, alertas e ordens de servico
- cenarios tranquilos, intermediarios e problematicos
- OS da ultima semana abertas, em execucao e concluidas

Comportamento:

- se o historico operacional ja existir, o script nao duplica dados
- para regenerar a massa operacional, use `--reset-operational`

Exemplos:

```powershell
cd C:\dev\manimaq\backend
python -m scripts.seed
python -m scripts.seed --reset-operational
```

## Usuarios seed padrao

Usuarios:

- `otavio` / `otavio@manimaq.local`
- `taina` / `taina@manimaq.local`
- `michael` / `michael@manimaq.local`
- `leonardo` / `leonardo@manimaq.local`
- `murillo` / `murillo@manimaq.local`
- `bruno` / `bruno@manimaq.local`

Senha padrao para todos: `Manimaq@123`

## Reset rapido do banco

Para apagar tudo e recomecar:

```powershell
Remove-Item C:\dev\manimaq\backend\data\manimaq.db
```

Depois disso:

- se rodar apenas backend/frontend, o sistema sobe com banco vazio e pede bootstrap do primeiro admin
- se rodar o seed depois, a base demonstrativa e recriada

## Observacoes

O banco SQLite padrao fica em `backend/data/manimaq.db`.

A principal pendencia tecnica atual do projeto e validar `next build` em ambiente estavel, pois o uso em desenvolvimento e na LAN ja foi exercitado, mas a validacao de build de producao ficou inconclusiva no ambiente de execucao das threads.
