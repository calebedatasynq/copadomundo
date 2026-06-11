from flask import Flask, jsonify, request, render_template
from database import buscar_jogadores
from copa import montar_selecao_automatica

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/jogadores')
def get_jogadores():
    return jsonify([j.to_dict() for j in buscar_jogadores()])


@app.route('/api/time/calcular', methods=['POST'])
def calcular_time():
    nomes = request.json.get('jogadores', [])
    selecionados = [j for j in buscar_jogadores() if j.nome in nomes]
    if not selecionados:
        return jsonify({'overall': 0, 'total': 0})
    overall = round(sum(j.calcular_overall() for j in selecionados) / len(selecionados))
    return jsonify({'overall': overall, 'total': len(selecionados)})


@app.route('/api/time/automatico')
def time_automatico():
    time = montar_selecao_automatica(buscar_jogadores())
    return jsonify({
        'overall': time.calcular_pontos(),
        'total': len(time),
        'jogadores': [j.to_dict() for j in time.jogadores]
    })


if __name__ == '__main__':
    app.run(debug=True)
