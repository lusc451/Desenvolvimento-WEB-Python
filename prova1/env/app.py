from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calc-triangulo', methods=['GET'])
def calc_triangulo():
    resultado = None
    lado1 = request.args.get('lado1', type=float)
    lado2 = request.args.get('lado2', type=float)
    lado3 = request.args.get('lado3', type=float)

    if lado1 is not None and lado2 is not None and lado3 is not None:
        if lado1 > 0 and lado2 > 0 and lado3 > 0 and (lado1 + lado2 > lado3) and (lado1 + lado3 > lado2) and (lado2 + lado3 > lado1):
            if lado1 == lado2 == lado3:
                resultado = "Equilátero"
            elif lado1 == lado2 or lado1 == lado3 or lado2 == lado3:
                resultado = "Isósceles"
            else:
                resultado = "Escaleno"
        else:
            resultado = "Os valores fornecidos não formam um triângulo válido."

    return render_template('calc-triangulo.html', resultado=resultado)


@app.route('/media-notas', methods=['GET', 'POST'])
def media_notas():
    media = None
    status = None  
    if request.method == 'POST':
        try:

            nota1 = float(request.form['nota1'])
            nota2 = float(request.form['nota2'])
            nota3 = float(request.form['nota3'])
            nota4 = float(request.form['nota4'])

            media = (nota1 + nota2 + nota3 + nota4) / 4
            
            if media >= 6.0:
                status = "aprovado"
            else:
                status = "reprovado"
        except (ValueError, TypeError):
            media = "Por favor, insira valores válidos para as notas."
    
    return render_template('media-notas.html', media=media, status=status)


if __name__ == '__main__':
    app.run(debug=True)
