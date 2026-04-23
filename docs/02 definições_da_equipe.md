"US01: Tabela users
id
name
username
email
password_hash
role (admin|gerente|operador)
active (true|false)
created_at
updated_atInterface mínima

Tela Login

Campo: usuário/email
Campo: senha
Botão: entrar
Mensagem de erro simples

Validações:

campos obrigatórios
senha mascarada
botão desabilitado enquanto enviaDefinição de pronto
Tela login funcional
Endpoint /auth/login implementado
Usuário persistido com senha criptografada
Proteção de rotas privadas
Logout funcionando
Testes básicos executadosSubtarefas de desenvolvimento
Criar tabela users
Criar seed com 3 usuários de teste
Implementar endpoint /auth/login
Implementar hash de senha
Implementar geração/validação de token ou sessão
Criar middleware de autenticação
Criar tela de login
Proteger rotas internas
Implementar logout
Testar fluxo completo"



"US02: Perfis
Administrador - Otávio
Gerente - Tainá
Manutentores - Michael, Leonardo e Murillo
Acessos
Administrador: Acesso total
Gerente: Acesso total, criação e encaminhamento de OS, programação da manutenção
Manutentores: Executores"


"US05: Setores:
Administração
Produção
Expedição
Manutenção
UtilidadesEquipamentos:
Administração
- Computadores: PC-01,  PC-02, ...
- Infraestrutura (lâmpadas, tomadas, mesas e cadeiras, estrutura): LAMP-01, LAMP-02, ...; TOM-01, TOM-02, ...;Equipamentos:
Produção
- Maquinário: MAQ-01, MAQ-02, ...
- Infraestrutura (lâmpadas, tomadas, mesas e cadeiras, estrutura): LAMP-01, LAMP-02, ...; TOM-01, TOM-02, ...;
Equipamentos:
Expedição
- Maquinario: EMP-01, EMP-02, ...; PLT-01, PLT-02, ...;
- Infraestrutura (lâmpadas, tomadas, estrutura)
Equipamentos:
Manutenção
- FerramentasEquipamentos:
Utilidades
- Compressores: COMP-01, COMP-02, ...
- Geradores: GER-01, GER-02, ...
- Ar-condicionados: AR-01, AR-02, ...
- etc"

"US04: Administrador: Otavio
Gerente: Tainá
Operador: Michael, Murilo, Leonardo-Criar usuário com: nome, email, senha, perfil
-Não permitir email duplicado
-Listar usuários com busca/filtro
-Editar dados (exceto senha inicialmente — opcional)
-Desativar usuário (soft delete)
-Apenas admin/gerente podem acessar"



"US06: Como administrador ou gerente
Quero cadastrar, editar, visualizar e remover equipes
Para organizar a alocação de responsáveis nas ordens de serviçCriar equipe
Entrada: nome, descrição, setor
Saída: equipe criada com status ativoDefinição de Regras de Negócio
Nome da equipe deve ser único
Equipes inativas não podem ser utilizadas em novos vínculos
Não é permitido excluir equipe fisicamente
Usuários devem estar vinculados a equipes ativas"




"US09: Medições:
Vibrações
Temperatura
Tensão
CorrenteUnidades de vibração:
Velocidade de vibração (mm/s ou pol/s)
Aceleração de vibração (m/s^2 ou pol/s^2)
Deslocamento de vibração (um ou mm)
Frequência (Hz)
RMS (Root Mean Square)
Pico a pico (pp)Unidades de tensão
Volts (V)
- Tensão nominal
- Tensão de partida
- Tensão sob trabalho 
Unidades de corrente
Amperes (A)
- Corrente nominal
- Corrente de partida (pico de corrente)
- Corrente sob trabalho "





"US08: Como operador ou gerente
Quero registrar uma ocorrência em um equipamento
Para documentar falhas, riscos e eventos que impactam a operaçãoOcorrência sempre vinculada a um único equipamento
Timestamp padrão = data/hora atual
Severidade pode ser usada futuramente para alertas/OS
Se “parada de produção = sim”, destacar ocorrência (flag visual)
Não permitir salvar ocorrência sem descrição válida"
": Ideia Central

Registrar eventos anormais ou falhas em equipamentos de forma padronizada, permitindo rastreabilidade, análise e geração futura de ordens de serviço."
": Listar ocorrências
GET /ocorrencias
Implementar:
Paginação
Filtros:
equipamento
severidade
status
períodoDetalhar ocorrência
GET /ocorrencias/{id}Validações
Campos obrigatórios:
equipamento
tipo
severidade
descricao
Validar enums
Validar equipamento existenteTestes
Criar ocorrência válida
Criar ocorrência sem campos obrigatórios → erro
Editar ocorrência
Listar com filtros
Verificar permissõesResultado esperado
Usuário registra ocorrência rapidamente
Dados ficam padronizados
Base pronta para alertas e OS"