from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('imc.html')

@app.route('/calcular_imc_post', methods=['POST'])
def calcular_imc():
    altura = float(request.form['txt_altura'])
    peso = float(request.form['txt_peso'])
    imc = peso / (altura * altura)
    return render_template('imc.html', result_imc = imc)

@app.route('/calcular_imc_get') #Não informar o método, entende-se que será GET (PADRÃO)
def calcular_imc_get():
    args = request.args
    altura = float(args.get('txt_altura'))
    peso = float(args.get('txt_peso'))
    imc = peso / (altura * altura)
    return render_template('imc.html', result_imc = imc)

app.run()    