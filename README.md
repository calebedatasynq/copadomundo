# Copa Card Manager ⚽

Aplicação web para gerenciamento de cards de jogadores da **FIFA World Cup 2026**, com montagem de times, ranking de seleções e comparador. Desenvolvido em Python com Flask e MySQL, aplicando conceitos de **Programação Orientada a Objetos**.

---

## Funcionalidades

### 🏟️ Montar Time
- Visualize os **1248 jogadores reais** da Copa 2026 em cards
- Filtre por **posição** (ATK, MEI, LAT, ZAG, GOL)
- Filtre por **país** com busca autocomplete e bandeiras emoji
- Adicione até **11 jogadores** ao seu time manualmente
- Botão **"Montar Melhor Time"** — monta automaticamente o time com maior overall na formação 4-3-3 (aceita filtro de seleção ativo)
- **Overall do time** calculado com animação em anel

### 🌍 Seleções
- **Ranking das 48 seleções** ordenado por overall médio
- Cada card exibe bandeira, nome, overall médio, total de jogadores e top individual
- Selecione **2 seleções** para comparar diretamente com um clique

### ⚖️ Comparar
- **Jogadores:** busca por nome com autocomplete → cards lado a lado com barras de atributos (dourado = vence)
- **Seleções:** dropdowns com as 48 equipes → tabela detalhada por posição (total, média de overall, melhor jogador)

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 + Flask |
| Banco de dados | MySQL (`mysql-connector-python`) |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Dados externos | API [worldcup2026](https://github.com/rezarahiminia/worldcup2026) + SQLite fornecido |
| Sem frameworks JS | Nenhum npm, Node.js ou bundler |

---

## Estrutura do Projeto

```
poo22026/
├── copa.py                   # Modelo de domínio (classes POO)
├── database.py               # Camada de acesso a dados (MySQL)
├── app.py                    # API REST (Flask)
├── populate_db.py            # Popula banco com jogadores do jogadores.json
├── migrar_sqlite_mysql.py    # Migra SQLite → MySQL (1248 jogadores reais)
├── popular_stats.py          # Gera stats mock por posição e calcula overall
├── criar_tabelas_posicao.py  # Cria tabelas separadas por posição
├── buscar_selecoes.py        # Busca times da API Copa 2026
├── copa2026_jogadores.db     # Banco SQLite com dados reais (fonte)
├── copa2026_jogadores.csv    # Exportação CSV dos jogadores
├── jogadores.json            # 28 jogadores de exemplo para testes
├── templates/
│   └── index.html            # Frontend (3 abas)
└── static/
    ├── script.js             # Lógica do frontend
    └── style.css             # Estilos (tema escuro com acentos dourados)
```

---

## Banco de Dados (MySQL)

O banco `copa_card_manager` possui as seguintes tabelas:

| Tabela | Registros | Descrição |
|---|---|---|
| `jogador` | 1.248 | Jogadores reais com nome, seleção, posição e stats |
| `selecao` | 48 | Seleções da Copa 2026 |
| `clube` | 1.569 | Clubes de origem |
| `atacante` | 312 | Stats: velocidade, chute, passe, drible, defesa, fisico |
| `goleiro` | 145 | Stats: elasticidade, manejo, chute, reflexo, posicionamento, velocidade |
| `zagueiro` | 234 | Stats: marcacao, forca, cabeceio, velocidade, passe |
| `lateral` | 187 | Stats: velocidade, cruzamento, marcacao |
| `meiocampo` | 370 | Stats: passe, visao, resistencia |

Cada tabela de posição tem `jogador_id` como chave estrangeira e campo `overall` calculado.

---

## Conceitos de POO Aplicados

| Conceito | Implementação |
|---|---|
| **Herança + ABC** | `Jogador` abstrata → `Atacante`, `Goleiro`, `Zagueiro`, `Lateral`, `Meiocampo` |
| **Polimorfismo** | `calcular_overall()` com fórmula diferente em cada subclasse |
| **Encapsulamento** | Atributos `_privados` + `@property` somente leitura |
| **Abstração** | `@abstractmethod`, `to_dict()`, camada `_query()` |
| **Factory Pattern** | `JogadorFactory.criar(dict)` → instancia a classe correta |
| **Composição** | `Time` contém `list[Jogador]` (relação has-a) |
| **Métodos Mágicos** | `__str__`, `__len__` em `Time` e `Jogador` |
| **Class Method** | `@classmethod` em `JogadorFactory` |

---

## Instalação e Execução

### Pré-requisitos
- Python 3.11+
- MySQL rodando localmente

### 1. Instalar dependências
```bash
pip install flask mysql-connector-python requests
```

### 2. Configurar o banco
Edite as credenciais em `database.py`, `populate_db.py`, `migrar_sqlite_mysql.py` e `popular_stats.py`:
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'SUA_SENHA',
    'database': 'copa_card_manager',
}
```

### 3. Montar o banco completo
Execute os scripts na ordem:
```bash
# Cria o banco e migra os 1248 jogadores reais do SQLite
python migrar_sqlite_mysql.py

# Gera stats por posição e calcula overall de cada jogador
python popular_stats.py

# Cria tabelas separadas por posição (atacante, goleiro, etc.)
python criar_tabelas_posicao.py
```

### 4. Iniciar o servidor
```bash
python app.py
```

Acesse: [http://localhost:5000](http://localhost:5000)

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/jogadores?posicao=&selecao=` | Lista jogadores com filtros opcionais |
| GET | `/api/jogadores/buscar?q=nome` | Busca jogadores por nome (top 10) |
| GET | `/api/selecoes` | Lista as 48 seleções |
| GET | `/api/selecoes/ranking` | Ranking por overall médio |
| GET | `/api/selecoes/comparar?a=Brazil&b=France` | Compara duas seleções por posição |
| GET | `/api/comparar/jogadores?a=id&b=id` | Compara stats de dois jogadores |
| POST | `/api/time/calcular` | Calcula overall de uma lista de nomes |
| GET | `/api/time/automatico?selecao=` | Monta o melhor 11 automaticamente |

---

## Fórmulas de Overall por Posição

```
Atacante:   chute×0.35 + velocidade×0.25 + drible×0.25 + passe×0.15
Goleiro:    reflexo×0.35 + posicionamento×0.30 + elasticidade×0.20 + manejo×0.15
Zagueiro:   marcacao×0.35 + forca×0.30 + cabeceio×0.25 + velocidade×0.10
Lateral:    velocidade×0.35 + cruzamento×0.35 + marcacao×0.30
Meiocampo:  passe×0.40 + visao×0.35 + resistencia×0.25
```

---

## Dados

Os jogadores reais foram extraídos do arquivo `copa2026_jogadores.db` (SQLite) contendo elencos oficiais das 48 seleções classificadas para a Copa do Mundo 2026. Os **atributos individuais** (velocidade, chute, etc.) são **dados simulados** gerados com `popular_stats.py`, distribuídos por faixas realistas de acordo com a posição.
