**Backlog (MVP – 4 semanas / 160h)**
Estruturado por **épicos → histórias (priorizadas)** com foco em entrega viável.

---

## ÉPICO 1 — Autenticação e Perfis (≈16h)

* US01: Login com usuário/senha
* US02: Perfis (admin, gerente, operador) com controle básico de acesso
* US03: Logout + sessão simples

---

## ÉPICO 2 — Cadastro Base (≈32h)

* US04: CRUD usuários
* US05: CRUD equipamentos (TAG + setor + identificação por código simples)
* US06: CRUD equipes
* US07: Busca e filtro básico (equipamentos/usuários)

---

## ÉPICO 3 — Ocorrências e Medições (≈32h)

* US08: Registrar ocorrência (severidade, risco, parada, descrição, timestamp)
* US09: Registrar medições (valores + unidade)
* US10: Histórico por equipamento
* US11: Edição/consulta de registros

---

## ÉPICO 4 — Ordens de Serviço (≈32h)

* US12: Criar OS manual (prioridade, equipe, equipamento, datas)
* US13: Atualizar status (aberta, em execução, concluída)
* US14: Apontamentos da execução
* US15: Listagem + filtro de OS

---

## ÉPICO 5 — Alertas (IA simplificada) (≈16h)

* US16: Regras fixas (thresholds) para medições (ex: vibração > limite)
* US17: Geração de alerta (visual)
* US18: Sugestão de criação de OS (não automática)

---

## ÉPICO 6 — KPIs e Relatórios (≈16h)

* US19: MTBF (cálculo simples)
* US20: MTTR
* US21: % preventiva vs corretiva
* US22: Backlog de OS
* US23: Exportação simples (PDF/CSV básico)

---

## ÉPICO 7 — Infra/Qualidade (≈16h)

* US24: Log de alterações (básico)
* US25: Backup simples (rotina diária)
* US26: Responsividade (web mobile/desktop)
* US27: Controle de acesso (autorização por perfil)

---

# Priorização (ordem de execução)

1. Épico 1 (Auth)
2. Épico 2 (Cadastro base)
3. Épico 3 (Ocorrências/medições)
4. Épico 4 (OS)
5. Épico 5 (Alertas simples)
6. Épico 6 (KPIs)
7. Épico 7 (Infra mínima)

---

# Sprint Plan (sugestão)

### Sprint 1 (40h)

* Auth + Cadastro base (parcial)
* Estrutura de dados

### Sprint 2 (40h)

* Cadastro completo
* Ocorrências + medições

### Sprint 3 (40h)

* OS completa
* Alertas simples

### Sprint 4 (40h)

* KPIs + relatórios
* Logs + ajustes + validação

---

# Cortes claros (para caber no prazo)

* IA = apenas **regras heurísticas**
* Sem integração externa
* UI simples (sem refinamento avançado)
* Relatórios básicos (sem BI complexo)

---

# Critérios de pronto (DoD)

* CRUD funcionando + persistência
* Fluxo completo: ocorrência → alerta → OS → conclusão
* KPIs calculando com dados reais
* Acesso por perfil respeitado
* Tempo de resposta < 3s em uso básico

---

# Perguntas rápidas para PO

* Limites (thresholds) das medições já definidos?
* Prioridade: OS ou KPIs se houver corte?
* Exportação é obrigatória no MVP?
* Identificação por código = QR ou texto manual?
* Quantos equipamentos/usuários esperados no piloto?
