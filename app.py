from flask import Flask, jsonify, request, render_template
import os
from copa import JogadorFactory

app = Flask(__name__)

_jogadores = JogadorFactory.carregar_json(
    os.path.join(os.path.dirname(__file__), 'jogadores.json')
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/jogadores')
def get_jogadores():
    return jsonify([j.to_dict() for j in _jogadores])


@app.route('/api/time/calcular', methods=['POST'])
def calcular_time():
    nomes = request.json.get('jogadores', [])
    selecionados = [j for j in _jogadores if j.nome in nomes]
    if not selecionados:
        return jsonify({'overall': 0, 'total': 0})
    overall = round(sum(j.calcular_overall() for j in selecionados) / len(selecionados))
    return jsonify({'overall': overall, 'total': len(selecionados)})


if __name__ == '__main__':
    app.run(debug=True)
