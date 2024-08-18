from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Olá, mundo!'

@app.route('/rota2')
def NomeDaFuncao():
    return 'Outro texto'

app.run()