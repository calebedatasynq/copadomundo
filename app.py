from flask import Flask, jsonify, request, render_template
from database import (
    buscar_jogadores, buscar_selecoes, buscar_ranking_selecoes,
    buscar_por_nome, buscar_stats_jogador, buscar_comparar_selecoes,
)
from copa import montar_selecao_automatica

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/jogadores')
def get_jogadores():
    posicao = request.args.get('posicao')
    selecao = request.args.get('selecao')
    jogadores = buscar_jogadores(selecao=selecao, posicao=posicao)
    return jsonify([j.to_dict() for j in jogadores])


@app.route('/api/jogadores/buscar')
def buscar_jogadores_nome():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    return jsonify(buscar_por_nome(q))


@app.route('/api/selecoes')
def get_selecoes():
    return jsonify(buscar_selecoes())


@app.route('/api/selecoes/ranking')
def ranking_selecoes():
    return jsonify(buscar_ranking_selecoes())


@app.route('/api/selecoes/comparar')
def comparar_selecoes():
    a = request.args.get('a', '')
    b = request.args.get('b', '')
    if not a or not b:
        return jsonify({'erro': 'Informe dois times: ?a=Brazil&b=France'}), 400
    return jsonify(buscar_comparar_selecoes(a, b))


@app.route('/api/comparar/jogadores')
def comparar_jogadores():
    a = request.args.get('a', '')
    b = request.args.get('b', '')
    if not a or not b:
        return jsonify({'erro': 'Informe dois IDs: ?a=Q123&b=Q456'}), 400
    stats_a = buscar_stats_jogador(a)
    stats_b = buscar_stats_jogador(b)
    if not stats_a or not stats_b:
        return jsonify({'erro': 'Jogador não encontrado'}), 404
    return jsonify({'a': stats_a, 'b': stats_b})


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
    selecao = request.args.get('selecao')
    jogadores = buscar_jogadores(selecao=selecao)
    time = montar_selecao_automatica(jogadores)
    return jsonify({
        'overall':   time.calcular_pontos(),
        'total':     len(time),
        'jogadores': [j.to_dict() for j in time.jogadores],
    })


if __name__ == '__main__':
    app.run(debug=True)
