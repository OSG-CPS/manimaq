# HANDOFF SPT6

## 1. Objetivo da thread

Executar a Sprint 6 do MVP do sistema de manutenção industrial.

Esta thread deve aproveitar a base já consolidada de ocorrências, medições, ordens de serviço e alertas para implementar dashboard, KPIs e relatórios básicos, consolidando visual e operacionalmente os dados já disponíveis no sistema.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/HANDOFF_SPT5.md`
- `docs/HANDOFF_SPT5_SAIDA.md`
- `docs/HANDOFF_SPT5_5.md`
- `docs/MODELO_HANDOFF_DE_SAIDA.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Usar como referência principal o estado final consolidado das Sprints 5 e 5.5.

---

## 3. Estado de entrada da Sprint 6

As sprints anteriores deixaram pronto:

- autenticação com JWT
- sessão autenticada no frontend
- controle de acesso por perfil
- CRUD de `users`, `teams` e `equipments`
- registro de `occurrences`
- registro de `measurements`
- histórico consolidado por equipamento
- fluxo manual de `work-orders`
- histórico de status de OS
- alertas por regras com persistência
- thresholds por equipamento
- revisão gerencial de alertas
- abertura manual de OS a partir do alerta
- enriquecimento opcional de alertas por IA com fallback seguro

Pendências herdadas:

- validar `tsc --noEmit` e `next build` do frontend em ambiente sem bloqueio
- decidir futuramente se alertas revisados sem OS exigirão motivo estruturado
- decidir futuramente se haverá mais de um tipo principal de medição por equipamento
- revisar futuramente a estratégia simplificada de evolução de schema SQLite

Essas pendências não devem bloquear a Sprint 6, salvo se houver impacto direto no dashboard, nos relatórios ou na validação do frontend.

---

## 4. Reorientação oficial do roadmap

O roadmap foi reorganizado assim:

- `SPT5` permanece encerrada como bloco concluído
- `SPT6` passa a focar em dashboard, KPIs e relatórios básicos
- `SPT7` ficará para alertas com IA mais madura, análise de comportamento/tendência e leitura analítica por IA

Portanto, esta Sprint 6 não deve puxar IA pesada como foco principal.

---

## 5. Escopo da Sprint 6

### Dashboard

- criar visão consolidada inicial no dashboard
- destacar indicadores principais do sistema
- exibir dados úteis para operação e gestão
- integrar dashboard à navegação já existente

### KPIs

Implementar, no mínimo, indicadores como:

- quantidade de OS abertas
- quantidade de OS concluídas
- backlog de OS
- percentual corretiva vs preventiva
- tempo médio de atendimento
- quantidade de ocorrências por equipamento
- equipamentos com maior recorrência de falha

Se necessário, manter cálculo simples e explicável.

### Relatórios básicos

- consolidar dados por período
- consolidar dados por equipamento
- consolidar dados por equipe
- consolidar dados por tipo de manutenção
- fornecer visão prática para consulta gerencial

### Frontend de visualização

- criar páginas e componentes básicos para dashboard e relatórios
- exibir KPIs de forma clara
- permitir filtros básicos quando necessário
- manter o frontend simples, funcional e consistente com o resto do projeto

---

## 6. Regras de negócio a respeitar

- os indicadores devem usar dados reais já persistidos no sistema
- cálculos devem ser simples, auditáveis e consistentes com o MVP
- dashboard deve refletir operação real, e não projeção hipotética
- IA não é foco desta sprint; qualquer preparação estrutural deve ser mínima
- respeitar permissões por perfil já consolidadas

Se houver dúvida entre sofisticação e clareza, priorizar clareza e utilidade prática.

---

## 7. Entregáveis esperados

- endpoints REST ou agregações necessárias para dashboard
- cálculo dos KPIs principais
- páginas básicas de dashboard e relatórios
- filtros básicos para consulta gerencial
- visualização consolidada dos dados operacionais já existentes

---

## 8. Critérios de pronto da Sprint 6

A sprint pode ser considerada pronta quando:

- dashboard exibir KPIs reais do sistema
- relatórios básicos puderem ser consultados
- dados de OS, ocorrências e equipamentos aparecerem consolidados de forma útil
- frontend permitir consulta clara dessas informações
- fluxo principal do sistema permanecer estável após a inclusão do dashboard

---

## 9. Ordem sugerida de implementação

1. revisar rapidamente os modelos e fluxos já consolidados de ocorrências, medições, OS e alertas
2. definir consultas e agregações mínimas de dashboard
3. implementar cálculo dos KPIs no backend
4. expor endpoints ou payloads agregados para frontend
5. construir páginas e componentes de dashboard/relatórios
6. validar consistência dos números com os dados existentes

---

## 10. Limites desta sprint

Não é objetivo da Sprint 6:

- aprofundar alertas com IA
- implementar análise de comportamento/tendência mais avançada
- transformar relatórios em leitura analítica por IA
- automatizar decisões de manutenção

Se houver preparação para a Sprint 7, ela deve ser mínima e não pode puxar o foco desta sprint.

---

## 11. Cuidados especiais

- usar os alertas e a relação com OS como uma das bases para os indicadores
- não exagerar em complexidade de BI nesta fase
- manter os cálculos transparentes
- se exportação simples entrar naturalmente, tudo bem; se ameaçar escopo, priorizar consulta em tela
- se o ambiente permitir, tentar validar também o que continua pendente de `tsc --noEmit` e `next build`

---

## 12. Saída esperada ao final da thread

Ao concluir a Sprint 6, devolver um handoff usando `docs/MODELO_HANDOFF_DE_SAIDA.md`, contendo no mínimo:

- resumo do que foi implementado
- status da sprint
- pendências e riscos
- decisões técnicas tomadas
- arquivos principais alterados
- como validar localmente
- o que fica pronto para a Sprint 7

Esse handoff será trazido de volta para a thread principal de planejamento.
