# HANDOFF SPT4

## 1. Objetivo da thread

Executar a Sprint 4 do MVP do sistema de manutenção industrial.

Esta thread deve aproveitar a base já existente de autenticação, autorização, cadastros e fluxo operacional para implementar `work-orders`, histórico de status e o ciclo inicial de execução da manutenção.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/HANDOFF_SPT3.md`
- `docs/HANDOFF_SPT3_SAIDA.md`
- `docs/MODELO_HANDOFF_DE_SAIDA.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Usar como referência principal o estado final consolidado da Sprint 3.

---

## 3. Estado de entrada da Sprint 4

As sprints anteriores deixaram pronto:

- autenticação com JWT
- sessão autenticada no frontend
- autorização por perfil
- área autenticada com navegação modular
- CRUD de `users`
- CRUD de `teams`
- CRUD de `equipments`
- registro e listagem de `occurrences`
- registro e listagem de `measurements`
- histórico consolidado por equipamento
- persistência SQLite funcional

Pendências herdadas:

- validar `tsc --noEmit` e `next build` do frontend em ambiente sem bloqueio
- acompanhar se a regra de edição de ocorrência em 24h continua adequada diante do fluxo de OS

Essas pendências não devem bloquear a Sprint 4, salvo se houver impacto direto no frontend ou nas regras operacionais.

---

## 4. Escopo da Sprint 4

### Work Orders

- criar modelo, schemas e rotas de `work-orders`
- criar OS manualmente
- vincular OS obrigatoriamente a:
  - equipamento
  - equipe
- suportar no mínimo:
  - tipo
  - prioridade
  - status
  - descrição
  - origem
  - data prevista de início
  - duração estimada

### Workflow operacional

- permitir criação de OS por `gerente` e `admin`, conforme regra adotada
- permitir encaminhamento da OS para equipe responsável
- permitir atualização de status
- permitir registrar retorno/conclusão
- preservar rastreabilidade por autor e data/hora em cada transição relevante

### Histórico de status

- implementar histórico de mudança de status da OS
- armazenar responsável, status anterior, status novo e timestamp
- manter base preparada para futura ligação com alertas e IA

### Frontend de OS

- criar página de listagem de OS
- criar formulário de criação manual de OS
- criar detalhe visual mínimo da OS
- permitir atualização de status no frontend
- integrar a navegação do dashboard aos novos módulos

---

## 5. Regras de negócio a respeitar

- toda OS deve estar vinculada a um equipamento
- toda OS deve estar vinculada a uma equipe
- decisão de abertura/priorização da OS é do `gerente`
- `admin` pode ter acesso amplo conforme decisões consolidadas
- mudanças de status devem ser registradas em histórico
- fluxo deve preservar rastreabilidade técnica e operacional
- o desenho deve ficar simples, mas pronto para receber alertas e sugestões futuras

Se for necessário escolher enums, manter a solução mínima e compatível com o handoff geral.

Sugestão mínima de enums para esta sprint, se necessário:

- tipo: `corretiva`, `preventiva`
- status: `aberta`, `em_execucao`, `concluida`, `cancelada`
- origem: `manual`, `sugerida`
- prioridade: `baixa`, `media`, `alta`, `critica`

Se houver ajuste nesses enums, registrar no handoff de saída.

---

## 6. Entregáveis esperados

- endpoints REST de `work-orders`
- estrutura de histórico de status de OS
- validações mínimas de negócio
- páginas básicas no frontend para criação, listagem, detalhe e atualização de status
- fluxo funcional de OS ponta a ponta

---

## 7. Critérios de pronto da Sprint 4

A sprint pode ser considerada pronta quando:

- uma OS puder ser criada com persistência
- uma OS puder ser listada e consultada
- o status da OS puder ser atualizado
- o histórico de transições da OS puder ser consultado
- a OS permanecer corretamente vinculada a equipamento e equipe
- o frontend permitir operar esse fluxo de forma básica

---

## 8. Ordem sugerida de implementação

1. revisar rapidamente os módulos da Sprint 3 e o histórico por equipamento
2. modelar `work-orders`
3. modelar histórico de status de OS
4. implementar rotas REST e validações no backend
5. conectar criação e atualização de OS ao frontend
6. validar fluxo ponta a ponta

---

## 9. Limites desta sprint

Não é objetivo da Sprint 4:

- implementar alertas por regras
- integrar OpenAI
- criar alertas por comportamento e tendência
- construir dashboard real de KPIs
- desenvolver relatórios analíticos

Também não é objetivo automatizar abertura de OS nesta sprint; o foco é fluxo manual e rastreável.

---

## 10. Cuidados especiais

- reutilizar o histórico por equipamento como contexto do fluxo de OS sempre que fizer sentido
- manter simplicidade no frontend
- não acoplar a OS prematuramente a lógica de alertas
- preservar o padrão de rastreabilidade por autor e timestamp
- se surgirem dúvidas de permissão entre `admin`, `gerente` e `operador`, escolher a opção mais conservadora e registrar no handoff de saída

---

## 11. Saída esperada ao final da thread

Ao concluir a Sprint 4, devolver um handoff usando `docs/MODELO_HANDOFF_DE_SAIDA.md`, contendo no mínimo:

- resumo do que foi implementado
- status da sprint
- pendências e riscos
- decisões técnicas tomadas
- arquivos principais alterados
- como validar localmente
- o que fica pronto para a Sprint 5

Esse handoff será trazido de volta para a thread principal de planejamento.
