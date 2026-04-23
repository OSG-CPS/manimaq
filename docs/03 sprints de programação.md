Perfeito. Com essas definições, o plano macro fica mais consistente e mais seguro para o MVP:

- modelo único para IA: `gpt-5.4-mini`
- IA sugere alertas, análises e abertura de OS, mas a decisão final de abrir/priorizar OS é do `gerente`
- chave da OpenAI em `.env`, usada só no backend

Eu reorganizaria as sprints assim:

**Sprint 1**
Base do projeto e fundações técnicas.

- estrutura `frontend` + `backend`
- configuração de ambiente, `.env`, banco e seed inicial
- modelagem inicial das entidades principais
- autenticação, login, proteção de rotas e logout
- perfis `admin`, `gerente`, `operador`

**Sprint 2**
Cadastros-base e governança dos dados.

- CRUD de usuários
- CRUD de equipes
- CRUD de equipamentos
- vínculo usuário-equipe
- filtros e buscas básicas
- regras de acesso por perfil

**Sprint 3**
Fluxo operacional de chão de fábrica.

- registro de ocorrências
- registro de medições
- histórico por equipamento
- listagens e detalhes
- padronização de severidade, status e flags operacionais

**Sprint 4**
Ordens de serviço e ciclo de execução.

- criação manual de OS
- encaminhamento para equipe
- atualização de status
- retorno/conclusão
- histórico de mudanças
- decisão de OS concentrada no gerente

**Sprint 5**
Alertas híbridos com IA.

- motor de regras determinísticas
- integração backend com OpenAI API usando `gpt-5.4-mini`
- análise por comportamento e tendência
- sugestão de risco, causa provável e ação recomendada
- sugestão de abertura de OS para avaliação do gerente
- fallback para operação sem IA se a chamada falhar

**Sprint 6**
Dashboard, relatórios e fechamento do MVP.

- KPIs consolidados
- leitura assistida por IA dos indicadores
- relatórios textuais mais fáceis de interpretar
- destaque de potenciais problemas e tendências
- exportação simples
- ajustes de responsividade, validações finais e testes essenciais

**Leitura geral do plano**
A ordem ideal agora é:

1. garantir cadastro, autenticação e rastreabilidade
2. fechar o fluxo operacional real
3. estruturar a OS
4. só então adicionar a camada inteligente de IA
5. por fim transformar os dados em leitura gerencial útil

**Assunções já fechadas para esse plano**
- IA não substitui regra de negócio crítica
- IA apoia decisão, não executa decisão de manutenção
- `gerente` continua como aprovador operacional da OS sugerida
- OpenAI fica encapsulada no backend
- `.env` guarda `OPENAI_API_KEY` e não deve ir para versionamento

