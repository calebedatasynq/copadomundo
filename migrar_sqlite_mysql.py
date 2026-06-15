import sqlite3
import mysql.connector

SQLITE_PATH = r'C:\Users\caleb\OneDrive\Documentos\poo22026\copa2026_jogadores.db'

MYSQL = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Zen@2425',
    'database': 'copa_card_manager',
}


def criar_tabelas(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS selecao (
            id   INT          PRIMARY KEY,
            nome VARCHAR(100) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clube (
            id   VARCHAR(20)  PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            pais VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS jogador (
            id             VARCHAR(20)  PRIMARY KEY,
            nome           VARCHAR(200) NOT NULL,
            selecao        VARCHAR(100),
            posicao        VARCHAR(10),
            clube_atual_id VARCHAR(20),
            FOREIGN KEY (clube_atual_id) REFERENCES clube(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS passagem_clube (
            jogador_id VARCHAR(20)  NOT NULL,
            clube_id   VARCHAR(20)  NOT NULL,
            temporada  VARCHAR(20),
            PRIMARY KEY (jogador_id, clube_id, temporada),
            FOREIGN KEY (jogador_id) REFERENCES jogador(id),
            FOREIGN KEY (clube_id)   REFERENCES clube(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("Tabelas criadas no MySQL.")


def migrar(sqlite_cur, mysql_cur, tabela, sql_insert, batchsize=500):
    sqlite_cur.execute(f"SELECT * FROM {tabela}")
    rows = sqlite_cur.fetchall()
    total = 0
    for i in range(0, len(rows), batchsize):
        batch = rows[i:i + batchsize]
        mysql_cur.executemany(sql_insert, batch)
        total += len(batch)
    print(f"  {total} registros inseridos em '{tabela}'.")
    return total


def main():
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cur  = sqlite_conn.cursor()

    mysql_conn = mysql.connector.connect(**MYSQL)
    mysql_cur  = mysql_conn.cursor()

    criar_tabelas(mysql_cur)
    mysql_conn.commit()

    print("\nMigrando dados...")

    mysql_cur.execute("DELETE FROM passagem_clube")
    mysql_cur.execute("DELETE FROM jogador")
    mysql_cur.execute("DELETE FROM clube")
    mysql_cur.execute("DELETE FROM selecao")
    mysql_conn.commit()

    migrar(sqlite_cur, mysql_cur, "selecao",
           "INSERT INTO selecao (id, nome) VALUES (%s, %s)")
    mysql_conn.commit()

    migrar(sqlite_cur, mysql_cur, "clube",
           "INSERT INTO clube (id, nome, pais) VALUES (%s, %s, %s)")
    mysql_conn.commit()

    # Busca IDs de clubes existentes para evitar FK inválida
    mysql_cur.execute("SELECT id FROM clube")
    clubes_validos = {r[0] for r in mysql_cur.fetchall()}

    sqlite_cur.execute("SELECT id, nome, selecao, posicao, clube_atual_id FROM jogador")
    jogadores = []
    for row in sqlite_cur.fetchall():
        jid, nome, selecao, posicao, clube_id = row
        clube_id = clube_id if clube_id in clubes_validos else None
        jogadores.append((jid, nome, selecao, posicao, clube_id))

    mysql_cur.executemany(
        "INSERT INTO jogador (id, nome, selecao, posicao, clube_atual_id) VALUES (%s, %s, %s, %s, %s)",
        jogadores
    )
    print(f"  {len(jogadores)} registros inseridos em 'jogador'.")
    mysql_conn.commit()

    mysql_cur.execute("SELECT id FROM jogador")
    jogadores_validos = {r[0] for r in mysql_cur.fetchall()}

    sqlite_cur.execute("SELECT jogador_id, clube_id, temporada FROM passagem_clube")
    passagens = [
        row for row in sqlite_cur.fetchall()
        if row[0] in jogadores_validos and row[1] in clubes_validos
    ]
    mysql_cur.executemany(
        "INSERT INTO passagem_clube (jogador_id, clube_id, temporada) VALUES (%s, %s, %s)",
        passagens
    )
    print(f"  {len(passagens)} registros inseridos em 'passagem_clube'.")
    mysql_conn.commit()

    sqlite_cur.close()
    sqlite_conn.close()
    mysql_cur.close()
    mysql_conn.close()

    print("\nMigração concluída!")


if __name__ == "__main__":
    main()
