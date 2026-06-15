import requests
import mysql.connector

API_BASE = "https://worldcup26.ir"
EMAIL    = "calebesoares.alencar@gmail.com"
SENHA    = "Copa2026@Pass"

DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Zen@2425',
    'database': 'copa_card_manager',
}

# Mapeamento: nacionalidade (PT) → código iso2 da API
MAPA_PAIS = {
    "Alemanha":   "DE",
    "Argentina":  "AR",
    "Bélgica":    "BE",
    "Brasil":     "BR",
    "Canadá":     "CA",
    "Colômbia":   "CO",
    "Croácia":    "HR",
    "Egito":      "EG",
    "Equador":    "EC",
    "Espanha":    "ES",
    "França":     "FR",
    "Holanda":    "NL",
    "Inglaterra": "ENG",
    "Japão":      "JP",
    "Marrocos":   "MA",
    "México":     "MX",
    "Nigéria":    None,
    "Noruega":    "NO",
    "Polônia":    None,
    "Portugal":   "PT",
    "Senegal":    "SN",
    "Suíça":      "CH",
    "Suécia":     "SE",
    "Tunísia":    "TN",
    "Ucrânia":    None,
    "Uruguai":    "UY",
    "EUA":        "US",
    "Eslovênia":  None,
}


def autenticar() -> str:
    resp = requests.post(f"{API_BASE}/auth/authenticate",
                         json={"email": EMAIL, "password": SENHA}, timeout=10)
    resp.raise_for_status()
    token = resp.json()["token"]
    print("Autenticado na API.")
    return token


def buscar_times(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_BASE}/get/teams", headers=headers, timeout=10)
    resp.raise_for_status()
    times = resp.json()["teams"]
    print(f"{len(times)} times recebidos da API.")
    return times


def preparar_banco(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS selecoes (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            iso2        VARCHAR(10)  NOT NULL UNIQUE,
            nome_en     VARCHAR(100) NOT NULL,
            codigo_fifa VARCHAR(10),
            grupo       VARCHAR(5),
            bandeira    VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    cur.execute("""
        ALTER TABLE jogadores
        ADD COLUMN IF NOT EXISTS bandeira_url VARCHAR(255)
    """)
    conn.commit()
    cur.close()
    print("Banco preparado (tabela selecoes + coluna bandeira_url).")


def salvar_times(conn, times: list[dict]):
    cur = conn.cursor()
    sql = """
        INSERT INTO selecoes (iso2, nome_en, codigo_fifa, grupo, bandeira)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nome_en     = VALUES(nome_en),
            codigo_fifa = VALUES(codigo_fifa),
            grupo       = VALUES(grupo),
            bandeira    = VALUES(bandeira)
    """
    for t in times:
        cur.execute(sql, (
            t["iso2"],
            t["name_en"],
            t.get("fifa_code"),
            t.get("groups"),
            t.get("flag"),
        ))
    conn.commit()
    cur.close()
    print(f"{len(times)} seleções salvas na tabela 'selecoes'.")


def atualizar_bandeiras_jogadores(conn, times: list[dict]):
    iso2_para_bandeira = {t["iso2"]: t.get("flag") for t in times}
    cur = conn.cursor()
    atualizados = 0
    for nome_pt, iso2 in MAPA_PAIS.items():
        if iso2 and iso2 in iso2_para_bandeira:
            url = iso2_para_bandeira[iso2]
            cur.execute(
                "UPDATE jogadores SET bandeira_url = %s WHERE nacionalidade = %s",
                (url, nome_pt)
            )
            atualizados += cur.rowcount
    conn.commit()
    cur.close()
    print(f"{atualizados} jogadores atualizados com bandeira_url.")


def main():
    token = autenticar()
    times = buscar_times(token)

    conn = mysql.connector.connect(**DB_CONFIG)
    preparar_banco(conn)
    salvar_times(conn, times)
    atualizar_bandeiras_jogadores(conn, times)
    conn.close()

    print("\nConcluído! Resumo dos times buscados:")
    for t in sorted(times, key=lambda x: x["groups"]):
        print(f"  Grupo {t['groups']} | {t['name_en']:30s} | {t['iso2']:4s} | {t.get('flag','')}")


if __name__ == "__main__":
    main()
