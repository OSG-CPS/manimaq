
# Handoff Inicial — Software para Análise de Falhas em Maquinário Industrial

## 1. Visão do produto

Sistema web responsivo para uso em **rede local**, acessível por **PC e celular**, com foco em:

* cadastro de usuários, equipes e equipamentos;
* registro de ocorrências e medições;
* geração e acompanhamento de ordens de serviço;
* visualização de KPIs e relatórios;
* alertas automáticos baseados em regras;
* preparação para futura camada de IA.

---

## 2. Objetivo do MVP

Entregar, em 4 semanas, uma solução funcional que permita:

1. cadastrar equipamentos, equipes e usuários;
2. registrar ocorrências e medições de equipamentos;
3. gerar OS manualmente e também automaticamente por regras simples;
4. acompanhar status das OS;
5. visualizar indicadores básicos de manutenção.

**Fora do MVP inicial**

* predição avançada com IA;
* integrações com ERP/CMMS;
* app nativo;
* analytics avançado.

---

## 3. Problema que o sistema resolve

Hoje o processo de manutenção tende a ser disperso, manual ou pouco rastreável.
O sistema deve centralizar:

* identificação de falhas;
* histórico por equipamento;
* tomada de decisão para manutenção;
* emissão e retorno de OS;
* acompanhamento de eficiência operacional.

---

## 4. Perfis de usuário

### Admin

* gerencia usuários, equipes, equipamentos;
* configura regras e parâmetros;
* acessa todos os relatórios.

### Gerente

* acompanha indicadores;
* aprova/prioriza OS;
* consulta histórico e desempenho.

### Operador

* registra ocorrência e medições;
* consulta equipamentos;
* executa/retorna OS conforme permissão.

---

## 5. Escopo funcional do MVP

### 5.1 Cadastro

**Usuários**

* nome
* login
* senha
* perfil: admin, gerente, operador
* setor

**Equipes**

* nome
* setor
* função/responsabilidade

**Equipamentos**

* TAG/código único
* nome
* setor
* criticidade
* status
* fabricante/modelo opcional

---

### 5.2 Registro operacional

**Ocorrências**

* equipamento
* data/hora
* usuário responsável pelo registro
* risco à segurança? (sim/não)
* parada de produção? (sim/não)
* grau de severidade
* descrição

**Medições**

* equipamento
* data/hora
* temperatura
* tensão
* corrente
* ruído
* vibração
* horímetro
* data prevista para próxima atuação
* observações

---

### 5.3 Ordens de serviço (OS)

Campos mínimos:

* identificador
* equipamento
* equipe responsável
* prioridade
* data de início prevista
* duração estimada
* tipo: corretiva ou preventiva
* status: aberta, em execução, concluída, cancelada
* descrição do serviço
* origem: manual ou automática

Funções:

* criar OS manualmente;
* sugerir/criar OS por regra;
* editar status;
* registrar retorno/conclusão;
* manter histórico.

---

### 5.4 Relatórios e indicadores

KPIs mínimos:

* quantidade de OS abertas / concluídas;
* % corretiva vs preventiva;
* tempo médio de atendimento;
* quantidade de ocorrências por equipamento;
* equipamentos com maior recorrência de falha.

Relatórios:

* por período;
* por equipamento;
* por equipe;
* por tipo de manutenção.

---

### 5.5 Alertas automáticos

No MVP, **não usar IA preditiva real**.
Implementar motor simples baseado em regras, por exemplo:

* vibração acima do limite → alerta;
* temperatura acima do limite → alerta;
* ocorrência com severidade alta → sugerir OS imediata;
* risco à segurança = sim → prioridade alta;
* parada de produção = sim → prioridade crítica.

---

## 6. Fluxo principal do usuário

1. usuário faz login;
2. acessa painel inicial;
3. cadastra ou consulta equipamento;
4. registra ocorrência ou medição;
5. sistema avalia regras;
6. sistema sugere ou cria OS;
7. equipe executa serviço;
8. responsável finaliza OS com retorno;
9. gerente acompanha KPIs e relatórios.

---

## 7. Regras de negócio iniciais

* cada equipamento deve possuir **TAG única**;
* somente admin pode cadastrar usuários;
* gerente e admin podem visualizar relatórios consolidados;
* operador pode registrar ocorrências e medições;
* OS automática deve ser criada apenas quando uma regra objetiva for satisfeita;
* toda OS deve estar vinculada a um equipamento;
* toda ocorrência e medição deve ter data/hora e autor do registro;
* mudança de status da OS deve ficar registrada em histórico.

---

## 8. Requisitos não funcionais

* aplicação web responsiva;
* acesso por navegador em desktop e celular;
* tempo de resposta alvo: até 3 segundos nas operações comuns;
* autenticação por login e senha;
* controle de acesso por perfil;
* backup periódico;
* persistência confiável dos dados;
* execução em rede local;
* logs básicos para auditoria.

**Observação**: disponibilidade de **99,9%** pode ser mantida como meta, mas para MVP não deve virar impeditivo de arquitetura.

---

## 9. Suposições técnicas para o Codex

Como ponto de partida, o Codex pode assumir:

### Arquitetura sugerida

* frontend web responsivo;
* backend com API REST;
* banco relacional.

### Estrutura sugerida de módulos

* auth
* users
* teams
* equipments
* occurrences
* measurements
* work-orders
* reports
* alerts-rules

### Stack sugerida

Pode seguir qualquer stack web moderna.
Sugestão simples para produtividade:

* **Frontend**: React / Next.js
* **Backend**: Node.js + NestJS ou Express
* **Banco**: PostgreSQL
* **ORM**: Prisma ou TypeORM

Se quiser máxima simplicidade:

* frontend + backend fullstack no mesmo projeto.

---

## 10. Entidades principais

### User

* id
* name
* login
* password_hash
* role
* sector
* created_at

### Team

* id
* name
* sector
* function
* created_at

### Equipment

* id
* tag
* name
* sector
* criticality
* status
* created_at

### Occurrence

* id
* equipment_id
* user_id
* timestamp
* safety_risk
* production_stop
* severity
* description

### Measurement

* id
* equipment_id
* user_id
* timestamp
* temperature
* voltage
* current
* noise
* vibration
* hourmeter
* next_action_date
* notes

### WorkOrder

* id
* equipment_id
* team_id
* type
* priority
* start_date
* estimated_duration
* status
* description
* origin
* created_by
* closed_by
* closed_at

### Alert

* id
* equipment_id
* type
* severity
* message
* generated_from
* created_at

---

## 11. API mínima esperada

### Auth

* POST /auth/login

### Users

* GET /users
* POST /users
* PUT /users/:id

### Teams

* GET /teams
* POST /teams
* PUT /teams/:id

### Equipments

* GET /equipments
* POST /equipments
* GET /equipments/:id
* PUT /equipments/:id

### Occurrences

* GET /occurrences
* POST /occurrences

### Measurements

* GET /measurements
* POST /measurements

### Work Orders

* GET /work-orders
* POST /work-orders
* PUT /work-orders/:id
* PATCH /work-orders/:id/status

### Reports

* GET /reports/kpis
* GET /reports/work-orders
* GET /reports/equipments

### Alerts

* GET /alerts
* POST /alerts/evaluate

---

## 12. Telas mínimas

* login
* dashboard
* cadastro de usuários
* cadastro de equipes
* cadastro de equipamentos
* registro de ocorrência
* registro de medição
* listagem e detalhe de OS
* relatórios/KPIs

---

## 13. Critérios de aceite do MVP

* usuário consegue autenticar;
* equipamento pode ser cadastrado e consultado;
* ocorrência pode ser registrada;
* medição pode ser registrada;
* OS pode ser criada manualmente;
* regra simples pode gerar sugestão/criação de OS;
* status da OS pode ser atualizado;
* dashboard exibe KPIs básicos;
* sistema funciona em desktop e mobile via navegador.

---

## 14. Riscos de projeto

* escopo alto para 160h;
* IA pode inflar esforço sem ganho real no MVP;
* disponibilidade 99,9% pode exigir infraestrutura além do prazo;
* requisitos ainda sem limites numéricos claros de alerta e severidade.

---

## 15. Recomendações ao Codex

* priorizar entrega funcional antes de refinamento visual;
* implementar primeiro CRUDs e autenticação;
* usar regras fixas para alertas;
* deixar arquitetura preparada para plugar IA depois;
* manter código modular;
* gerar seed inicial com usuários, equipes e equipamentos de exemplo;
* documentar variáveis de limite de medições em configuração.

---

## 16. Itens em aberto para refinamento com PO

* quais limites de temperatura, vibração, ruído etc. geram alerta?
* OS automática deve ser criada sempre ou apenas sugerida?
* quais KPIs são obrigatórios no dashboard?
* haverá anexos/fotos nas ocorrências?
* QR code faz parte do MVP ou apenas TAG manual?
* qual volume esperado de usuários e registros?
* backup será local, nuvem ou híbrido?
* existe necessidade de impressão em PDF já no MVP?

---
