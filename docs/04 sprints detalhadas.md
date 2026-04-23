**Backlog de Sprints**

Abaixo está o plano macro convertido em backlog de sprint, com entregáveis por módulo e critério de pronto de cada etapa.

**Sprint 1**
Objetivo: colocar o sistema de pé com base técnica, autenticação e estrutura inicial.

Entregáveis por módulo:
- `infra`
  - estrutura do repositório com `frontend/` e `backend/`
  - configuração de ambiente local
  - `.env.example`
  - setup de banco `SQLite`
- `backend/core`
  - configuração `FastAPI`
  - conexão com banco
  - base de models/schemas
- `auth`
  - login por `username` ou `email`
  - hash de senha
  - JWT
  - middleware/dependência de autenticação
  - logout no frontend
- `seed`
  - usuários iniciais
  - equipes iniciais mínimas
  - equipamentos iniciais mínimos

Critérios de pronto:
- aplicação frontend e backend sobem localmente
- usuário consegue autenticar com seed
- rotas privadas estão protegidas
- perfis básicos existem e são reconhecidos
- configuração sensível está fora do código e em `.env`

**Sprint 2**
Objetivo: consolidar os cadastros-base com regras de acesso e consistência.

Entregáveis por módulo:
- `users`
  - listar
  - criar
  - editar
  - desativar
  - filtro/busca
- `teams`
  - criar
  - editar
  - listar
  - inativar
  - validação de nome único
- `equipments`
  - criar
  - editar
  - listar
  - detalhar
  - validação de TAG única
- `authorization`
  - permissões por perfil nos módulos acima

Critérios de pronto:
- CRUDs principais funcionam com persistência
- email duplicado não é permitido
- equipe inativa não entra em novos vínculos
- equipamento tem TAG única validada
- permissões mínimas por perfil estão aplicadas

**Sprint 3**
Objetivo: habilitar a operação do dia a dia no chão de fábrica.

Entregáveis por módulo:
- `occurrences`
  - registrar ocorrência
  - listar com filtros
  - detalhar
  - editar conforme regra de permissão
- `measurements`
  - registrar medições de vibração, temperatura, tensão e corrente
  - listar histórico
  - associar unidade/tipo quando necessário
- `equipment-history`
  - visão consolidada do histórico do equipamento
- `ui-operacional`
  - formulários e listagens responsivas
  - destaque de parada de produção e severidade

Critérios de pronto:
- operador e gerente conseguem registrar ocorrências
- medições ficam vinculadas ao equipamento e autor
- histórico por equipamento pode ser consultado
- filtros básicos funcionam
- dados ficam padronizados e auditáveis

**Sprint 4**
Objetivo: fechar o ciclo de manutenção com ordens de serviço.

Entregáveis por módulo:
- `work-orders`
  - criar OS manual
  - listar
  - filtrar
  - detalhar
  - atualizar status
  - registrar retorno/conclusão
- `work-order-history`
  - histórico de mudança de status
  - responsável e data/hora das alterações
- `workflow`
  - fluxo com decisão do gerente sobre abertura/priorização

Critérios de pronto:
- gerente consegue abrir e encaminhar OS
- executores conseguem atuar conforme permissão
- status da OS é atualizado com histórico
- OS permanece vinculada a equipamento e equipe
- fluxo ponta a ponta de OS fica funcional

**Sprint 5**
Objetivo: adicionar inteligência aos alertas sem perder previsibilidade operacional.

Entregáveis por módulo:
- `alerts-rules`
  - regras determinísticas por severidade, risco, parada e thresholds
- `ai-integration`
  - cliente OpenAI no backend
  - leitura de `OPENAI_API_KEY` via `.env`
  - integração com `gpt-5.4-mini`
- `alerts-ai`
  - análise de comportamento e tendência
  - sugestão de risco, causa provável e ação recomendada
  - sugestão de abertura de OS
- `fallback`
  - operação continua com regras mesmo se IA falhar

Critérios de pronto:
- alerta pode ser gerado por regra objetiva
- IA consegue enriquecer alerta com análise textual
- sugestão de OS é exibida, mas não executada automaticamente
- decisão final continua com o gerente
- falha da API OpenAI não quebra o sistema

**Sprint 6**
Objetivo: transformar os dados em leitura gerencial útil e fechar o MVP.

Entregáveis por módulo:
- `reports`
  - consolidação de dados por período, equipamento, equipe e tipo
  - exportação simples
- `dashboard`
  - KPIs principais
  - backlog de OS
  - corretiva vs preventiva
  - tempo médio de atendimento
  - recorrência por equipamento
- `reports-ai`
  - resumo executivo em linguagem simples
  - análise de tendências
  - potenciais problemas
  - recomendações operacionais
- `quality`
  - responsividade
  - validações finais
  - testes essenciais dos fluxos críticos
  - revisão de permissões e estabilidade

Critérios de pronto:
- dashboard mostra KPIs reais do sistema
- relatório analítico pode ser consultado com clareza
- IA gera leitura gerencial útil sobre os dados
- exportação simples funciona
- fluxo principal do MVP está estável em desktop e mobile

**Entregáveis transversais**
Esses itens devem existir em todas as sprints, conforme o módulo entregue:

- modelos e persistência
- schemas de entrada e saída
- endpoints REST
- validações de negócio
- telas ou páginas correspondentes
- testes básicos do fluxo crítico
- controle de acesso por perfil

**Critério de pronto do MVP**
Ao final das sprints, o sistema deve permitir:

- autenticação com perfis
- cadastro de usuários, equipes e equipamentos
- registro de ocorrências e medições
- histórico por equipamento
- criação e acompanhamento de OS
- alertas por regra e por análise assistida por IA
- sugestão de OS com decisão final do gerente
- dashboard com KPIs
- relatórios com apoio de IA

Se quiser, no próximo passo eu organizo isso em formato de **roadmap executável**, com dependências entre módulos e ordem real de implementação dentro de cada sprint.