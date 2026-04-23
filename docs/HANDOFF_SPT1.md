# HANDOFF SPT1

## 1. Objetivo da thread

Executar a Sprint 1 do MVP do sistema de manutenção industrial.

Esta thread deve focar exclusivamente em colocar a base técnica do projeto em funcionamento, preparando o terreno para os módulos das próximas sprints.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Decisões já fechadas para esta sprint:

- frontend em `Next.js`
- backend em `FastAPI`
- banco `SQLite`
- ORM `SQLAlchemy`
- autenticação com `JWT`
- login por `username` ou `email`
- senha com hash
- perfis: `admin`, `gerente`, `operador`
- integração OpenAI ainda não é foco desta sprint
- `OPENAI_API_KEY` deve existir em `.env.example`, mas a integração real será feita mais à frente

---

## 3. Escopo da Sprint 1

### Infraestrutura

- estruturar o repositório com `frontend/` e `backend/`
- configurar ambiente local mínimo para execução
- preparar `.env.example`
- preparar setup inicial de banco

### Backend core

- subir a base do `FastAPI`
- configurar conexão com `SQLite`
- organizar estrutura inicial de app, configs e dependências
- criar base de models e schemas centrais

### Auth

- implementar login por `username` ou `email`
- implementar hash de senha
- implementar geração e validação de `JWT`
- proteger rotas privadas

### Frontend inicial

- criar tela de login
- integrar login com backend
- tratar estado autenticado
- implementar logout

### Seed inicial

- preparar usuários iniciais:
  - `Otávio` como admin
  - `Tainá` como gerente
  - `Michael`, `Leonardo` e `Murilo` como operadores
- criar equipes iniciais mínimas necessárias
- criar equipamentos iniciais mínimos para ambiente de teste

---

## 4. Entregáveis esperados

- projeto com frontend e backend organizados
- backend inicial funcional
- tela de login funcional
- autenticação funcionando ponta a ponta
- rotas privadas protegidas
- seed utilizável para testes locais
- `.env.example` documentando variáveis necessárias

---

## 5. Critérios de pronto da Sprint 1

A sprint pode ser considerada pronta quando:

- frontend e backend sobem localmente
- usuário seed consegue autenticar com sucesso
- senha não é armazenada em texto puro
- JWT é emitido e validado
- área autenticada fica protegida
- logout funciona
- perfis básicos já existem na base
- configuração sensível fica fora do código

---

## 6. Limites desta sprint

Não é objetivo da Sprint 1:

- implementar CRUD completo de usuários
- implementar CRUD de equipes
- implementar CRUD de equipamentos
- desenvolver ocorrências, medições ou OS
- integrar OpenAI de fato
- construir dashboard, relatórios ou alertas inteligentes

Se algum desses pontos exigir pequena preparação estrutural, isso pode ser feito sem expandir o escopo funcional.

---

## 7. Diretrizes de implementação

- priorizar simplicidade e base sólida
- evitar sobreengenharia
- manter código modular
- preparar o terreno para as sprints seguintes
- documentar rapidamente como subir o projeto
- se houver dúvida entre robustez futura e entrega rápida, favorecer uma solução simples, limpa e extensível

---

## 8. Saída esperada ao final da thread

Ao concluir a Sprint 1, devolver um handoff contendo:

- resumo do que foi implementado
- status da sprint
- pendências
- riscos ou decisões tomadas
- arquivos principais alterados
- como validar localmente
- o que fica pronto para a Sprint 2

Esse handoff será trazido de volta para a thread principal de planejamento.
