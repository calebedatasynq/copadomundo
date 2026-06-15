import mysql.connector
from copa import JogadorFactory, Jogador

DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Zen@2425',
    'database': 'copa_card_manager',
}

# Cada query faz JOIN entre jogador e sua tabela de posição,
# retornando exatamente os campos que JogadorFactory.criar() espera.
_SQL = {
    'Atacante': """
        SELECT j.id, j.nome, j.selecao AS nacionalidade,
               'Atacante' AS posicao, 0 AS idade,
               a.velocidade, a.chute, a.passe, a.drible, a.defesa, a.fisico, a.overall
        FROM jogador j
        JOIN atacante a ON j.id = a.jogador_id
    """,
    'Goleiro': """
        SELECT j.id, j.nome, j.selecao AS nacionalidade,
               'Goleiro' AS posicao, 0 AS idade,
               g.elasticidade, g.manejo, g.chute, g.reflexo, g.posicionamento, g.velocidade, g.overall
        FROM jogador j
        JOIN goleiro g ON j.id = g.jogador_id
    """,
    'Zagueiro': """
        SELECT j.id, j.nome, j.selecao AS nacionalidade,
               'Zagueiro' AS posicao, 0 AS idade,
               z.marcacao, z.forca, z.cabeceio, z.velocidade, z.passe, z.overall
        FROM jogador j
        JOIN zagueiro z ON j.id = z.jogador_id
    """,
    'Lateral': """
        SELECT j.id, j.nome, j.selecao AS nacionalidade,
               'Lateral' AS posicao, 0 AS idade,
               l.velocidade, l.cruzamento, l.marcacao, l.overall
        FROM jogador j
        JOIN `lateral` l ON j.id = l.jogador_id
    """,
    'Meiocampo': """
        SELECT j.id, j.nome, j.selecao AS nacionalidade,
               'Meiocampo' AS posicao, 0 AS idade,
               m.passe, m.visao, m.resistencia, m.overall
        FROM jogador j
        JOIN meiocampo m ON j.id = m.jogador_id
    """,
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def _query(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def buscar_jogadores(selecao: str = None, posicao: str = None) -> list[Jogador]:
    """Retorna objetos Jogador com filtros opcionais por seleção e/ou posição."""
    posicoes = [posicao] if posicao else list(_SQL.keys())
    resultado = []
    for pos in posicoes:
        sql = _SQL[pos]
        if selecao:
            sql += " WHERE j.selecao = %s"
            rows = _query(sql, (selecao,))
        else:
            rows = _query(sql)
        resultado.extend(JogadorFactory.criar(r) for r in rows)
    return resultado


def buscar_selecoes() -> list[str]:
    """Retorna os nomes de todas as 48 seleções."""
    return [r['nome'] for r in _query("SELECT nome FROM selecao ORDER BY nome")]


def buscar_ranking_selecoes() -> list[dict]:
    return _query("""
        SELECT selecao, COUNT(*) AS jogadores,
               ROUND(AVG(overall), 1) AS overall_medio,
               MAX(overall) AS melhor_overall
        FROM jogador
        GROUP BY selecao
        ORDER BY overall_medio DESC
    """)


def buscar_por_nome(q: str) -> list[dict]:
    return _query("""
        SELECT id, nome, posicao_classe AS posicao, selecao, overall
        FROM jogador
        WHERE nome LIKE %s
        ORDER BY overall DESC
        LIMIT 10
    """, (f'%{q}%',))


def buscar_stats_jogador(jogador_id: str) -> dict | None:
    rows = _query("""
        SELECT j.id, j.nome, j.selecao AS nacionalidade,
               j.posicao_classe AS posicao, j.overall,
               COALESCE(a.velocidade, g.velocidade, z.velocidade, l.velocidade, 0) AS velocidade,
               COALESCE(a.chute,      g.chute,      0)                             AS chute,
               COALESCE(a.passe,      z.passe,      m.passe,   0)                 AS passe,
               COALESCE(a.drible,     0)                                           AS drible,
               COALESCE(a.defesa,     0)                                           AS defesa,
               COALESCE(a.fisico,     0)                                           AS fisico,
               COALESCE(g.elasticidade,   0)                                       AS elasticidade,
               COALESCE(g.manejo,         0)                                       AS manejo,
               COALESCE(g.reflexo,        0)                                       AS reflexo,
               COALESCE(g.posicionamento, 0)                                       AS posicionamento,
               COALESCE(z.marcacao, l.marcacao, 0)                                 AS marcacao,
               COALESCE(z.forca,    0)                                             AS forca,
               COALESCE(z.cabeceio, 0)                                             AS cabeceio,
               COALESCE(l.cruzamento, 0)                                           AS cruzamento,
               COALESCE(m.visao,      0)                                           AS visao,
               COALESCE(m.resistencia,0)                                           AS resistencia
        FROM jogador j
        LEFT JOIN atacante  a ON j.id = a.jogador_id
        LEFT JOIN goleiro   g ON j.id = g.jogador_id
        LEFT JOIN zagueiro  z ON j.id = z.jogador_id
        LEFT JOIN `lateral` l ON j.id = l.jogador_id
        LEFT JOIN meiocampo m ON j.id = m.jogador_id
        WHERE j.id = %s
    """, (jogador_id,))
    return rows[0] if rows else None


def buscar_comparar_selecoes(sel_a: str, sel_b: str) -> dict:
    rows = _query("""
        SELECT selecao, posicao_classe,
               COUNT(*)                AS total,
               ROUND(AVG(overall), 1)  AS avg_overall,
               MAX(overall)            AS melhor
        FROM jogador
        WHERE selecao IN (%s, %s)
        GROUP BY selecao, posicao_classe
        ORDER BY selecao, posicao_classe
    """, (sel_a, sel_b))

    resultado = {sel_a: {}, sel_b: {}}
    for r in rows:
        resultado[r['selecao']][r['posicao_classe']] = {
            'total': r['total'],
            'avg':   r['avg_overall'],
            'melhor': r['melhor'],
        }

    # overall geral de cada time
    for sel in (sel_a, sel_b):
        totais = _query(
            "SELECT ROUND(AVG(overall),1) AS media FROM jogador WHERE selecao = %s",
            (sel,)
        )
        resultado[sel]['_geral'] = totais[0]['media'] if totais else 0

    return resultado
