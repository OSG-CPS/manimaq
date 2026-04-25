# OPERACAO LOCAL

## 1. Objetivo

Este documento resume a operacao local do Manimaq para desenvolvimento, demonstracao e testes em rede local.

Usar este guia para:

- subir backend e frontend
- iniciar com seed de demonstracao
- iniciar sem seed usando bootstrap
- acessar pela LAN
- resetar banco
- resolver problemas rapidos de ambiente

---

## 2. Estrutura principal

- backend: `C:\dev\manimaq\backend`
- frontend: `C:\dev\manimaq\frontend`
- banco SQLite padrao: `C:\dev\manimaq\backend\data\manimaq.db`

---

## 3. Subir o backend

No diretório `backend`:

```powershell
cd C:\dev\manimaq\backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Para acesso pela LAN:

```powershell
cd C:\dev\manimaq\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. Subir o frontend

No diretório `frontend`:

```powershell
cd C:\dev\manimaq\frontend
npm install
npm run dev
```

---

## 5. Configuracao de `.env`

### Backend

Copiar:

```powershell
Copy-Item C:\dev\manimaq\backend\.env.example C:\dev\manimaq\backend\.env
```

Campos importantes:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`
- `CORS_ORIGIN_REGEX`
- `OPENAI_API_KEY`

### Frontend

Copiar:

```powershell
Copy-Item C:\dev\manimaq\frontend\.env.example C:\dev\manimaq\frontend\.env.local
```

Campo importante:

- `NEXT_PUBLIC_API_BASE_URL`

Valor padrao:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

Em acesso pela LAN, o frontend tenta reescrever automaticamente `localhost` para o hostname/IP atual do navegador.

---

## 6. Rodar com seed de demonstracao

O seed atual cria:

- usuarios e equipes base
- equipamentos com thresholds
- historico operacional de aproximadamente 6 meses
- ocorrencias
- medicoes
- alertas
- ordens de servico
- cenarios tranquilos, intermediarios e problematicos

Executar:

```powershell
cd C:\dev\manimaq\backend
python -m scripts.seed
```

Para recriar somente a massa operacional:

```powershell
cd C:\dev\manimaq\backend
python -m scripts.seed --reset-operational
```

---

## 7. Rodar sem seed usando bootstrap

Se o banco estiver vazio e voce subir backend + frontend sem rodar seed:

- a tela `/login` entra em modo de bootstrap
- o sistema permite criar o primeiro usuario administrador
- depois disso o acesso segue normalmente

Esse e o fluxo recomendado para inicializacao manual sem massa demonstrativa.

---

## 8. Usuarios seed padrao

Usuarios:

- `otavio`
- `taina`
- `michael`
- `leonardo`
- `murillo`
- `bruno`

Senha padrao:

- `Manimaq@123`

---

## 9. Reset do banco

Para apagar tudo:

```powershell
Remove-Item C:\dev\manimaq\backend\data\manimaq.db
```

Depois disso:

- se subir backend/frontend sem seed, o sistema pede bootstrap do primeiro admin
- se rodar o seed depois, a base demonstrativa e recriada

---

## 10. Acesso pela LAN

Exemplo:

- frontend: `http://192.168.0.100:3000`
- backend: `http://192.168.0.100:8000`

Checklist:

1. backend rodando com `--host 0.0.0.0`
2. frontend rodando normalmente
3. celular e computador na mesma rede
4. `NEXT_PUBLIC_API_BASE_URL` configurado ou reescrita automatica funcionando
5. firewall do Windows permitindo acesso nas portas usadas

---

## 11. Troubleshooting rapido

### 1. `Failed to fetch` no celular

Verificar:

- backend subiu em `0.0.0.0`, nao em `127.0.0.1`
- frontend nao esta preso em `localhost:8000` no celular
- CORS do backend esta carregando o `.env` correto

### 2. Tela mostra `sem dependencia da OpenAI`

Significa:

- a leitura analitica caiu em fallback local
- nao significa mock necessariamente
- verificar logs do backend para saber se houve:
  - chave ausente
  - timeout
  - erro HTTP
  - resposta nao parseavel

### 3. Banco vazio e sem login

Esperado se:

- voce apagou o banco
- nao rodou seed

Solucao:

- usar bootstrap pela tela de login
- ou rodar o seed

### 4. `next build` inconclusivo

Esse ainda e um ponto pendente do projeto.
O sistema ja foi usado em dev, tipagem e acesso LAN, mas a validacao final de build de producao ainda precisa de ambiente mais estavel.

---

## 12. Comandos uteis

### Backend com LAN

```powershell
cd C:\dev\manimaq\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
cd C:\dev\manimaq\frontend
npm run dev
```

### Seed completa

```powershell
cd C:\dev\manimaq\backend
python -m scripts.seed
```

### Regenerar historico operacional

```powershell
cd C:\dev\manimaq\backend
python -m scripts.seed --reset-operational
```

### Apagar banco

```powershell
Remove-Item C:\dev\manimaq\backend\data\manimaq.db
```
