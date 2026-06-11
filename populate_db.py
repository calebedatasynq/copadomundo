import mysql.connector
import json
import os

HOST     = 'localhost'
USER     = 'root'
PASSWORD = 'Zen@2425'
DB_NAME  = 'copa_card_manager'

COLUNAS = [
    'nome', 'posicao', 'nacionalidade', 'idade',
    'velocidade', 'chute', 'passe', 'drible', 'defesa', 'fisico',
    'elasticidade', 'manejo', 'reflexo', 'posicionamento',
    'marcacao', 'forca', 'cabeceio', 'cruzamento',
    'visao', 'resistencia'
]


def criar_banco():
    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Banco '{DB_NAME}' pronto.")


def criar_tabela():
    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            nome            VARCHAR(100) NOT NULL,
            posicao         VARCHAR(50)  NOT NULL,
            nacionalidade   VARCHAR(50)  NOT NULL,
            idade           INT          NOT NULL,
            velocidade      INT,
            chute           INT,
            passe           INT,
            drible          INT,
            defesa          INT,
            fisico          INT,
            elasticidade    INT,
            manejo          INT,
            reflexo         INT,
            posicionamento  INT,
            marcacao        INT,
            forca           INT,
            cabeceio        INT,
            cruzamento      INT,
            visao           INT,
            resistencia     INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela 'jogadores' pronta.")


def popular():
    caminho = os.path.join(os.path.dirname(__file__), 'jogadores.json')
    with open(caminho, encoding='utf-8') as f:
        jogadores = json.load(f)

    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM jogadores")

    placeholders = ', '.join(['%s'] * len(COLUNAS))
    sql = f"INSERT INTO jogadores ({', '.join(COLUNAS)}) VALUES ({placeholders})"

    for j in jogadores:
        valores = tuple(j.get(col) for col in COLUNAS)
        cursor.execute(sql, valores)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"{len(jogadores)} jogadores inseridos com sucesso.")


if __name__ == '__main__':
    criar_banco()
    criar_tabela()
    popular()
