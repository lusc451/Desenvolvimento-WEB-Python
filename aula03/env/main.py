from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', uma_variavel_no_html = 'Licas', teste = 'Teste de variável')

@app.route('/pag1')
def pag1():
    return render_template('pag1.html')

@app.route('/pag2')
def pag2():
    return render_template('pag2.html')

app.run(debug=True)