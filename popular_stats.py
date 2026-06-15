import random
import mysql.connector

random.seed(42)

MYSQL = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Zen@2425',
    'database': 'copa_card_manager',
}

# DF split: ~60% Zagueiro, ~40% Lateral
PROB_LATERAL = 0.40


def r(low, high):
    return random.randint(low, high)


def gerar_stats(posicao_classe: str) -> dict:
    """Gera atributos realistas por posição (mesmos campos das classes copa.py)."""
    if posicao_classe == 'Goleiro':
        return dict(
            elasticidade   = r(65, 92),
            manejo         = r(60, 90),
            chute          = r(40, 72),
            reflexo        = r(68, 95),
            posicionamento = r(65, 93),
            velocidade     = r(48, 78),
            # restantes zerados
            passe=0, drible=0, defesa=0, fisico=0,
            marcacao=0, forca=0, cabeceio=0, cruzamento=0, visao=0, resistencia=0,
        )
    if posicao_classe == 'Atacante':
        return dict(
            velocidade = r(65, 97),
            chute      = r(65, 95),
            passe      = r(55, 85),
            drible     = r(60, 95),
            defesa     = r(18, 55),
            fisico     = r(55, 85),
            # restantes zerados
            elasticidade=0, manejo=0, reflexo=0, posicionamento=0,
            marcacao=0, forca=0, cabeceio=0, cruzamento=0, visao=0, resistencia=0,
        )
    if posicao_classe == 'Zagueiro':
        return dict(
            marcacao   = r(65, 92),
            forca      = r(65, 90),
            cabeceio   = r(60, 90),
            velocidade = r(52, 82),
            passe      = r(48, 82),
            # restantes zerados
            chute=0, drible=0, defesa=0, fisico=0,
            elasticidade=0, manejo=0, reflexo=0, posicionamento=0,
            cruzamento=0, visao=0, resistencia=0,
        )
    if posicao_classe == 'Lateral':
        return dict(
            velocidade = r(65, 92),
            cruzamento = r(60, 90),
            marcacao   = r(55, 88),
            # restantes zerados
            chute=0, passe=0, drible=0, defesa=0, fisico=0,
            elasticidade=0, manejo=0, reflexo=0, posicionamento=0,
            forca=0, cabeceio=0, visao=0, resistencia=0,
        )
    # Meiocampo
    return dict(
        passe      = r(65, 93),
        visao      = r(60, 92),
        resistencia= r(63, 90),
        # restantes zerados
        velocidade=0, chute=0, drible=0, defesa=0, fisico=0,
        elasticidade=0, manejo=0, reflexo=0, posicionamento=0,
        marcacao=0, forca=0, cabeceio=0, cruzamento=0,
    )


def calcular_overall(posicao_classe: str, s: dict) -> int:
    """Mesmas fórmulas das classes de copa.py."""
    if posicao_classe == 'Goleiro':
        return round(s['reflexo'] * 0.35 + s['posicionamento'] * 0.30
                     + s['elasticidade'] * 0.20 + s['manejo'] * 0.15)
    if posicao_classe == 'Atacante':
        return round(s['chute'] * 0.35 + s['velocidade'] * 0.25
                     + s['drible'] * 0.25 + s['passe'] * 0.15)
    if posicao_classe == 'Zagueiro':
        return round(s['marcacao'] * 0.35 + s['forca'] * 0.30
                     + s['cabeceio'] * 0.25 + s['velocidade'] * 0.10)
    if posicao_classe == 'Lateral':
        return round(s['velocidade'] * 0.35 + s['cruzamento'] * 0.35
                     + s['marcacao'] * 0.30)
    # Meiocampo
    return round(s['passe'] * 0.40 + s['visao'] * 0.35 + s['resistencia'] * 0.25)


def mapear_posicao(posicao_fifa: str) -> str:
    if posicao_fifa == 'GK':
        return 'Goleiro'
    if posicao_fifa == 'FW':
        return 'Atacante'
    if posicao_fifa == 'MF':
        return 'Meiocampo'
    # DF → Zagueiro ou Lateral
    return 'Lateral' if random.random() < PROB_LATERAL else 'Zagueiro'


TODAS_COLUNAS = [
    'velocidade', 'chute', 'passe', 'drible', 'defesa', 'fisico',
    'elasticidade', 'manejo', 'reflexo', 'posicionamento',
    'marcacao', 'forca', 'cabeceio', 'cruzamento', 'visao', 'resistencia',
]


def adicionar_colunas(cur):
    cur.execute("SHOW COLUMNS FROM jogador")
    existentes = {r['Field'] for r in cur.fetchall()}

    novas = [c for c in TODAS_COLUNAS + ['posicao_classe', 'overall'] if c not in existentes]
    for col in novas:
        tipo = 'VARCHAR(20)' if col == 'posicao_classe' else 'INT DEFAULT 0'
        cur.execute(f"ALTER TABLE jogador ADD COLUMN {col} {tipo}")
    if novas:
        print(f"Colunas adicionadas: {novas}")
    else:
        print("Todas as colunas já existem.")


def main():
    conn = mysql.connector.connect(**MYSQL)
    cur  = conn.cursor(dictionary=True)

    adicionar_colunas(cur)
    conn.commit()

    cur.execute("SELECT id, posicao FROM jogador")
    jogadores = cur.fetchall()
    print(f"Populando stats de {len(jogadores)} jogadores...")

    set_cols = ', '.join([f"{c} = %s" for c in TODAS_COLUNAS + ['posicao_classe', 'overall']])
    sql = f"UPDATE jogador SET {set_cols} WHERE id = %s"

    batch = []
    for j in jogadores:
        classe = mapear_posicao(j['posicao'])
        stats  = gerar_stats(classe)
        overall = calcular_overall(classe, stats)
        valores = [stats[c] for c in TODAS_COLUNAS] + [classe, overall, j['id']]
        batch.append(valores)

    cur.executemany(sql, batch)
    conn.commit()

    # Resumo por posição
    cur.execute("""
        SELECT posicao_classe,
               COUNT(*) AS total,
               ROUND(AVG(overall), 1) AS media_overall,
               MIN(overall) AS min_ov,
               MAX(overall) AS max_ov
        FROM jogador
        GROUP BY posicao_classe
        ORDER BY posicao_classe
    """)
    print(f"\n{'Posição':<12} {'Total':>6} {'Média':>7} {'Mín':>5} {'Máx':>5}")
    print("-" * 40)
    for r in cur.fetchall():
        print(f"{r['posicao_classe']:<12} {r['total']:>6} {r['media_overall']:>7} {r['min_ov']:>5} {r['max_ov']:>5}")

    cur.close()
    conn.close()
    print("\nConcluído!")


if __name__ == "__main__":
    main()
