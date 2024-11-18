from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuração do banco de dados
db_config = {
    'host': '201.23.3.86',
    'user': 'usr_aluno',
    'password': 'E$tud@_m@1$',
    'database': 'aula_fatec'
}

# Conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Rotas principais
@app.route('/')
def index():
    return render_template('index.html')

# Cadastro de disciplinas
@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        carga_horaria = request.form['carga_horaria']
        cursor.execute("INSERT INTO LucasAntunes_tbdisciplinas (nome, carga_horaria) VALUES (%s, %s)", (nome, carga_horaria))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('disciplinas'))

    cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
    disciplinas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('disciplinas.html', disciplinas=disciplinas)

# Cadastro de cursos
@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        disciplinas = request.form.getlist('disciplinas')
        
        # Inserindo o curso
        cursor.execute("INSERT INTO LucasAntunes_tbcursos (nome) VALUES (%s)", (nome,))
        curso_id = cursor.lastrowid

        # Associando disciplinas ao curso
        for disciplina_id in disciplinas:
            cursor.execute("INSERT INTO LucasAntunes_tbcursos_disciplinas (curso_id, disciplina_id) VALUES (%s, %s)", (curso_id, disciplina_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('cursos'))

    # Recuperando dados
    cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
    disciplinas = cursor.fetchall()

    cursor.execute("""
        SELECT cursos.id, cursos.nome, GROUP_CONCAT(disciplinas.nome SEPARATOR ', ') AS disciplinas
        FROM LucasAntunes_tbcursos AS cursos
        LEFT JOIN LucasAntunes_tbcursos_disciplinas AS cd ON cursos.id = cd.curso_id
        LEFT JOIN LucasAntunes_tbdisciplinas AS disciplinas ON cd.disciplina_id = disciplinas.id
        GROUP BY cursos.id
    """)
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('cursos.html', cursos=cursos, disciplinas=disciplinas)

# Cadastro de professores
@app.route('/professores', methods=['GET', 'POST'])
def professores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        usuario = request.form['usuario']
        senha = request.form['senha']
        disciplinas = request.form.getlist('disciplinas')

        cursor.execute("INSERT INTO LucasAntunes_tbprofessores (nome, telefone, usuario, senha) VALUES (%s, %s, %s, %s)", 
                       (nome, telefone, usuario, senha))
        professor_id = cursor.lastrowid

        for disciplina_id in disciplinas:
            cursor.execute("INSERT INTO LucasAntunes_tbprofessores_disciplinas (professor_id, disciplina_id) VALUES (%s, %s)", 
                           (professor_id, disciplina_id))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('professores'))

    cursor.execute("SELECT * FROM LucasAntunes_tbdisciplinas")
    disciplinas = cursor.fetchall()

    cursor.execute("""
        SELECT professores.id, professores.nome, professores.telefone, GROUP_CONCAT(disciplinas.nome SEPARATOR ', ') AS disciplinas
        FROM LucasAntunes_tbprofessores AS professores
        LEFT JOIN LucasAntunes_tbprofessores_disciplinas AS pd ON professores.id = pd.professor_id
        LEFT JOIN LucasAntunes_tbdisciplinas AS disciplinas ON pd.disciplina_id = disciplinas.id
        GROUP BY professores.id
    """)
    professores = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('professores.html', professores=professores, disciplinas=disciplinas)

# Cadastro de alunos
@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        senha = request.form['senha']
        curso_id = request.form['curso']

        cursor.execute("INSERT INTO LucasAntunes_tbalunos (nome, cpf, endereco, senha, curso_id) VALUES (%s, %s, %s, %s, %s)", 
                       (nome, cpf, endereco, senha, curso_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('alunos'))

    cursor.execute("SELECT * FROM LucasAntunes_tbcursos")
    cursos = cursor.fetchall()

    cursor.execute("""
        SELECT alunos.id, alunos.nome, alunos.cpf, alunos.endereco, cursos.nome AS curso
        FROM LucasAntunes_tbalunos AS alunos
        LEFT JOIN LucasAntunes_tbcursos AS cursos ON alunos.curso_id = cursos.id
    """)
    alunos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('alunos.html', alunos=alunos, cursos=cursos)

if __name__ == '__main__':
    app.run(debug=True)
