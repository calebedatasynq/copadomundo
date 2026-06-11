import mysql.connector
from copa import JogadorFactory, Jogador

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Zen@2425',
    'database': 'copa_card_manager'
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def buscar_jogadores() -> list[Jogador]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jogadores ORDER BY nome")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [JogadorFactory.criar(row) for row in rows]
