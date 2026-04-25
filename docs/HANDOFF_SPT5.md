# HANDOFF SPT5

## 1. Objetivo da thread

Executar a Sprint 5 do MVP do sistema de manutenção industrial.

Esta thread deve aproveitar a base já existente de ocorrências, medições, histórico por equipamento e ordens de serviço para implementar alertas por regras, alertas com IA e sugestão de abertura de OS para decisão do gerente.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/HANDOFF_SPT4.md`
- `docs/HANDOFF_SPT4_SAIDA.md`
- `docs/MODELO_HANDOFF_DE_SAIDA.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Usar como referência principal o estado final consolidado da Sprint 4.

---

## 3. Estado de entrada da Sprint 5

As sprints anteriores deixaram pronto:

- autenticação com JWT
- sessão autenticada no frontend
- controle de acesso por perfil
- CRUD de `users`, `teams` e `equipments`
- registro de `occurrences`
- registro de `measurements`
- histórico consolidado por equipamento
- fluxo manual de `work-orders`
- histórico de status de OS com rastreabilidade operacional

Pendências herdadas:

- validar `tsc --noEmit` e `next build` do frontend em ambiente sem bloqueio
- decidir como representar a origem operacional de uma OS sugerida em relação a ocorrências e medições
- revisar posteriormente a estratégia simplificada de evolução de schema SQLite

Essas pendências não devem bloquear a Sprint 5, exceto se impactarem diretamente a implementação do fluxo de alertas.

---

## 4. Escopo da Sprint 5

### Alertas por regras

- criar modelo, schemas e rotas de `alerts`
- implementar geração de alerta por regras determinísticas
- considerar no mínimo:
  - severidade alta de ocorrência
  - risco à segurança
  - parada de produção
  - thresholds simples de medição
- persistir alertas gerados
- permitir consulta/listagem de alertas

### Alertas com IA

- integrar backend com OpenAI API usando `gpt-5.4-mini`
- ler chave via `.env` com `OPENAI_API_KEY`
- usar IA para analisar comportamento e tendência, não apenas limiar
- gerar análise textual curta com:
  - risco
  - possível causa
  - recomendação operacional
- manter fallback funcional caso a chamada da IA falhe

### Sugestão de OS

- permitir que um alerta sugira abertura de OS
- manter a sugestão como recomendação, sem abertura automática
- preservar a decisão final de abertura e priorização com `gerente`
- definir uma forma simples de registrar a origem da sugestão para uso futuro

### Frontend de alertas

- criar página/listagem de alertas
- exibir severidade, origem, recomendação e sugestão de OS
- destacar alertas mais críticos
- integrar o módulo de alertas à navegação do dashboard

---

## 5. Regras de negócio a respeitar

- IA não substitui regra de negócio crítica
- sistema deve continuar operando mesmo se a OpenAI falhar
- decisão final de abrir/priorizar OS continua com o `gerente`
- `admin` pode ter acesso amplo conforme decisões consolidadas
- `operador` pode visualizar o que fizer sentido operacionalmente, mas não deve ganhar autonomia gerencial sem alinhamento explícito
- alertas devem ficar vinculados ao contexto operacional relevante, preferencialmente equipamento e origem do evento

Se for necessário simplificar o vínculo de origem nesta sprint, preferir solução mínima, rastreável e compatível com evolução futura.

---

## 6. Decisões já adotadas para esta sprint

- modelo de IA adotado: `gpt-5.4-mini`
- chave da OpenAI em `.env`
- integração OpenAI somente no backend
- frontend nunca deve chamar a OpenAI diretamente
- alertas devem combinar regras determinísticas com análise por IA
- OS pode ser sugerida, mas não aberta automaticamente

---

## 7. Entregáveis esperados

- endpoints REST de `alerts`
- persistência de alertas
- motor mínimo de regras determinísticas
- integração backend com OpenAI API
- fallback sem quebra quando IA falhar
- página básica de alertas no frontend
- sugestão de OS visível para avaliação gerencial

---

## 8. Critérios de pronto da Sprint 5

A sprint pode ser considerada pronta quando:

- alertas puderem ser gerados por regra objetiva com persistência
- alertas puderem ser consultados no sistema
- IA conseguir enriquecer pelo menos parte dos alertas com análise textual
- falha da OpenAI não quebrar o fluxo principal
- sugestão de OS ficar visível, mas sem criação automática
- frontend permitir consultar alertas de forma básica

---

## 9. Ordem sugerida de implementação

1. revisar rapidamente `occurrences`, `measurements`, `work-orders` e seus históricos
2. definir o modelo mínimo de `alerts`
3. implementar regras determinísticas e persistência
4. integrar OpenAI no backend com `gpt-5.4-mini`
5. adicionar enriquecimento por IA aos alertas
6. definir e exibir sugestão de OS
7. conectar frontend ao módulo de alertas
8. validar o fluxo principal com e sem IA disponível

---

## 10. Limites desta sprint

Não é objetivo da Sprint 5:

- criar dashboard real de KPIs
- desenvolver relatórios analíticos completos
- automatizar criação de OS
- transformar IA em decisora final de manutenção

Se for necessário preparar estrutura para relatórios da Sprint 6, isso deve ser feito apenas de forma mínima.

---

## 11. Cuidados especiais

- manter o desenho simples e auditável
- não acoplar demais a OpenAI ao fluxo principal
- preservar logs e rastreabilidade de como o alerta foi gerado
- deixar claro na modelagem se o alerta veio de `rule`, `ai` ou `hybrid`
- se thresholds ainda estiverem indefinidos, adotar valores provisórios configuráveis e registrar isso no handoff de saída
- se possível, validar também o que ficou pendente de `tsc` e `next build` caso o ambiente permita

---

## 12. Saída esperada ao final da thread

Ao concluir a Sprint 5, devolver um handoff usando `docs/MODELO_HANDOFF_DE_SAIDA.md`, contendo no mínimo:

- resumo do que foi implementado
- status da sprint
- pendências e riscos
- decisões técnicas tomadas
- arquivos principais alterados
- como validar localmente
- o que fica pronto para a Sprint 6

Esse handoff será trazido de volta para a thread principal de planejamento.
