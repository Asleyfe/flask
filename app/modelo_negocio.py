from datetime import datetime

# --- Estruturas de Dados Globais (Simulando um DB) ---
# Dicionários que armazenarão instâncias de objetos (e não dados simples)
TODOS_USUARIOS = {}  # {matricula: <instância de User/Professor/Aluno>}
TODAS_TURMAS = {}    # {registro: <instância de Turma>}

# --- 1. Classes de Entidades do Sistema ---

class Aula:
    def __init__(self, materia: str, professor_nome: str, data: datetime, descricao: str):
        self.materia = materia
        self.professor = professor_nome
        self.data = data
        self.descricao = descricao

    def get_details_aula(self) -> dict:
        """Retorna os detalhes da aula."""
        return {
            'materia': self.materia,
            'professor': self.professor,
            'data': self.data.strftime("%d/%m/%Y %H:%M"),
            'descricao': self.descricao
        }

class Atividade:
    def __init__(self, nome_atividade: str, materia: str, professor_nome: str, data_entrega: datetime, anexo_pdf: str):
        self.name_atividade = nome_atividade
        self.materia = materia
        self.professor = professor_nome
        self.data = data_entrega
        self.anexo_pdf = anexo_pdf
        self.descricao = "" # Atributo inicializado

    def get_details_atividade(self) -> dict:
        """Retorna os detalhes da atividade."""
        return {
            'nome': self.name_atividade,
            'materia': self.materia,
            'data_entrega': self.data.strftime("%d/%m/%Y"),
            'professor': self.professor,
            'anexo': self.anexo_pdf
        }

# --- 2. Classe Turma ---

class Turma:
    def __init__(self, curso: str, materia: str, vagas: int, professor_obj):
        self.registro_turma = f"{curso}-{materia}-{professor_obj.matricula}"
        self.curso = curso
        self.materia = materia
        self.vagas = vagas
        self.professor = professor_obj  # Referência ao objeto Professor
        self.alunos = {}  # {matricula: <objeto Aluno>}
        self.aulas = []   # Lista de objetos Aula
        self.atividades = [] # Lista de objetos Atividade

    def calcular_vagas(self) -> int:
        """Calcula o número de vagas restantes."""
        return self.vagas - len(self.alunos)

    def get_alunos(self) -> list:
        """Retorna uma lista de objetos Aluno matriculados."""
        return list(self.alunos.values())

# --- 3. Hierarquia de Usuários (POO com Herança) ---

class User:
    def __init__(self, name: str, matricula: str, funcao: str):
        self.name = name
        self.matricula = matricula
        self.funcao = funcao
    
    # Método para ser usado pelas rotas Flask
    def get_dados_basicos(self) -> dict:
        return {'nome': self.name, 'matricula': self.matricula, 'funcao': self.funcao}

class Professor(User):
    def __init__(self, name: str, matricula: str):
        # Herda atributos de User
        super().__init__(name, matricula, "professor")
        self.turmas_criadas = {} # {registro_turma: <objeto Turma>}

    def create_turma(self, curso: str, materia: str, vagas: int) -> tuple:
        """Cria uma nova turma e a associa ao professor."""
        
        # O registro garante unicidade baseada em curso-materia-professor
        registro = f"{curso}-{materia}-{self.matricula}"
        
        if registro in TODAS_TURMAS:
            return False, f"Turma com registro '{registro}' já existe."
        
        # Instancia a nova Turma
        nova_turma = Turma(curso, materia, vagas, self)
        
        # Adiciona às estruturas de dados
        TODAS_TURMAS[registro] = nova_turma
        self.turmas_criadas[registro] = nova_turma
        
        return True, f"Turma '{registro}' criada com sucesso."

    def insert_aula(self, registro_turma: str, data_str: str, descricao: str) -> tuple:
        """Insere uma nova aula na turma."""
        turma = TODAS_TURMAS.get(registro_turma)
        
        if not turma or turma.professor.matricula != self.matricula:
            return False, "Turma não encontrada ou você não é o professor responsável."
        
        try:
            data_aula = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            return False, "Formato de data inválido. Use DD/MM/AAAA."

        nova_aula = Aula(turma.materia, self.name, data_aula, descricao)
        turma.aulas.append(nova_aula)
        return True, f"Aula inserida em {turma.curso}."

    def consultar_aulas(self, registro_turma: str) -> list:
        """Lista todas as aulas de uma turma específica."""
        turma = TODAS_TURMAS.get(registro_turma)
        if turma and turma.professor.matricula == self.matricula:
            return [aula.get_details_aula() for aula in turma.aulas]
        return []
    
    def inserir_aula(self, registro_turma: str, data_str: str, descricao: str) -> tuple:
        """Insere uma nova aula na turma."""
        turma = TODAS_TURMAS.get(registro_turma)
        
        if not turma or turma.professor.matricula != self.matricula:
            return False, "Turma não encontrada ou você não é o professor responsável."
        
        try:
            # Assumindo que a data vem no formato DD/MM/AAAA
            data_aula = datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            return False, "Formato de data inválido. Use DD/MM/AAAA."

        nova_aula = Aula(turma.materia, self.name, data_aula, descricao)
        turma.aulas.append(nova_aula)
        return True, f"Aula '{descricao[:20]}...' inserida na turma {turma.materia}."
        
    def criar_atividade_nova(self, registro_turma: str, nome_atividade: str, data_entrega_str: str, anexo_pdf: str, descricao: str) -> tuple:
        """Cria e insere uma nova atividade na turma."""
        turma = TODAS_TURMAS.get(registro_turma)

        if not turma or turma.professor.matricula != self.matricula:
            return False, "Turma não encontrada ou você não é o professor responsável."

        try:
            data_entrega = datetime.strptime(data_entrega_str, "%d/%m/%Y")
        except ValueError:
            return False, "Formato de data de entrega inválido. Use DD/MM/AAAA."
            
        # Verifica duplicidade simples
        if any(a.name_atividade == nome_atividade for a in turma.atividades):
             return False, f"Atividade com o nome '{nome_atividade}' já existe nesta turma."

        # Instancia a nova Atividade
        nova_atividade = Atividade(
            nome_atividade=nome_atividade,
            materia=turma.materia,
            professor_nome=self.name,
            data_entrega=data_entrega,
            anexo_pdf=anexo_pdf # Em um sistema real, seria o caminho do arquivo
        )
        nova_atividade.descricao = descricao
        turma.atividades.append(nova_atividade)
        
        return True, f"Atividade '{nome_atividade}' criada e adicionada à turma {turma.materia}."

class Aluno(User):
    def __init__(self, name: str, matricula: str):
        super().__init__(name, matricula, "aluno")
        self.turmas_matriculadas = {} # {registro_turma: <objeto Turma>}

    def entrar_turma(self, registro_turma: str) -> tuple:
        """Matricula o aluno em uma turma."""
        turma = TODAS_TURMAS.get(registro_turma)
        
        if not turma:
            return False, "Turma não encontrada."
        
        if turma.calcular_vagas() <= 0:
            return False, "Turma sem vagas disponíveis."
        
        if self.matricula in turma.alunos:
            return False, "Você já está matriculado nesta turma."
        
        # Realiza a matrícula
        turma.alunos[self.matricula] = self
        self.turmas_matriculadas[registro_turma] = turma
        
        return True, f"Matrícula realizada com sucesso na turma de {turma.materia}."
    
    def buscar_atividade(self, registro_turma: str, nome_atividade: str) -> Atividade or None:
        """Busca uma atividade específica em uma turma matriculada."""
        turma = self.turmas_matriculadas.get(registro_turma)
        if turma:
            for atividade in turma.atividades:
                if atividade.name_atividade == nome_atividade:
                    return atividade
        return None

# --- Funções de Gerenciamento do Sistema (Usadas pelas Rotas Flask) ---

def criar_novo_usuario(name: str, matricula: str, funcao: str) -> tuple:
    """Função wrapper para instanciar a classe correta."""
    if matricula in TODOS_USUARIOS:
        return False, "Matrícula já existente."
    
    funcao = funcao.lower()
    
    if funcao == "professor":
        novo_usuario = Professor(name, matricula)
    elif funcao == "aluno":
        novo_usuario = Aluno(name, matricula)
    else:
        return False, "Função inválida. Use 'professor' ou 'aluno'."
        
    TODOS_USUARIOS[matricula] = novo_usuario
    return True, f"Usuário {name} ({funcao}) criado com sucesso."

def validar_login(matricula: str) -> User or None:
    """Retorna o objeto User/Professor/Aluno se a matrícula existir."""
    return TODOS_USUARIOS.get(matricula, None)

def listar_turmas_disponiveis() -> list:
    """Retorna uma lista de dados de turmas disponíveis."""
    lista = []
    for registro, turma in TODAS_TURMAS.items():
        lista.append({
            'registro': registro,
            'curso': turma.curso,
            'materia': turma.materia,
            'professor': turma.professor.name,
            'vagas_restantes': turma.calcular_vagas()
        })
    return lista


# --- Pré-carregamento de Dados (Para Teste) ---

# 1. Criação de usuários
criar_novo_usuario("Dr. Silva", "P001", "professor")
criar_novo_usuario("Ms. Oliveira", "P002", "professor")
criar_novo_usuario("João Aluno", "A010", "aluno")

# 2. Criação de turmas pelo P001
professor_silva = TODOS_USUARIOS["P001"]
professor_silva.create_turma("Engenharia", "POO", 15)
professor_silva.create_turma("Engenharia", "BD", 10)

# 3. Matrícula de aluno
aluno_joao = TODOS_USUARIOS["A010"]
aluno_joao.entrar_turma("Engenharia-POO-P001")