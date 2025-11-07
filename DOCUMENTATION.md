# Documentação da Aplicação Flask - GT PIM

Este documento descreve a estrutura e as funcionalidades principais da aplicação Flask "GT PIM", que simula um sistema de gerenciamento de turmas, aulas e atividades para professores e alunos.

## 1. Estrutura do Projeto

A aplicação segue uma estrutura modular típica de projetos Flask:

```
.
├── app/
│   ├── __init__.py             # Inicialização da aplicação Flask
│   ├── modelo_negocio.py       # Lógica de negócio (classes e funções POO)
│   ├── routes.py               # Definição das rotas e lógica de controle
│   └── templates/              # Arquivos HTML (templates Jinja2)
│       ├── base.html
│       ├── cadastro.html
│       ├── contato.html
│       ├── criar_turma.html
│       ├── detalhes_turma.html
│       ├── gerenciar_conteudo_menu.html
│       ├── index.html
│       ├── inicio.html
│       └── inserir_conteudo.html
├── .flaskenv                   # Variáveis de ambiente para o Flask
└── microblog.py                # Ponto de entrada da aplicação
```

## 2. Componentes Principais

### `app/__init__.py`
- Inicializa a instância da aplicação Flask.
- Configura a `app.secret_key` para o uso de sessões.
- Importa as rotas (`app.routes`) para evitar problemas de dependência circular.

### `app/modelo_negocio.py`
Este arquivo contém a lógica de negócio da aplicação, implementada com Programação Orientada a Objetos (POO). Ele simula um banco de dados usando dicionários globais.

#### Estruturas de Dados Globais (Simuladas)
- `TODOS_USUARIOS`: Dicionário que armazena instâncias de `User`, `Professor` ou `Aluno` (chave: matrícula).
- `TODAS_TURMAS`: Dicionário que armazena instâncias de `Turma` (chave: registro da turma).

#### Classes de Entidades
- **`Aula`**:
    - Representa uma aula com atributos como matéria, nome do professor, data e descrição.
    - `get_details_aula()`: Retorna um dicionário com os detalhes formatados da aula.
- **`Atividade`**:
    - Representa uma atividade com nome, matéria, nome do professor, data de entrega, anexo PDF e descrição.
    - `get_details_atividade()`: Retorna um dicionário com os detalhes formatados da atividade.
- **`Turma`**:
    - Representa uma turma com registro único, curso, matéria, vagas, professor responsável, alunos matriculados, aulas e atividades.
    - `calcular_vagas()`: Calcula as vagas restantes na turma.
    - `get_alunos()`: Retorna uma lista dos objetos `Aluno` matriculados.

#### Hierarquia de Usuários
- **`User`**:
    - Classe base para todos os usuários, com atributos como nome, matrícula e função.
    - `get_dados_basicos()`: Retorna um dicionário com os dados básicos do usuário.
- **`Professor` (Herda de `User`)**:
    - Representa um professor, com a capacidade de criar e gerenciar turmas, inserir aulas e atividades.
    - `turmas_criadas`: Dicionário de turmas criadas pelo professor.
    - `create_turma(curso, materia, vagas)`: Cria uma nova turma.
    - `insert_aula(registro_turma, data_str, descricao)`: Insere uma aula em uma turma.
    - `consultar_aulas(registro_turma)`: Lista as aulas de uma turma.
    - `inserir_aula(registro_turma, data_str, descricao)`: Insere uma aula (duplicidade com `insert_aula`, verificar).
    - `criar_atividade_nova(registro_turma, nome_atividade, data_entrega_str, anexo_pdf, descricao)`: Cria e insere uma atividade.
- **`Aluno` (Herda de `User`)**:
    - Representa um aluno, com a capacidade de se matricular em turmas.
    - `turmas_matriculadas`: Dicionário de turmas em que o aluno está matriculado.
    - `entrar_turma(registro_turma)`: Matricula o aluno em uma turma.
    - `buscar_atividade(registro_turma, nome_atividade)`: Busca uma atividade específica.

#### Funções de Gerenciamento do Sistema
- `criar_novo_usuario(name, matricula, funcao)`: Cria uma instância de `Professor` ou `Aluno` e a adiciona a `TODOS_USUARIOS`.
- `validar_login(matricula)`: Retorna o objeto usuário se a matrícula existir.
- `listar_turmas_disponiveis()`: Retorna uma lista de dicionários com detalhes das turmas.

#### Pré-carregamento de Dados
O arquivo inclui um bloco para pré-carregar alguns usuários e turmas para fins de teste.

### `app/routes.py`
Define as rotas da aplicação Flask e a lógica de controle para cada endpoint. Interage com a lógica de negócio definida em `modelo_negocio.py`.

#### Funções Auxiliares
- `get_current_user()`: Obtém o objeto do usuário logado a partir da sessão.

#### Rotas Principais
- **`/` (inicio)**: Página inicial de autenticação. Redireciona para o dashboard se o usuário já estiver logado.
- **`/cadastro`**: Permite o cadastro de novos usuários (professores ou alunos).
- **`/login`**: Processa o login do usuário, armazenando dados na sessão.
- **`/logout`**: Encerra a sessão do usuário.
- **`/dashboard`**: Página principal após o login, exibindo informações e menus específicos para professores e alunos.
- **`/professor/criar_turma`**: Formulário e lógica para professores criarem novas turmas.
- **`/aluno/entrar_turma/<registro_turma>`**: Lógica para alunos se matricularem em turmas.
- **`/professor/gerenciar`**: Menu para professores gerenciarem o conteúdo de suas turmas.
- **`/professor/turma/<registro_turma>/inserir_conteudo`**: Formulário e lógica para professores inserirem aulas ou atividades em uma turma específica.
- **`/turma/<registro_turma>`**: Exibe os detalhes e o conteúdo (aulas e atividades) de uma turma. Requer login e permissão (aluno matriculado ou professor da turma).
- **`/gerenciar_conteudo`**: Rota duplicada de `/professor/gerenciar` (verificar e remover duplicidade).
- **`/inserir_conteudo/<registro_turma>`**: Rota duplicada de `/professor/turma/<registro_turma>/inserir_conteudo` (verificar e remover duplicidade).
- **`/contato`**: Página de contato estática.

### `app/templates/`
Contém os arquivos HTML que definem a interface do usuário. Utiliza Jinja2 para renderização dinâmica.

- `base.html`: Template base para todas as páginas, incluindo cabeçalho, navegação e rodapé.
- `inicio.html`: Página de boas-vindas e formulário de login.
- `cadastro.html`: Formulário de cadastro de usuário.
- `index.html`: Dashboard principal após o login.
- `criar_turma.html`: Formulário para criar uma nova turma.
- `gerenciar_conteudo_menu.html`: Lista as turmas para o professor gerenciar conteúdo.
- `inserir_conteudo.html`: Formulário para inserir aulas ou atividades.
- `detalhes_turma.html`: Exibe o conteúdo detalhado de uma turma.
- `contato.html`: Página de contato.

## 3. Funcionalidades Resumidas

- **Autenticação e Autorização**:
    - Cadastro de usuários como "professor" ou "aluno".
    - Login e logout com gerenciamento de sessão.
    - Rotas protegidas que exigem login e/ou função específica (professor/aluno).
- **Gerenciamento de Turmas (Professor)**:
    - Professores podem criar novas turmas, especificando curso, matéria e vagas.
    - Professores podem inserir aulas e atividades em suas turmas.
    - Visualização das turmas criadas pelo professor.
- **Matrícula em Turmas (Aluno)**:
    - Alunos podem se matricular em turmas disponíveis, respeitando o limite de vagas.
    - Alunos podem visualizar o conteúdo (aulas e atividades) das turmas em que estão matriculados.
- **Visualização de Conteúdo**:
    - Detalhes de aulas e atividades são exibidos nas páginas das turmas.
- **Simulação de Banco de Dados**:
    - Utiliza dicionários em memória para armazenar dados de usuários e turmas, facilitando o desenvolvimento e teste sem a necessidade de um banco de dados real.

## 4. Próximos Passos / Melhorias Potenciais

- **Persistência de Dados**: Integrar com um banco de dados real (SQLite, PostgreSQL, etc.) para que os dados não sejam perdidos ao reiniciar a aplicação.
- **Validação de Formulários**: Melhorar a validação de entrada de dados nos formulários (ex: datas, campos obrigatórios).
- **Tratamento de Erros**: Implementar um tratamento de erros mais robusto e páginas de erro personalizadas.
- **Refatoração de Rotas**: Remover rotas duplicadas em `app/routes.py` (`/gerenciar_conteudo` e `/inserir_conteudo/<registro_turma>`).
- **Interface do Usuário**: Melhorar a experiência do usuário e o design das páginas.
- **Funcionalidades Adicionais**:
    - Edição/Exclusão de turmas, aulas e atividades.
    - Upload real de arquivos PDF para atividades.
    - Sistema de notas/entregas de atividades para alunos.
    - Mensagens entre usuários.
