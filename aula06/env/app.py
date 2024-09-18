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
    return imc  

app.run()    