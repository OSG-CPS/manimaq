## 1. Identificação

- Sprint: `SPT3`
- Thread: `Sprint 3 - ocorrencias, medicoes e historico por equipamento`
- Data: `2026-04-23`
- Responsável pela execução: `Codex`
- Status geral: `concluída`

---

## 2. Objetivo da sprint

Entregar a Sprint 3 do MVP habilitando o fluxo operacional básico do sistema com registro de `occurrences`, registro de `measurements` e consulta de `equipment-history`.

A sprint deveria destravar o uso diário do sistema no chão de fábrica, mantendo rastreabilidade por equipamento, autor e data/hora e deixando a base pronta para a Sprint 4 de ordens de serviço.

---

## 3. Resumo executivo

Foi entregue a base completa de ocorrências, medições e histórico por equipamento no backend e no frontend, com persistência em SQLite, autenticação reaproveitada da Sprint 2 e navegação integrada ao dashboard.

Também foi adicionada a possibilidade de informar a data/hora operacional real de ocorrências e medições: por padrão o campo entra com o horário atual, mas o usuário pode alterar para um horário anterior quando necessário.

O resultado deixa a Sprint 4 pronta para começar sobre uma base operacional funcional e rastreável. Ficou como limitação de validação desta thread apenas a checagem de frontend com TypeScript/build, que não pôde ser executada neste ambiente por bloqueio de execução local.

---

## 4. Entregas concluídas

- modelos, schemas e endpoints REST de `occurrences`
- modelos, schemas e endpoints REST de `measurements`
- endpoint de histórico consolidado por equipamento em `equipment-history`
- validação de existência de equipamento antes de criar ocorrência ou medição
- vínculo obrigatório de ocorrência e medição com equipamento e autor autenticado
- padronização de severidade de ocorrência com enum simples para uso futuro em alertas e OS
- formulário e listagem de ocorrências no frontend
- formulário e listagem de medições no frontend
- visão de histórico por equipamento no frontend
- destaque visual para ocorrência com parada de produção
- campo editável de data/hora operacional em ocorrências e medições, com preenchimento padrão no horário atual
- ajuste de layout da página de medições para manter o formulário ancorado no topo enquanto a lista cresce
- teste automatizado em arquivo cobrindo criação de ocorrência, criação de medição, consulta de histórico e validação de equipamento inexistente
- testes funcionais manuais confirmados pelo usuário

---

## 5. Entregas parciais

- validação automatizada do frontend com `tsc` ou `next build` não pôde ser concluída nesta sessão por bloqueio de execução de `node`/binários locais no ambiente

---

## 6. Itens não iniciados

- nenhum item central da Sprint 3 ficou sem início
- não foi iniciado escopo da Sprint 4 além do preparo estrutural natural dos dados

---

## 7. Decisões técnicas tomadas

- `occurrences` e `measurements` foram modeladas como entidades simples vinculadas diretamente a `equipment` e `user`, sem antecipar complexidade de alertas ou OS
- foi adotado um timestamp operacional separado do timestamp técnico: `occurred_at` para ocorrências e `measured_at` para medições, preservando `created_at` e `updated_at` para rastreabilidade interna
- o backend passou a normalizar esses timestamps para UTC explícito na resposta da API
- para compatibilidade com banco SQLite já existente, a inicialização do backend adiciona as colunas novas automaticamente quando necessário e preenche registros antigos com o valor de `created_at`
- regra de edição adotada para ocorrências: `admin` e `gerente` podem editar sempre; `operador` pode editar apenas ocorrência própria nas primeiras 24 horas
- operadores passaram a ter acesso aos módulos operacionais (`Ocorrencias`, `Medicoes`, `Historico`) sem acesso aos módulos administrativos da Sprint 2

Se alguma decisão alterou uma premissa anterior:
- sim; a sprint passou a distinguir claramente o horário operacional informado pelo usuário do horário técnico de persistência, o que não existia nas sprints anteriores

---

## 8. Estado atual do sistema

Hoje o sistema já funciona ponta a ponta em:
- login e sessão autenticada
- controle de acesso por perfil
- cadastros de equipes, equipamentos e usuários
- registro de ocorrências com severidade, risco, parada de produção, descrição, autor e data/hora operacional
- registro de medições com tipo, valor, unidade, autor e data/hora operacional
- consulta de histórico consolidado por equipamento

Funciona parcialmente em:
- validação técnica do frontend por `tsc`/`next build`, ainda não confirmada nesta thread

Ainda não existe:
- ordens de serviço
- histórico de status de OS
- alertas por regras
- alertas com IA
- dashboard real de KPIs
- relatórios analíticos

Já está preparado estruturalmente para a próxima sprint:
- base operacional rastreável por equipamento
- enums e flags úteis para priorização futura de OS
- histórico por equipamento pronto para ser usado no fluxo de abertura e análise de OS

---

## 9. Arquivos principais alterados

- `backend/app/models/occurrence.py`  
  modelagem de ocorrências
- `backend/app/models/measurement.py`  
  modelagem de medições
- `backend/app/api/routes/occurrences.py`  
  listagem, criação, detalhe e edição de ocorrências
- `backend/app/api/routes/measurements.py`  
  listagem e criação de medições
- `backend/app/api/routes/equipment_history.py`  
  histórico consolidado por equipamento
- `backend/app/schemas/occurrences.py`
- `backend/app/schemas/measurements.py`
- `backend/app/schemas/history.py`
- `backend/app/schemas/common.py`
- `backend/app/db/session.py`  
  criação automática de colunas novas no SQLite existente
- `backend/app/main.py`
- `frontend/app/dashboard/occurrences/page.tsx`
- `frontend/app/dashboard/measurements/page.tsx`
- `frontend/app/dashboard/history/page.tsx`
- `frontend/components/dashboard-shell.tsx`
- `frontend/app/dashboard/page.tsx`
- `frontend/app/globals.css`
- `backend/tests/test_sprint3_api.py`

---

## 10. Validação executada

### Comandos executados

- `python -m unittest backend.tests.test_sprint3_api`
- `python -c "import sys; sys.path.insert(0, r'C:\dev\manimaq\backend'); from app.main import app; print('app ok')"`

### Resultado da validação

Testado com sucesso:
- criação de ocorrência válida
- criação de medição válida
- retorno do histórico por equipamento
- rejeição de ocorrência com equipamento inexistente
- aceitação e retorno correto de `occurred_at` e `measured_at`
- testes funcionais manuais do frontend confirmados pelo usuário

Falhou:
- nenhum fluxo funcional principal da Sprint 3 falhou após os ajustes finais

Não pôde ser validado:
- `tsc --noEmit` no frontend
- `next build` no frontend

Motivo:
- o ambiente desta thread retornou `Access is denied` para execução de `node` e binários locais, impedindo a validação técnica do frontend

---

## 11. Pendências e riscos

- validar o frontend com `tsc --noEmit` fora desta thread
- validar `next build` em ambiente local estável
- revisar posteriormente a migração automática de colunas no SQLite para um mecanismo mais robusto quando o projeto crescer
- acompanhar se a regra de edição de ocorrência em 24h continua adequada quando a Sprint 4 introduzir OS e fluxo operacional mais rígido

---

## 12. Limitações conhecidas

- medições continuam com modelo simplificado de um valor por registro, sem agrupar múltiplos tipos em uma única coleta
- não há edição de medições nesta sprint
- não há paginação nas listagens de ocorrências e medições
- a migração de esquema está simplificada no `init_db`, suficiente para o MVP local, mas não substitui ferramenta formal de migração

---

## 13. Recomendações para a próxima sprint

- começar a Sprint 4 pela modelagem de `work-orders` e do histórico de mudança de status
- reutilizar o histórico por equipamento como contexto principal da criação e análise de OS
- manter o mesmo padrão de rastreabilidade por autor e data/hora em qualquer transição de status da OS
- decidir logo no início da Sprint 4 como `gerente` aprova, prioriza e encaminha OS com base em ocorrências e medições

---

## 14. Instruções para continuidade

Ordem recomendada de continuidade:
- revisar rapidamente os novos endpoints de `occurrences`, `measurements` e `equipment-history`
- modelar `work-orders` com vínculo obrigatório a equipamento e equipe
- implementar histórico de status de OS
- conectar a criação de OS ao contexto operacional já presente no frontend

Dependências já prontas:
- autenticação JWT
- controle de acesso por perfil
- CRUDs administrativos da Sprint 2
- fluxo operacional de ocorrências e medições
- histórico consolidado por equipamento

Pontos que precisam ser revistos antes de seguir:
- confirmar build e checagem TypeScript do frontend em ambiente sem bloqueio de execução
- decidir se medições continuarão como registros unitários por tipo ou se a Sprint 4 exigirá agrupamento por coleta

Atenções especiais:
- o banco SQLite pode já conter registros antigos; as novas colunas `occurred_at` e `measured_at` são preenchidas automaticamente com `created_at` quando ausentes
- `created_at` e `updated_at` devem continuar sendo tratados como rastreabilidade técnica, não como hora operacional do evento

---

## 15. Bloco final resumido

- Sprint encerrada com: fluxo operacional básico de ocorrências, medições e histórico por equipamento funcionando ponta a ponta
- Próxima sprint recomendada: `Sprint 4 - ordens de serviço e histórico de status`
- Principal pendência: validar o frontend com `tsc` e `next build` em ambiente local estável
- Principal risco: seguir sem validação técnica de build do frontend pode esconder regressão entre uso manual e build de produção
- Projeto está pronto para continuar? `sim`
