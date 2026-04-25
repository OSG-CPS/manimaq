# HANDOFF SPT7

## 1. Objetivo da thread

Executar a Sprint 7 do MVP do sistema de manutenção industrial.

Esta thread deve aproveitar a base já consolidada de dashboard, KPIs, relatórios, alertas e ordens de serviço para implementar análise e leitura analítica com IA, mantendo a IA como apoio à decisão e não como substituta da decisão humana.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/HANDOFF_SPT6.md`
- `docs/HANDOFF_SPT6_SAIDA.md`
- `docs/MODELO_HANDOFF_DE_SAIDA.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Usar como referência principal o estado final consolidado da Sprint 6.

---

## 3. Estado de entrada da Sprint 7

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
- dashboard com KPIs reais
- relatórios básicos com filtros
- enriquecimento opcional de alertas por IA com fallback seguro

Pendências herdadas:

- validar `next build` do frontend em ambiente estável
- decidir futuramente se relatórios precisarão de exportação simples
- revisar futuramente o motivo estruturado para alertas revisados sem OS

Essas pendências não devem bloquear a Sprint 7, salvo se houver impacto direto na entrega da camada analítica.

---

## 4. Escopo da Sprint 7

### Leitura analítica por IA

- usar `gpt-5.4-mini` para gerar leitura analítica sobre os dados consolidados
- produzir interpretação em linguagem clara para facilitar leitura gerencial
- considerar no mínimo:
  - resumo executivo
  - principais pontos de atenção
  - possíveis causas ou padrões relevantes
  - recomendações operacionais

### Relatório de análise de tendências

- incluir relatório de análise de tendências com abordagem zero-shot
- tratar a saída como apoio analítico e sinal preditivo assistido por IA, não como previsão determinística de falha
- permitir análise:
  - por equipamento
  - por setor
- permitir janela selecionável:
  - `7 dias`
  - `30 dias`
  - `total`
- produzir duas camadas de leitura:
  - executiva
  - técnica
- classificar o contexto analisado em níveis como:
  - `normal`
  - `monitorar`
  - `intervir`
- exibir esse relatório apenas na área de relatórios, não no dashboard principal

### Análise sobre dados consolidados

- usar como base os agregados já existentes de dashboard e relatórios
- aproveitar alertas, OS, ocorrências e recorrência por equipamento como contexto
- evitar reabrir modelagem operacional já consolidada, salvo necessidade real

### Apoio à decisão

- manter a IA como apoio interpretativo
- não automatizar decisão crítica
- não abrir OS automaticamente
- não substituir revisão gerencial

### Frontend analítico

- criar espaço visual no dashboard e/ou relatórios para exibir a leitura analítica
- deixar claro quando o texto veio da IA
- exibir fallback claro quando a IA não estiver disponível

---

## 5. Regras de negócio a respeitar

- a decisão final continua humana
- a IA deve ser tratada como apoio interpretativo
- o sistema deve continuar útil mesmo sem resposta da OpenAI
- a análise deve se basear em dados reais persistidos e agregados do sistema
- manter rastreabilidade simples do que foi produzido por IA

Se for necessário limitar o escopo para caber melhor no MVP, priorizar leitura analítica sobre dashboard e relatórios antes de qualquer tentativa de inteligência operacional mais complexa.

Na análise de tendências, priorizar identificação de:

- piora recorrente
- aumento de incidência de ocorrências
- concentração de alertas
- sinais de deterioração operacional
- recomendação de inspeção, monitoramento ou intervenção

---

## 6. Decisões já adotadas para esta sprint

- modelo de IA adotado: `gpt-5.4-mini`
- integração OpenAI somente no backend
- chave em `.env` via `OPENAI_API_KEY`
- IA como apoio, não como decisora final
- reaproveitar agregações da Sprint 6 como base principal da análise

---

## 7. Entregáveis esperados

- integração backend para gerar leitura analítica sobre dados consolidados
- endpoint ou payload analítico para dashboard/relatórios
- resumo executivo por IA
- destaques de riscos/tendências em linguagem simples
- recomendações operacionais geradas por IA
- relatório de análise de tendências por equipamento e por setor
- leitura executiva e técnica no relatório
- classificação operacional `normal | monitorar | intervir`
- frontend exibindo essa leitura de forma clara
- fallback sem quebra quando IA falhar

---

## 8. Critérios de pronto da Sprint 7

A sprint pode ser considerada pronta quando:

- a IA conseguir gerar leitura analítica útil sobre os dados consolidados
- a IA conseguir gerar relatório de tendência útil por equipamento e por setor
- o relatório aceitar janela `7 dias`, `30 dias` e `total`
- o relatório exibir leitura executiva e técnica
- o relatório classificar o cenário em `normal`, `monitorar` ou `intervir`
- dashboard e/ou relatórios exibirem essa leitura de forma clara
- o sistema continuar funcional sem a OpenAI
- a leitura por IA não quebrar o fluxo principal nem alterar decisões automaticamente
- a entrega permanecer compatível com o escopo de MVP

---

## 9. Ordem sugerida de implementação

1. revisar rapidamente os agregados da Sprint 6 e o módulo atual de alertas
2. definir qual payload consolidado será enviado à IA
3. implementar serviço backend de leitura analítica
4. integrar o serviço com `gpt-5.4-mini`
5. adicionar fallback seguro e rastreabilidade mínima
6. implementar payload e fluxo do relatório de tendências por equipamento/setor e janela
7. expor a leitura analítica ao frontend na área de relatórios
8. validar a utilidade prática da resposta no contexto executivo e técnico

---

## 10. Limites desta sprint

Não é objetivo da Sprint 7:

- transformar o sistema em BI avançado
- automatizar manutenção ou abertura de OS
- substituir análise humana por decisão automática
- reabrir a modelagem principal das sprints anteriores sem necessidade real

---

## 11. Cuidados especiais

- manter prompts simples, objetivos e auditáveis
- evitar excesso de texto gerado por IA
- garantir que a análise seja ancorada em números e fatos do sistema
- identificar claramente quando a leitura veio da IA
- deixar claro que análise de tendência zero-shot não equivale a modelo treinado especializado
- evitar linguagem que prometa previsão certa de falha
- se o ambiente permitir, tentar novamente a validação de `next build`

---

## 12. Saída esperada ao final da thread

Ao concluir a Sprint 7, devolver um handoff usando `docs/MODELO_HANDOFF_DE_SAIDA.md`, contendo no mínimo:

- resumo do que foi implementado
- status da sprint
- pendências e riscos
- decisões técnicas tomadas
- arquivos principais alterados
- como validar localmente
- o que ficou pronto após a Sprint 7

Esse handoff será trazido de volta para a thread principal de planejamento.
