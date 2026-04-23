# HANDOFF SPT3

## 1. Objetivo da thread

Executar a Sprint 3 do MVP do sistema de manutenção industrial.

Esta thread deve aproveitar a base já consolidada de autenticação, autorização e cadastros para implementar o fluxo operacional inicial do sistema, com foco em `occurrences`, `measurements` e `equipment-history`.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/HANDOFF_SPT2.md`
- `docs/HANDOFF_SPT2_SAIDA.md`
- `docs/MODELO_HANDOFF_DE_SAIDA.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Usar como referência principal o estado final consolidado da Sprint 2.

---

## 3. Estado de entrada da Sprint 3

A Sprint 2 deixou pronto:

- autenticação com JWT
- sessão autenticada no frontend
- autorização inicial por perfil
- área autenticada com navegação administrativa
- CRUD de `users`
- CRUD de `teams`
- CRUD de `equipments`
- persistência SQLite funcional
- relação estrutural entre usuários, equipes e equipamentos

Pendências herdadas:

- validar `next build` em ambiente local estável
- ampliar cobertura com testes automatizados persistidos em arquivo

Essas pendências não devem bloquear a Sprint 3, salvo se aparecer impacto direto no desenvolvimento dos novos módulos.

---

## 4. Escopo da Sprint 3

### Occurrences

- criar modelo, schemas e rotas de ocorrências
- registrar ocorrência vinculada a um único equipamento
- registrar autor e timestamp
- suportar severidade, risco à segurança, parada de produção e descrição
- listar ocorrências com filtros básicos
- detalhar ocorrência
- permitir edição somente se estiver dentro das regras definidas na implementação

### Measurements

- criar modelo, schemas e rotas de medições
- registrar medições de:
  - vibração
  - temperatura
  - tensão
  - corrente
- registrar autor e timestamp
- associar unidade/tipo quando necessário
- listar histórico de medições

### Equipment History

- consolidar visão por equipamento
- reunir ocorrências e medições relacionadas
- permitir consulta operacional do histórico

### Frontend operacional

- criar páginas de registro e listagem de ocorrências
- criar páginas de registro e listagem de medições
- criar visão básica de histórico por equipamento
- manter navegação simples, funcional e integrada ao dashboard existente

---

## 5. Regras de negócio a respeitar

- ocorrência sempre vinculada a um único equipamento
- medição sempre vinculada a um único equipamento
- toda ocorrência e medição deve registrar autor e data/hora
- descrição de ocorrência é obrigatória
- se `parada de produção = sim`, destacar visualmente no frontend
- severidade deve ficar padronizada para uso futuro em alertas e OS
- validar existência do equipamento antes de criar ocorrência ou medição
- respeitar autenticação e permissões já existentes

Se surgir necessidade de escolher enums ou campos auxiliares, manter o desenho o mais simples possível e registrar a decisão no handoff de saída.

---

## 6. Entregáveis esperados

- endpoints REST de `occurrences`
- endpoints REST de `measurements`
- modelos e schemas persistidos no backend
- validações mínimas de negócio
- páginas básicas no frontend para registro, listagem e detalhe
- histórico por equipamento com visão operacional simples

---

## 7. Critérios de pronto da Sprint 3

A sprint pode ser considerada pronta quando:

- ocorrência puder ser registrada com persistência
- medição puder ser registrada com persistência
- ocorrências puderem ser listadas e consultadas
- medições puderem ser listadas e consultadas
- histórico por equipamento puder ser visualizado
- dados ficarem vinculados corretamente a equipamento e autor
- frontend permitir operar esses fluxos de forma básica

---

## 8. Ordem sugerida de implementação

1. revisar rapidamente a base existente da Sprint 2
2. definir modelos e schemas de `occurrences`
3. definir modelos e schemas de `measurements`
4. implementar rotas REST e validações no backend
5. criar visão de histórico por equipamento
6. conectar frontend aos novos módulos
7. validar fluxos principais

---

## 9. Limites desta sprint

Não é objetivo da Sprint 3:

- implementar ordens de serviço
- implementar alertas
- integrar OpenAI
- construir dashboard real de KPIs
- iniciar relatórios analíticos

Se for necessário preparar estrutura para as próximas sprints, isso deve ser feito apenas de forma mínima e sem expandir o escopo funcional.

---

## 10. Cuidados especiais

- preservar o padrão de organização de rotas, schemas e dependências da Sprint 2
- não complexificar demais o modelo de medições neste momento
- priorizar fluxo operacional funcionando antes de refinamentos de interface
- se possível, já salvar testes automatizados em arquivo para os fluxos novos
- se `next build` continuar sendo um problema, registrar com clareza no handoff de saída

---

## 11. Saída esperada ao final da thread

Ao concluir a Sprint 3, devolver um handoff usando `docs/MODELO_HANDOFF_DE_SAIDA.md`, contendo no mínimo:

- resumo do que foi implementado
- status da sprint
- pendências e riscos
- decisões técnicas tomadas
- arquivos principais alterados
- como validar localmente
- o que fica pronto para a Sprint 4

Esse handoff será trazido de volta para a thread principal de planejamento.
