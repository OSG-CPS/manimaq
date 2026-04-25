# HANDOFF GERAL

## 1. Objetivo deste documento

Este documento serve como contexto-base para abertura de novas threads no Codex durante o desenvolvimento do MVP do sistema de manutenção de máquinas industriais.

Cada sprint deve ser executada em uma thread nova.
Ao final de cada sprint, a thread responsável deve devolver um handoff de saída com:

- o que foi implementado
- o que ficou parcial
- o que não foi iniciado
- estado atual do projeto
- pendências, riscos e decisões tomadas
- arquivos principais alterados
- instruções para continuidade

Esse handoff de saída será trazido de volta para a thread principal de planejamento, onde a sprint seguinte será preparada.

---

## 2. Fontes oficiais do projeto

Antes de iniciar qualquer sprint, considerar como referência principal os arquivos:

- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Este `HANDOFF_GERAL.md` consolida as decisões mais recentes e deve ser usado como ponto de partida entre threads.

---

## 2.1 Estado atual consolidado

Neste momento, o projeto já concluiu o bloco principal do MVP, incluindo:

- autenticação com JWT
- bootstrap inicial do primeiro administrador quando o banco está vazio
- CRUD de usuários, equipes e equipamentos
- ocorrências, medições e histórico por equipamento
- ordens de serviço com histórico de status
- alertas por regras
- thresholds por equipamento
- abertura manual de OS a partir de alerta
- dashboard com KPIs reais
- relatórios básicos
- leitura analítica com IA na área de relatórios
- relatório de tendências por equipamento e por setor

Pendências principais de acabamento:

- validar `next build` em ambiente estável
- pente fino funcional e visual da área de relatórios e tendências
- calibrar linguagem e classificação assistiva da camada analítica
- decidir se haverá exportação simples de relatórios no acabamento do MVP

---

## 3. Visão do produto

Sistema web responsivo, para uso em rede local, acessível por desktop e celular, com foco em:

- cadastro de usuários, equipes e equipamentos
- registro de ocorrências e medições
- criação e acompanhamento de ordens de serviço
- dashboard com KPIs
- relatórios com apoio de IA
- alertas híbridos com regras e análise por IA

---

## 4. Escopo do MVP

O MVP deve permitir:

- autenticação com perfis
- cadastro de usuários, equipes e equipamentos
- registro de ocorrências e medições
- histórico por equipamento
- criação e acompanhamento de OS
- alertas com regras determinísticas e análise assistida por IA
- sugestão de abertura de OS, com decisão final do gerente
- dashboard com KPIs básicos
- relatórios com leitura facilitada por IA

Fora do MVP inicial:

- app nativo
- integrações com ERP/CMMS
- analytics avançado
- automação plena da decisão de manutenção

---

## 5. Decisões já adotadas

### Stack e arquitetura

- frontend: `Next.js`
- backend: `FastAPI`
- servidor: `Uvicorn`
- banco: `SQLite`
- ORM: `SQLAlchemy`
- organização: `frontend/` e `backend/` no mesmo repositório
- API no padrão REST

### Autenticação e segurança

- autenticação por `username` ou `email` + senha
- senha com hash no backend
- autenticação com `JWT`
- quando o banco estiver vazio, o sistema deve permitir bootstrap do primeiro administrador pela tela de login
- chave da OpenAI armazenada em `.env`
- nome esperado da variável: `OPENAI_API_KEY`
- frontend nunca deve chamar a OpenAI diretamente
- integração com OpenAI fica encapsulada no backend

### IA

- modelo adotado para todas as etapas com IA: `gpt-5.4-mini`
- IA apoia análise e decisão humana, não executa decisão crítica sozinha
- abertura de OS pode ser sugerida pelo sistema, mas a decisão final é do gerente
- sistema deve continuar funcional mesmo se a integração com IA falhar

### Perfis

- `admin`: acesso total
- `gerente`: operação ampla, acompanhamento, criação/encaminhamento/priorização de OS
- `operador`: execução operacional, registros e atuação conforme permissão

### Regras operacionais assumidas

- equipamento deve ter `TAG` única
- usuário deve estar vinculado a equipe ativa
- exclusões devem priorizar desativação/inativação, não remoção física
- email de usuário não pode duplicar
- nome de equipe deve ser único
- equipes inativas não podem receber novos vínculos
- OS sempre vinculada a equipamento e equipe
- toda ocorrência e medição precisa registrar autor e data/hora
- toda mudança relevante de status da OS deve gerar histórico

### Escopo simplificado adotado

- QR code fica fora do MVP inicial
- exportação inicial simples
- IA não substitui regras determinísticas
- UI pode ser simples, desde que funcional e responsiva
- seed histórica de 6 meses existe apenas para ambiente de demonstração/teste e não é obrigatória para bootstrap do sistema

---

## 6. Usuários, perfis e seeds iniciais

Usuários de referência para seed inicial:

- `Otávio` — administrador
- `Tainá` — gerente
- `Michael` — operador
- `Leonardo` — operador
- `Murillo` — operador

Setores iniciais:

- Administração
- Produção
- Expedição
- Manutenção
- Utilidades

Exemplos de TAGs/equipamentos por setor:

- Administração: `PC-01`, `LAMP-01`, `TOM-01`
- Produção: `MAQ-01`
- Expedição: `EMP-01`, `PLT-01`
- Utilidades: `COMP-01`, `GER-01`, `AR-01`

---

## 7. Módulos previstos

- `auth`
- `users`
- `teams`
- `equipments`
- `occurrences`
- `measurements`
- `work-orders`
- `alerts-rules`
- `alerts-ai`
- `reports`
- `reports-ai`
- `dashboard`

---

## 8. Roadmap consolidado

### Sprint 1

- base do projeto
- autenticação
- estrutura inicial de dados
- seeds

### Sprint 2

- CRUD de usuários
- CRUD de equipes
- CRUD de equipamentos
- permissões e consistência de cadastros

### Sprint 3

- ocorrências
- medições
- histórico por equipamento

### Sprint 4

- ordens de serviço
- fluxo operacional e histórico de status

### Sprint 5

- alertas por regras
- enriquecimento opcional por IA
- sugestão de OS para decisão do gerente
- thresholds por equipamento
- fluxo gerencial de abertura manual de OS a partir do alerta
- edição de OS ainda aberta para correção operacional

### Sprint 6

- dashboard
- KPIs
- relatórios básicos
- consolidação visual e operacional dos dados já disponíveis
- sem IA pesada como foco principal

### Sprint 7

- alertas com IA mais madura
- análise de comportamento e tendência
- leitura analítica por IA
- refinamento gerencial das recomendações e análises

### Pós-S7.5

- pente fino funcional
- calibracao analitica
- validacao final de build
- eventual exportacao simples de relatorios

Todas as sprints de S1 a S7.5 já foram concluídas no fluxo atual de desenvolvimento.

---

## 9. Regras para novas threads de sprint

Ao abrir uma nova thread:

1. ler este arquivo e os documentos numerados em `docs/`
2. assumir somente a sprint atual como foco principal
3. não avançar para escopos de sprints futuras sem necessidade
4. preservar decisões já adotadas, salvo instrução explícita em contrário
5. ao fim, produzir handoff de saída claro e reutilizável

---

## 10. Formato esperado do handoff de saída de cada sprint

Ao concluir uma sprint, o handoff devolvido para a thread principal deve conter:

- resumo do objetivo da sprint
- status geral: concluído, parcial ou bloqueado
- entregas concluídas
- entregas parciais
- itens não iniciados
- decisões técnicas tomadas durante a execução
- pendências e riscos
- arquivos principais alterados
- comandos de validação executados
- limitações conhecidas
- recomendação objetiva para a próxima sprint

---

## 11. Diretriz de execução

Priorizar sempre:

- funcionamento ponta a ponta
- simplicidade de implementação
- consistência do modelo de dados
- controle de acesso por perfil
- rastreabilidade operacional
- base pronta para a camada de IA nas sprints posteriores
- clareza de documentação para operação local e em LAN

Este projeto deve evoluir sprint a sprint, com handoffs curtos, claros e reaproveitáveis entre threads.
