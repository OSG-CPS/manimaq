# HANDOFF SPT2

## 1. Objetivo da thread

Executar a Sprint 2 do MVP do sistema de manutenção industrial.

Esta thread deve aproveitar a base criada na Sprint 1 para entregar os cadastros-base e a governança inicial dos dados, com foco em `users`, `teams`, `equipments` e regras de autorização por perfil.

---

## 2. Contexto que deve ser assumido

Ler antes de começar:

- `docs/HANDOFF_GERAL.md`
- `docs/HANDOFF_SPT1.md`
- `docs/MODELO_HANDOFF_DE_SAIDA.md`
- `docs/00 handoff_inicial.md`
- `docs/01 product_backlog_inicial.md`
- `docs/02 definições_da_equipe.md`
- `docs/03 sprints de programação.md`
- `docs/04 sprints detalhadas.md`

Usar também como contexto o handoff de saída da Sprint 1, já consolidado nesta thread principal.

---

## 3. Estado de entrada da Sprint 2

A Sprint 1 deixou pronto:

- estrutura do projeto com `frontend/` e `backend/`
- backend FastAPI funcional
- autenticação com JWT
- login por `username` ou `email`
- hash de senha no backend
- rota autenticada de validação
- endpoint `/api/auth/me`
- seed inicial com usuários, equipes e equipamentos
- frontend com login, logout, persistência de sessão e proteção básica da área autenticada
- `.env.example`
- `README.md` com passos básicos

Pendências herdadas da Sprint 1:

- falta smoke test manual completo em navegador
- não há autorização por perfil além da autenticação
- não há testes automatizados salvos em arquivo
- `next@15.3.1` acusou vulnerabilidade conhecida e deve ser revisado

---

## 4. Escopo da Sprint 2

### Autorização

- implementar autorização por perfil no backend
- restringir acesso aos módulos conforme regras de negócio
- garantir base mínima para diferenciação entre `admin`, `gerente` e `operador`

### Teams

- listar equipes
- criar equipe
- editar equipe
- inativar equipe
- validar nome único
- impedir uso de equipe inativa em novos vínculos

### Equipments

- listar equipamentos
- criar equipamento
- editar equipamento
- detalhar equipamento
- validar `TAG` única

### Users

- listar usuários
- criar usuário
- editar usuário
- desativar usuário
- validar email único
- manter senha fora do escopo de edição comum nesta sprint

### Frontend administrativo

- transformar a área autenticada em base para os módulos de cadastro
- criar páginas/listagens/formulários mínimos para `users`, `teams` e `equipments`
- aplicar navegação interna simples e funcional

---

## 5. Regras de negócio a respeitar

- `admin`: acesso total
- `gerente`: acesso operacional amplo, mas sem assumir mudanças fora do combinado
- `operador`: não deve acessar áreas administrativas de cadastro
- usuário deve estar vinculado a equipe ativa
- email de usuário não pode duplicar
- nome de equipe deve ser único
- equipes inativas não podem ser usadas em novos vínculos
- equipamento deve possuir `TAG` única
- exclusão deve ser lógica/inativação, não remoção física, sempre que aplicável

Se houver ambiguidade entre documentos anteriores, preservar as decisões consolidadas em `HANDOFF_GERAL.md`.

---

## 6. Entregáveis esperados

- autorização por perfil funcionando no backend
- endpoints REST de `users`, `teams` e `equipments`
- validações principais de negócio aplicadas
- páginas básicas de cadastro/listagem no frontend
- fluxo autenticado permitindo acessar os módulos administrativos
- persistência real dos cadastros no banco local

---

## 7. Critérios de pronto da Sprint 2

A sprint pode ser considerada pronta quando:

- CRUD de `teams` estiver funcional com persistência
- CRUD de `equipments` estiver funcional com persistência
- CRUD de `users` estiver funcional com persistência
- regras mínimas de autorização por perfil estiverem aplicadas
- `email` duplicado for bloqueado
- `TAG` duplicada for bloqueada
- equipe inativa não puder receber novos vínculos
- frontend permitir operar os cadastros de forma básica

---

## 8. Ordem sugerida de implementação

1. revisar rapidamente o fluxo real de login/dashboard herdado da Sprint 1
2. implementar autorização por perfil no backend
3. implementar CRUD de `teams`
4. implementar CRUD de `equipments`
5. implementar CRUD de `users`
6. conectar frontend aos endpoints
7. validar fluxos principais

---

## 9. Limites desta sprint

Não é objetivo da Sprint 2:

- implementar ocorrências
- implementar medições
- implementar ordens de serviço
- integrar OpenAI
- desenvolver alertas ou dashboard real
- refatorar profundamente a autenticação da Sprint 1, salvo se necessário para destravar autorização

---

## 10. Cuidados especiais

- evitar retrabalho da base de auth já pronta
- manter simplicidade no frontend administrativo
- se precisar revisar dependências do frontend por conta do `next@15.3.1`, fazer isso com cautela e registrar a decisão no handoff de saída
- qualquer ajuste estrutural herdado da Sprint 1 deve ser pequeno, justificado e documentado

---

## 11. Saída esperada ao final da thread

Ao concluir a Sprint 2, devolver um handoff usando `docs/MODELO_HANDOFF_DE_SAIDA.md`, contendo no mínimo:

- resumo do que foi implementado
- status da sprint
- pendências e riscos
- decisões técnicas tomadas
- arquivos principais alterados
- como validar localmente
- o que fica pronto para a Sprint 3

Esse handoff será trazido de volta para a thread principal de planejamento.
