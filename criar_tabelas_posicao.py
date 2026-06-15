import mysql.connector

MYSQL = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Zen@2425',
    'database': 'copa_card_manager',
}

TABELAS = {
    'atacante': ['velocidade', 'chute', 'passe', 'drible', 'defesa', 'fisico'],
    'goleiro':  ['elasticidade', 'manejo', 'chute', 'reflexo', 'posicionamento', 'velocidade'],
    'zagueiro': ['marcacao', 'forca', 'cabeceio', 'velocidade', 'passe'],
    'lateral':  ['velocidade', 'cruzamento', 'marcacao'],
    'meiocampo':['passe', 'visao', 'resistencia'],
}

CLASSE_TABELA = {
    'Atacante':   'atacante',
    'Goleiro':    'goleiro',
    'Zagueiro':   'zagueiro',
    'Lateral':    'lateral',
    'Meiocampo':  'meiocampo',
}


def criar_tabelas(cur):
    for nome, colunas in TABELAS.items():
        cols_sql = '\n'.join([f"    {c:15s} INT NOT NULL," for c in colunas])
        sql = f"""
            CREATE TABLE IF NOT EXISTS `{nome}` (
                jogador_id  VARCHAR(20) PRIMARY KEY,
                {cols_sql}
                overall     INT NOT NULL,
                FOREIGN KEY (jogador_id) REFERENCES jogador(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cur.execute(sql)
        print(f"Tabela '{nome}' criada ({', '.join(colunas)}, overall).")


def popular_tabelas(cur):
    cur.execute("""
        SELECT id, posicao_classe, velocidade, chute, passe, drible, defesa, fisico,
               elasticidade, manejo, reflexo, posicionamento,
               marcacao, forca, cabeceio, cruzamento, visao, resistencia, overall
        FROM jogador
        WHERE posicao_classe IS NOT NULL
    """)
    jogadores = cur.fetchall()

    lotes = {nome: [] for nome in TABELAS}

    for j in jogadores:
        (jid, classe, velocidade, chute, passe, drible, defesa, fisico,
         elasticidade, manejo, reflexo, posicionamento,
         marcacao, forca, cabeceio, cruzamento, visao, resistencia, overall) = j

        tabela = CLASSE_TABELA.get(classe)
        if not tabela:
            continue

        if tabela == 'atacante':
            lotes['atacante'].append((jid, velocidade, chute, passe, drible, defesa, fisico, overall))
        elif tabela == 'goleiro':
            lotes['goleiro'].append((jid, elasticidade, manejo, chute, reflexo, posicionamento, velocidade, overall))
        elif tabela == 'zagueiro':
            lotes['zagueiro'].append((jid, marcacao, forca, cabeceio, velocidade, passe, overall))
        elif tabela == 'lateral':
            lotes['lateral'].append((jid, velocidade, cruzamento, marcacao, overall))
        elif tabela == 'meiocampo':
            lotes['meiocampo'].append((jid, passe, visao, resistencia, overall))

    sqls = {
        'atacante':  "INSERT INTO atacante  (jogador_id, velocidade, chute, passe, drible, defesa, fisico, overall) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        'goleiro':   "INSERT INTO goleiro   (jogador_id, elasticidade, manejo, chute, reflexo, posicionamento, velocidade, overall) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        'zagueiro':  "INSERT INTO zagueiro  (jogador_id, marcacao, forca, cabeceio, velocidade, passe, overall) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        'lateral':   "INSERT INTO `lateral`  (jogador_id, velocidade, cruzamento, marcacao, overall) VALUES (%s,%s,%s,%s,%s)",
        'meiocampo': "INSERT INTO meiocampo (jogador_id, passe, visao, resistencia, overall) VALUES (%s,%s,%s,%s,%s)",
    }

    for nome, rows in lotes.items():
        if rows:
            cur.executemany(sqls[nome], rows)
            print(f"  {len(rows):>4} registros inseridos em '{nome}'.")


def main():
    conn = mysql.connector.connect(**MYSQL)
    cur  = conn.cursor()

    print("Criando tabelas de posição...")
    criar_tabelas(cur)
    conn.commit()

    print("\nPopulando com os stats do jogador...")
    popular_tabelas(cur)
    conn.commit()

    # Resumo
    print("\nResumo final:")
    for nome in TABELAS:
        cur.execute(f"SELECT COUNT(*), ROUND(AVG(overall),1), MIN(overall), MAX(overall) FROM `{nome}`")
        total, media, minv, maxv = cur.fetchone()
        print(f"  {nome:<12} | {total:>4} jogadores | overall: média {media}  min {minv}  max {maxv}")

    cur.close()
    conn.close()
    print("\nConcluído!")


if __name__ == "__main__":
    main()
