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

# Rota Principal
@app.route('/')
def index():
    # Renderiza a página base com links para os cadastros
    return render_template('index.html')

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
    cursor.execute("DELETE FROM LucasAntunes_tbdisciplinas WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('disciplinas'))


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

    # Inserir novo curso
    if request.method == 'POST':
        nome = request.form['nome']
        cursor.execute("INSERT INTO LucasAntunes_tbcursos (nome) VALUES (%s)", (nome,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('cursos'))

    # Buscar cursos e disciplinas
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

    cursor.close()
    conn.close()
    return render_template('cursos.html', cursos=cursos)



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
        cursor.close()
        conn.close()
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
    cursor.execute("DELETE FROM LucasAntunes_tbcursos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('cursos'))


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

    # Inserir novo professor
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        cursor.execute(
            "INSERT INTO LucasAntunes_tbprofessores (nome, telefone, usuario, senha) VALUES (%s, %s, %s, %s)",
            (nome, telefone, usuario, senha)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('professores'))

    # Buscar professores
    search = request.args.get('search', '')
    if search:
        cursor.execute("SELECT * FROM LucasAntunes_tbprofessores WHERE nome LIKE %s", (f"%{search}%",))
    else:
        cursor.execute("SELECT * FROM LucasAntunes_tbprofessores")
    professores = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('professores.html', professores=professores, search=search)


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
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        cursor.execute(
            "UPDATE LucasAntunes_tbprofessores SET nome = %s, telefone = %s, usuario = %s, senha = %s WHERE id = %s",
            (nome, telefone, usuario, senha, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('professores'))

    cursor.execute("SELECT * FROM LucasAntunes_tbprofessores WHERE id = %s", (id,))
    professor = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_professor.html', professor=professor)


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
    cursor.execute("DELETE FROM LucasAntunes_tbprofessores WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('professores'))


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

    # Inserir novo aluno
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        curso_id = request.form['curso_id']
        cursor.execute(
            "INSERT INTO LucasAntunes_tbalunos (nome, cpf, endereco, senha, curso_id) VALUES (%s, %s, %s, %s, %s)",
            (nome, cpf, endereco, senha, curso_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('alunos'))

    # Buscar alunos
    search = request.args.get('search', '')
    if search:
        cursor.execute("""
            SELECT a.id, a.nome, a.cpf, a.endereco, c.nome AS curso_nome
            FROM LucasAntunes_tbalunos AS a
            LEFT JOIN LucasAntunes_tbcursos AS c ON a.curso_id = c.id
            WHERE a.nome LIKE %s
        """, (f"%{search}%",))
    else:
        cursor.execute("""
            SELECT a.id, a.nome, a.cpf, a.endereco, c.nome AS curso_nome
            FROM LucasAntunes_tbalunos AS a
            LEFT JOIN LucasAntunes_tbcursos AS c ON a.curso_id = c.id
        """)
    alunos = cursor.fetchall()

    # Consultar lista de cursos para o formulário
    cursor.execute("SELECT * FROM LucasAntunes_tbcursos")
    cursos = cursor.fetchall()

    cursor.close()
    conn.close()
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


if __name__ == '__main__':
    app.run(debug=True)
