from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', uma_variavel_no_html = 'Lucas', i = 0)

@app.route('/teste1')
def pag1():
    return render_template('teste1.html',num1 = 3, num2 = 5)

@app.route('/teste2')
def pag2():
    return render_template('teste2.html', titulo_pag2 = "Olá mundo",  url_imagem = 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png')

app.run(debug=True)