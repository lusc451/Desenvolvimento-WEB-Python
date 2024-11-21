from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import mysql.connector
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)


# Testando conexão com o banco de dados
try:
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
except:
    print("Ocorreu um erro ao se conectar com o banco de dados.")
if conn and conn.is_connected():
    print("Conexão com o banco de dados estabelecida com sucesso.")
    conn.close()

@app.route('/')
def index():
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM LucasAntunes_tbdisciplinas")
        total_disciplinas = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM LucasAntunes_tbcursos")
        total_cursos = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM LucasAntunes_tbprofessores")
        total_professores = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM LucasAntunes_tbalunos")
        total_alunos = cursor.fetchone()['total']
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'index.html',
        total_disciplinas=total_disciplinas,
        total_cursos=total_cursos,
        total_professores=total_professores,
        total_alunos=total_alunos
    )


# Cadastro de Disciplinas
@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    # Inserir nova disciplina
    if request.method == 'POST':
        nome = request.form['nome']
        carga_horaria = request.form['carga_horaria']
        cursor.execute("INSERT INTO LucasAntunes_tbdisciplinas (nome, carga_horaria) VALUES (%s, %s)", (nome, carga_horaria))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('disciplinas'))

    # Buscar disciplinas (opcional, filtro por nome)
    search = request.args.get('search', '')
    if search:
        cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas WHERE nome LIKE %s", (f"%{search}%",))
    else:
        cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
    disciplinas = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('disciplinas.html', disciplinas=disciplinas, search=search)


@app.route('/disciplinas/edit/<int:id>', methods=['GET', 'POST'])
def edit_disciplina(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        carga_horaria = request.form['carga_horaria']
        cursor.execute("UPDATE LucasAntunes_tbdisciplinas SET nome = %s, carga_horaria = %s WHERE id = %s", (nome, carga_horaria, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('disciplinas'))

    cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas WHERE id = %s", (id,))
    disciplina = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_disciplina.html', disciplina=disciplina)


@app.route('/disciplinas/delete/<int:id>', methods=['POST'])
def delete_disciplina(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor()
    try:
        # Removendo associações na tabela cursos_disciplinas
        cursor.execute("DELETE FROM LucasAntunes_tbcursos_disciplinas WHERE disciplina_id = %s", (id,))
        # Excluindo a disciplina
        cursor.execute("DELETE FROM LucasAntunes_tbdisciplinas WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        return f"Erro ao excluir: {e}", 400
    finally:
        cursor.close()
        conn.close()
    return redirect('/disciplinas')




# Cadastro de Cursos
@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'POST':
            # Inserir novo curso
            nome = request.form['nome']
            disciplinas = request.form.getlist('disciplinas')

            cursor.execute("INSERT INTO LucasAntunes_tbcursos (nome) VALUES (%s)", (nome,))
            curso_id = cursor.lastrowid  # Pegar o ID do curso recém-criado

            # Associar disciplinas ao curso
            for disciplina_id in disciplinas:
                cursor.execute(
                    "INSERT INTO LucasAntunes_tbcursos_disciplinas (curso_id, disciplina_id) VALUES (%s, %s)",
                    (curso_id, disciplina_id)
                )

            conn.commit()
            return redirect(url_for('cursos'))

        # Lógica de busca
        search = request.args.get('search', '')
        if search:
            cursor.execute("""
                SELECT 
                    c.id AS curso_id, 
                    c.nome AS curso_nome, 
                    GROUP_CONCAT(d.nome SEPARATOR ', ') AS disciplinas
                FROM LucasAntunes_tbcursos AS c
                LEFT JOIN LucasAntunes_tbcursos_disciplinas AS cd ON c.id = cd.curso_id
                LEFT JOIN LucasAntunes_tbdisciplinas AS d ON cd.disciplina_id = d.id
                WHERE c.nome LIKE %s
                GROUP BY c.id
            """, (f"%{search}%",))
        else:
            cursor.execute("""
                SELECT 
                    c.id AS curso_id, 
                    c.nome AS curso_nome, 
                    GROUP_CONCAT(d.nome SEPARATOR ', ') AS disciplinas
                FROM LucasAntunes_tbcursos AS c
                LEFT JOIN LucasAntunes_tbcursos_disciplinas AS cd ON c.id = cd.curso_id
                LEFT JOIN LucasAntunes_tbdisciplinas AS d ON cd.disciplina_id = d.id
                GROUP BY c.id
            """)
        cursos = cursor.fetchall()

        # Buscar todas as disciplinas disponíveis
        cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
        disciplinas = cursor.fetchall()

    except mysql.connector.Error as e:
        conn.rollback()
        return f"Erro ao acessar cursos: {e}", 400
    finally:
        cursor.close()
        conn.close()

    return render_template('cursos.html', cursos=cursos, disciplinas=disciplinas, search=search)



@app.route('/cursos/edit/<int:id>', methods=['GET', 'POST'])
def edit_curso(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'POST':
            # Atualizando o nome do curso
            nome = request.form['nome']
            cursor.execute("UPDATE LucasAntunes_tbcursos SET nome = %s WHERE id = %s", (nome, id))

            # Atualizando as disciplinas associadas ao curso
            disciplinas = request.form.getlist('disciplinas')
            cursor.execute("DELETE FROM LucasAntunes_tbcursos_disciplinas WHERE curso_id = %s", (id,))
            for disciplina_id in disciplinas:
                cursor.execute(
                    "INSERT INTO LucasAntunes_tbcursos_disciplinas (curso_id, disciplina_id) VALUES (%s, %s)",
                    (id, disciplina_id)
                )

            conn.commit()
            return redirect(url_for('cursos'))

        # Consultando dados do curso
        cursor.execute("SELECT * FROM LucasAntunes_tbcursos WHERE id = %s", (id,))
        curso = cursor.fetchone()

        # Consultando todas as disciplinas
        cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
        disciplinas = cursor.fetchall()

        # Consultando disciplinas já associadas ao curso
        cursor.execute("SELECT disciplina_id FROM LucasAntunes_tbcursos_disciplinas WHERE curso_id = %s", (id,))
        curso_disciplinas = [row['disciplina_id'] for row in cursor.fetchall()]

    except mysql.connector.Error as e:
        conn.rollback()
        return f"Erro ao editar curso: {e}", 400
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_curso.html', curso=curso, disciplinas=disciplinas, curso_disciplinas=curso_disciplinas)

@app.route('/cursos/delete/<int:id>', methods=['POST'])
def delete_curso(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor()
    try:
        # Removendo associações na tabela alunos
        cursor.execute("DELETE FROM LucasAntunes_tbalunos WHERE curso_id = %s", (id,))
        # Removendo associações na tabela cursos_disciplinas
        cursor.execute("DELETE FROM LucasAntunes_tbcursos_disciplinas WHERE curso_id = %s", (id,))
        # Excluindo o curso
        cursor.execute("DELETE FROM LucasAntunes_tbcursos WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        return f"Erro ao excluir: {e}", 400
    finally:
        cursor.close()
        conn.close()
    return redirect('/cursos')

# Cadastro de Professores
@app.route('/professores', methods=['GET', 'POST'])
def professores():
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        disciplinas = request.form.getlist('disciplinas')  # Lista de IDs de disciplinas

        try:
            # Inserir o professor na tabela
            cursor.execute(
                "INSERT INTO LucasAntunes_tbprofessores (nome, telefone, usuario, senha) VALUES (%s, %s, %s, %s)",
                (nome, telefone, usuario, senha)
            )
            professor_id = cursor.lastrowid  # Obter o ID do professor recém-cadastrado

            # Associar disciplinas ao professor
            for disciplina_id in disciplinas:
                cursor.execute(
                    "INSERT INTO LucasAntunes_tbprofessores_disciplinas (professor_id, disciplina_id) VALUES (%s, %s)",
                    (professor_id, disciplina_id)
                )

            conn.commit()  # Confirmar as alterações
        except mysql.connector.Error as e:
            conn.rollback()  # Reverter a transação em caso de erro
            return f"Erro ao cadastrar professor: {e}", 400
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('professores'))

    # Lógica de busca
    search = request.args.get('search', '')
    if search:
        cursor.execute("""
            SELECT 
                p.id AS professor_id, 
                p.nome AS professor_nome, 
                p.telefone, 
                GROUP_CONCAT(d.nome SEPARATOR ', ') AS disciplinas
            FROM LucasAntunes_tbprofessores AS p
            LEFT JOIN LucasAntunes_tbprofessores_disciplinas AS pd ON p.id = pd.professor_id
            LEFT JOIN LucasAntunes_tbdisciplinas AS d ON pd.disciplina_id = d.id
            WHERE p.nome LIKE %s
            GROUP BY p.id
        """, (f"%{search}%",))
    else:
        cursor.execute("""
            SELECT 
                p.id AS professor_id, 
                p.nome AS professor_nome, 
                p.telefone, 
                GROUP_CONCAT(d.nome SEPARATOR ', ') AS disciplinas
            FROM LucasAntunes_tbprofessores AS p
            LEFT JOIN LucasAntunes_tbprofessores_disciplinas AS pd ON p.id = pd.professor_id
            LEFT JOIN LucasAntunes_tbdisciplinas AS d ON pd.disciplina_id = d.id
            GROUP BY p.id
        """)
    professores = cursor.fetchall()

    # Buscar todas as disciplinas disponíveis para o formulário
    cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
    disciplinas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('professores.html', professores=professores, disciplinas=disciplinas, search=search)

@app.route('/professores/edit/<int:id>', methods=['GET', 'POST'])
def edit_professor(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Atualizar informações do professor
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        disciplinas = request.form.getlist('disciplinas')  # Recebe lista de IDs de disciplinas

        try:
            # Atualiza os dados do professor
            cursor.execute(
                "UPDATE LucasAntunes_tbprofessores SET nome = %s, telefone = %s, usuario = %s, senha = %s WHERE id = %s",
                (nome, telefone, usuario, senha, id)
            )

            # Remove todas as disciplinas associadas ao professor
            cursor.execute("DELETE FROM LucasAntunes_tbprofessores_disciplinas WHERE professor_id = %s", (id,))

            # Insere novamente as disciplinas selecionadas
            for disciplina_id in disciplinas:
                cursor.execute(
                    "INSERT INTO LucasAntunes_tbprofessores_disciplinas (professor_id, disciplina_id) VALUES (%s, %s)",
                    (id, disciplina_id)
                )

            conn.commit()

        except mysql.connector.Error as e:
            conn.rollback()  # Reverte a transação em caso de erro
            return f"Erro ao editar professor: {e}", 400

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('professores'))

    # Buscar informações do professor
    try:
        cursor.execute("SELECT * FROM LucasAntunes_tbprofessores WHERE id = %s", (id,))
        professor = cursor.fetchone()

        if not professor:
            return f"Professor com ID {id} não encontrado", 404

        # Buscar todas as disciplinas disponíveis
        cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
        disciplinas = cursor.fetchall()

        # Buscar disciplinas já associadas ao professor
        cursor.execute("SELECT disciplina_id FROM LucasAntunes_tbprofessores_disciplinas WHERE professor_id = %s", (id,))
        professor_disciplinas = [row['disciplina_id'] for row in cursor.fetchall()]

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'edit_professor.html',
        professor=professor,
        disciplinas=disciplinas,
        professor_disciplinas=professor_disciplinas
    )

@app.route('/professores/delete/<int:id>', methods=['POST'])
def delete_professor(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor()
    try:
        # Removendo associações na tabela professores_disciplinas
        cursor.execute("DELETE FROM LucasAntunes_tbprofessores_disciplinas WHERE professor_id = %s", (id,))
        # Excluindo o professor
        cursor.execute("DELETE FROM LucasAntunes_tbprofessores WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        return f"Erro ao excluir: {e}", 400
    finally:
        cursor.close()
        conn.close()
    return redirect('/professores')

# Cadastro de Alunos
@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'POST':
            # Dados do formulário
            nome = request.form['nome']
            cpf = request.form['cpf']
            endereco = request.form['endereco']
            senha = request.form['senha']
            curso_id = request.form['curso_id']

            # Inserir o aluno no banco de dados
            cursor.execute(
                "INSERT INTO LucasAntunes_tbalunos (nome, cpf, endereco, senha, curso_id) VALUES (%s, %s, %s, %s, %s)",
                (nome, cpf, endereco, senha, curso_id)
            )
            conn.commit()  # Confirmar a transação

            return redirect(url_for('alunos'))

        # Lógica de busca
        search = request.args.get('search', '')
        if search:
            cursor.execute("""
                SELECT a.id, a.nome, a.cpf, a.endereco, c.nome AS curso_nome
                FROM LucasAntunes_tbalunos AS a
                LEFT JOIN LucasAntunes_tbcursos AS c ON a.curso_id = c.id
                WHERE a.nome LIKE %s OR a.cpf LIKE %s
            """, (f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""
                SELECT a.id, a.nome, a.cpf, a.endereco, c.nome AS curso_nome
                FROM LucasAntunes_tbalunos AS a
                LEFT JOIN LucasAntunes_tbcursos AS c ON a.curso_id = c.id
            """)
        alunos = cursor.fetchall()

        # Consultar cursos para o formulário
        cursor.execute("SELECT * FROM LucasAntunes_tbcursos")
        cursos = cursor.fetchall()

    except mysql.connector.Error as e:
        conn.rollback()  # Reverter transação em caso de erro
        return f"Erro ao acessar alunos: {e}", 400
    finally:
        cursor.close()  # Fecha o cursor
        conn.close()  # Fecha a conexão

    return render_template('alunos.html', alunos=alunos, cursos=cursos, search=search)

@app.route('/alunos/edit/<int:id>', methods=['GET', 'POST'])
def edit_aluno(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Obtendo dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        curso_id = request.form['curso_id']

        # Atualizando o registro no banco de dados
        cursor.execute("""
            UPDATE LucasAntunes_tbalunos 
            SET nome = %s, cpf = %s, endereco = %s, senha = %s, curso_id = %s 
            WHERE id = %s
        """, (nome, cpf, endereco, senha, curso_id, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('alunos'))

    # Consultando dados do aluno para edição
    cursor.execute("SELECT * FROM LucasAntunes_tbalunos WHERE id = %s", (id,))
    aluno = cursor.fetchone()

    # Consultando lista de cursos para o dropdown
    cursor.execute("SELECT * FROM LucasAntunes_tbcursos")
    cursos = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('edit_aluno.html', aluno=aluno, cursos=cursos)

@app.route('/alunos/delete/<int:id>', methods=['POST'])
def delete_aluno(id):
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM LucasAntunes_tbalunos WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        return f"Erro ao excluir: {e}", 400
    finally:
        cursor.close()
        conn.close()
    return redirect('/alunos')


if __name__ == '__main__':
    app.run(debug=True)