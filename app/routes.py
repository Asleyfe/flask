from flask import render_template, flash, redirect, url_for, request, session
from app import app
from . import modelo_negocio as mn # Importa a lógica POO

# IMPORTANTE: Garanta que app.secret_key está configurado no app/__init__.py


# --- Função Auxiliar ---
def get_current_user():
    """Busca o objeto User (Professor ou Aluno) logado no dicionário global."""
    matricula = session.get('usuario_matricula')
    if matricula:
        return mn.TODOS_USUARIOS.get(matricula)
    return None

# ----------------------------------------------------
# 0. Rota Padrão: MENU DE AUTENTICAÇÃO
# ----------------------------------------------------
@app.route('/')
def inicio():
    if 'usuario_matricula' in session:
        return redirect(url_for('dashboard'))
    return render_template('inicio.html', titulo='Bem-vindo ao GT PIM')


# ----------------------------------------------------
# 1. Rotas de Autenticação e Cadastro
# ----------------------------------------------------
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        matricula = request.form.get('matricula')
        funcao = request.form.get('funcao')
        
        # Chama a lógica POO de criação
        sucesso, mensagem = mn.criar_novo_usuario(nome, matricula, funcao)
        
        if sucesso:
            flash(f'{mensagem} Use a matrícula {matricula} para entrar.', 'success')
            return redirect(url_for('inicio')) 
        else:
            flash(f'Erro ao cadastrar: {mensagem}', 'danger')
            return render_template('cadastro.html', titulo='Cadastrar Usuário', nome=nome, matricula=matricula)

    return render_template('cadastro.html', titulo='Cadastrar Usuário')

@app.route('/login', methods=['POST'])
def login():
    matricula = request.form.get('matricula')
    
    usuario_obj = mn.validar_login(matricula) # Retorna o objeto User/Professor/Aluno
    
    if usuario_obj:
        # Armazena APENAS dados simples (string/int) na sessão
        session['usuario_matricula'] = usuario_obj.matricula
        session['usuario_nome'] = usuario_obj.name
        session['usuario_funcao'] = usuario_obj.funcao
        
        flash(f'Bem-vindo(a), {session["usuario_nome"]}!', 'success')
        return redirect(url_for('dashboard')) 
    else:
        flash('Matrícula não encontrada. Tente novamente ou cadastre-se.', 'danger')
        return redirect(url_for('inicio'))

@app.route('/logout')
def logout():
    session.pop('usuario_matricula', None)
    session.pop('usuario_nome', None)
    session.pop('usuario_funcao', None)
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('inicio'))


# ----------------------------------------------------
# 2. DASHBOARD (Página Principal após login)
# ----------------------------------------------------
@app.route('/dashboard')
def dashboard():
    usuario_obj = get_current_user()
    if not usuario_obj:
        flash('Você precisa fazer login para acessar o dashboard.', 'info')
        return redirect(url_for('inicio'))
    
    # Prepara o contexto
    contexto = {
        'titulo': 'Dashboard',
        'usuario_logado': usuario_obj.name,
        'funcao_logado': usuario_obj.funcao,
        'total_usuarios': len(mn.TODOS_USUARIOS),
        'professores': mn.listar_turmas_disponiveis(), # Usando a função para listar turmas
        'turmas': mn.listar_turmas_disponiveis() # Usando a função para listar turmas
    }
    # O index.html agora é o dashboard, exibindo dados e menus específicos
    return render_template('index.html', **contexto) 


# ----------------------------------------------------
# 3. AÇÕES DO PROFESSOR
# ----------------------------------------------------
@app.route('/professor/criar_turma', methods=['GET', 'POST'])
def criar_turma_web():
    usuario_obj = get_current_user()
    
    # 1. Proteção: requer login e ser professor
    if not usuario_obj or usuario_obj.funcao != 'professor':
        flash('Acesso negado. Você deve ser um professor logado.', 'danger')
        return redirect(url_for('dashboard'))

    # Já sabemos que é um Professor, podemos usar os métodos da classe Professor
    professor_obj = usuario_obj

    if request.method == 'POST':
        curso = request.form.get('curso')
        materia = request.form.get('materia')
        vagas_str = request.form.get('vagas')
        
        try:
            vagas = int(vagas_str)
        except ValueError:
            flash('O campo Vagas deve ser um número inteiro.', 'danger')
            return redirect(url_for('criar_turma_web'))
            
        # Chama o método do OBJETO Professor
        sucesso, mensagem = professor_obj.create_turma(curso, materia, vagas)
        
        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Erro ao criar turma: {mensagem}', 'danger')

    # Método GET: Exibe o formulário
    return render_template(
        'criar_turma.html', 
        titulo='Criar Nova Turma', 
        professor=professor_obj.name
    )


# ----------------------------------------------------
# 4. AÇÕES DO ALUNO (Exemplo: Entrar em Turma)
# ----------------------------------------------------
@app.route('/aluno/entrar_turma/<registro_turma>', methods=['POST'])
def entrar_turma_web(registro_turma):
    usuario_obj = get_current_user()
    
    # 1. Proteção: requer login e ser aluno
    if not usuario_obj or usuario_obj.funcao != 'aluno':
        flash('Ação restrita a alunos logados.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Já sabemos que é um Aluno
    aluno_obj = usuario_obj
    
    # Chama o método do OBJETO Aluno
    sucesso, mensagem = aluno_obj.entrar_turma(registro_turma)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(f'Erro na matrícula: {mensagem}', 'danger')
        
    return redirect(url_for('dashboard'))

# ----------------------------------------------------
# 5. Rota: MENU DE CONTEÚDO DO PROFESSOR (Lista as turmas para escolha)
# ----------------------------------------------------
@app.route('/professor/gerenciar', methods=['GET'])
def gerenciar_conteudo_menu():
    usuario_obj = get_current_user()
    
    if not usuario_obj or usuario_obj.funcao != 'professor':
        flash('Acesso negado. Apenas professores podem gerenciar conteúdo.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Lista as turmas criadas por este professor
    turmas_do_professor = usuario_obj.turmas_criadas.values()
    
    return render_template(
        'gerenciar_conteudo_menu.html',
        titulo='Gerenciar Conteúdo',
        turmas=turmas_do_professor
    )


# ----------------------------------------------------
# 6. Rota: INSERIR AULA/ATIVIDADE (Formulário real)
# ----------------------------------------------------
@app.route('/professor/turma/<registro_turma>/inserir_conteudo', methods=['GET', 'POST'])
def inserir_conteudo_web(registro_turma):
    usuario_obj = get_current_user()
    
    if not usuario_obj or usuario_obj.funcao != 'professor':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))

    turma = mn.TODAS_TURMAS.get(registro_turma)
    
    # Verifica se a turma existe e se pertence ao professor
    if not turma or turma.professor.matricula != usuario_obj.matricula:
        flash('Turma não encontrada ou você não tem permissão para editá-la.', 'danger')
        return redirect(url_for('gerenciar_conteudo_menu'))

    if request.method == 'POST':
        tipo = request.form.get('tipo_conteudo')
        data_str = request.form.get('data')
        descricao = request.form.get('descricao')
        nome_atividade = request.form.get('nome_atividade')
        anexo_pdf = request.form.get('anexo_pdf', 'N/A') # Simplesmente armazena a string 'N/A'

        sucesso = False
        
        if tipo == 'aula':
            sucesso, mensagem = usuario_obj.inserir_aula(registro_turma, data_str, descricao)
        elif tipo == 'atividade':
            sucesso, mensagem = usuario_obj.criar_atividade_nova(registro_turma, nome_atividade, data_str, anexo_pdf, descricao)
        else:
            mensagem = "Tipo de conteúdo inválido."

        if sucesso:
            flash(mensagem, 'success')
            # Redireciona de volta para o menu de gerenciamento de conteúdo daquela turma (se tivéssemos um)
            return redirect(url_for('dashboard')) 
        else:
            flash(f'Erro: {mensagem}', 'danger')
            # Permite que o usuário tente novamente
            
    return render_template(
        'inserir_conteudo.html',
        titulo=f'Inserir Conteúdo em {turma.materia}',
        turma=turma
    )
# ----------------------------------------------------
# 7. Rota: DETALHES DA TURMA (Visualização de Conteúdo)
# ----------------------------------------------------
@app.route('/turma/<registro_turma>')
def detalhes_turma(registro_turma):
    usuario_obj = get_current_user()
    if not usuario_obj:
        flash('Você precisa fazer login para acessar o conteúdo.', 'info')
        return redirect(url_for('inicio'))
        
    turma = mn.TODAS_TURMAS.get(registro_turma)
    
    if not turma:
        flash(f'Turma com registro {registro_turma} não encontrada.', 'danger')
        return redirect(url_for('dashboard'))
        
    # Verifica permissão: Aluno deve estar matriculado OU ser o professor
    pode_acessar = (usuario_obj.matricula in turma.alunos) or \
                  (usuario_obj.matricula == turma.professor.matricula)
                  
    if not pode_acessar:
        flash('Acesso negado. Você não está matriculado(a) nesta turma.', 'danger')
        return redirect(url_for('dashboard'))

    # Prepara os dados para o template
    aulas_detalhes = [aula.get_details_aula() for aula in turma.aulas]
    atividades_detalhes = [ativ.get_details_atividade() for ativ in turma.atividades]
    
    contexto = {
        'titulo': f'Conteúdo: {turma.materia} - {turma.curso}',
        'turma': turma,
        'aulas': aulas_detalhes,
        'atividades': atividades_detalhes,
        'is_professor': usuario_obj.funcao == 'professor'
    }

    return render_template('detalhes_turma.html', **contexto)


# ----------------------------------------------------
# 10. Rota: MINHAS TURMAS (Painel do Aluno)
# ----------------------------------------------------
@app.route('/aluno/minhas_turmas')
def minhas_turmas_web():
    usuario_obj = get_current_user()
    
    # 1. Proteção: requer login e ser aluno
    if not usuario_obj:
        flash('Você precisa fazer login para acessar esta página.', 'info')
        return redirect(url_for('inicio'))
        
    if usuario_obj.funcao != 'aluno':
        flash('Acesso restrito a Alunos.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Já sabemos que é um objeto Aluno, podemos acessar a propriedade turmas_matriculadas
    aluno_obj = usuario_obj
    
    # Prepara os dados: queremos uma lista dos objetos Turma
    turmas_matriculadas = list(aluno_obj.turmas_matriculadas.values())
    
    # Prepara os detalhes de cada turma para o template
    turmas_detalhes = []
    for turma in turmas_matriculadas:
        turmas_detalhes.append({
            'registro': turma.registro_turma,
            'materia': turma.materia,
            'curso': turma.curso,
            'professor': turma.professor.name,
            'total_aulas': len(turma.aulas),
            'total_atividades': len(turma.atividades)
        })

    contexto = {
        'titulo': 'Minhas Turmas Matriculadas',
        'turmas': turmas_detalhes,
        'aluno_nome': aluno_obj.name
    }

    return render_template('minhas_turmas.html', **contexto)
# ----------------------------------------------------
# 11. Rota: CONTEÚDO PENDENTE (Visão Agregada do Aluno)
# ----------------------------------------------------
@app.route('/aluno/conteudo_pendente')
def conteudo_pendente_web():
    usuario_obj = get_current_user()
    
    # Proteção: requer login e ser aluno
    if not usuario_obj or usuario_obj.funcao != 'aluno':
        flash('Acesso restrito a Alunos.', 'danger')
        return redirect(url_for('dashboard'))
        
    aluno_obj = usuario_obj
    
    # ⚠️ ASSUMINDO que o método consultar_atividades_pendentes está no objeto Aluno
    atividades = []
    
    # Lógica de coleta de todas as turmas e atividades pendentes
    for turma in aluno_obj.turmas_matriculadas.values():
        for atividade in turma.atividades:
            # Em um sistema real, você checaria se o aluno já entregou
            # Aqui, listamos todas as atividades para fins de demonstração da interface.
            atividades.append({
                'turma_materia': turma.materia,
                'turma_registro': turma.registro_turma,
                'nome': atividade.nome,
                'data_entrega': atividade.data_entrega.strftime('%d/%m/%Y'),
                'link_detalhes': url_for('detalhes_turma', registro_turma=turma.registro_turma),
                'descricao': atividade.descricao
            })

    # Ordenar as atividades pela data de entrega (mais próximas primeiro)
    # (Não podemos fazer isso sem o código de Turma/Atividade, mas é uma boa prática)

    contexto = {
        'titulo': 'Atividades Pendentes',
        'atividades': atividades,
        'aluno_nome': aluno_obj.name
    }

    return render_template('conteudo_pendente.html', **contexto)
@app.route('/contato')
def contato():
    return render_template('contato.html', titulo='Entre em Contato')
