from abc import ABC, abstractmethod
import json


class Jogador(ABC):
    def __init__(self, nome, idade, nacionalidade):
        self._nome = nome
        self._idade = idade
        self._nacionalidade = nacionalidade

    @property
    def nome(self):
        return self._nome

    @property
    def idade(self):
        return self._idade

    @property
    def nacionalidade(self):
        return self._nacionalidade

    @abstractmethod
    def calcular_overall(self):
        pass

    def to_dict(self):
        result = {
            'nome': self.nome,
            'idade': self.idade,
            'nacionalidade': self.nacionalidade,
            'posicao': type(self).__name__,
            'overall': self.calcular_overall()
        }
        result.update({k: v for k, v in vars(self).items() if not k.startswith('_')})
        return result

    def __str__(self):
        return f"{self.nome} ({type(self).__name__}) | Overall: {self.calcular_overall()}"


class Atacante(Jogador):
    def __init__(self, nome, idade, nacionalidade, velocidade, chute, passe, drible, defesa, fisico):
        super().__init__(nome, idade, nacionalidade)
        self.velocidade = velocidade
        self.chute = chute
        self.passe = passe
        self.drible = drible
        self.defesa = defesa
        self.fisico = fisico

    def calcular_overall(self):
        return round(self.chute * 0.35 + self.velocidade * 0.25 + self.drible * 0.25 + self.passe * 0.15)


class Goleiro(Jogador):
    def __init__(self, nome, idade, nacionalidade, elasticidade, manejo, chute, reflexo, posicionamento, velocidade):
        super().__init__(nome, idade, nacionalidade)
        self.elasticidade = elasticidade
        self.manejo = manejo
        self.chute = chute
        self.reflexo = reflexo
        self.posicionamento = posicionamento
        self.velocidade = velocidade

    def calcular_overall(self):
        return round(self.reflexo * 0.35 + self.posicionamento * 0.30 + self.elasticidade * 0.20 + self.manejo * 0.15)


class Zagueiro(Jogador):
    def __init__(self, nome, idade, nacionalidade, marcacao, forca, cabeceio, velocidade, passe):
        super().__init__(nome, idade, nacionalidade)
        self.marcacao = marcacao
        self.forca = forca
        self.cabeceio = cabeceio
        self.velocidade = velocidade
        self.passe = passe

    def calcular_overall(self):
        return round(self.marcacao * 0.35 + self.forca * 0.30 + self.cabeceio * 0.25 + self.velocidade * 0.10)


class Lateral(Jogador):
    def __init__(self, nome, idade, nacionalidade, velocidade, cruzamento, marcacao):
        super().__init__(nome, idade, nacionalidade)
        self.velocidade = velocidade
        self.cruzamento = cruzamento
        self.marcacao = marcacao

    def calcular_overall(self):
        return round(self.velocidade * 0.35 + self.cruzamento * 0.35 + self.marcacao * 0.30)


class Meiocampo(Jogador):
    def __init__(self, nome, idade, nacionalidade, passe, visao, resistencia):
        super().__init__(nome, idade, nacionalidade)
        self.passe = passe
        self.visao = visao
        self.resistencia = resistencia

    def calcular_overall(self):
        return round(self.passe * 0.40 + self.visao * 0.35 + self.resistencia * 0.25)


class Time:
    MAX_JOGADORES = 11

    def __init__(self, nome="Meu Time"):
        self._nome = nome
        self._jogadores: list[Jogador] = []

    @property
    def nome(self):
        return self._nome

    @property
    def jogadores(self):
        return list(self._jogadores)

    def adicionar(self, jogador: Jogador):
        if len(self._jogadores) >= self.MAX_JOGADORES:
            raise ValueError("Time já tem 11 jogadores")
        self._jogadores.append(jogador)

    def remover(self, nome: str):
        self._jogadores = [j for j in self._jogadores if j.nome != nome]

    def calcular_pontos(self) -> int:
        if not self._jogadores:
            return 0
        return round(sum(j.calcular_overall() for j in self._jogadores) / len(self._jogadores))

    def __len__(self):
        return len(self._jogadores)

    def __str__(self):
        return f"Time: {self.nome} | {len(self)} jogadores | Overall: {self.calcular_pontos()}"


class JogadorFactory:
    _mapa = {
        'Atacante':  (Atacante,  ['velocidade', 'chute', 'passe', 'drible', 'defesa', 'fisico']),
        'Goleiro':   (Goleiro,   ['elasticidade', 'manejo', 'chute', 'reflexo', 'posicionamento', 'velocidade']),
        'Zagueiro':  (Zagueiro,  ['marcacao', 'forca', 'cabeceio', 'velocidade', 'passe']),
        'Lateral':   (Lateral,   ['velocidade', 'cruzamento', 'marcacao']),
        'Meiocampo': (Meiocampo, ['passe', 'visao', 'resistencia']),
    }

    @classmethod
    def criar(cls, dados: dict) -> Jogador:
        posicao = dados['posicao']
        if posicao not in cls._mapa:
            raise ValueError(f"Posição desconhecida: {posicao}")
        klass, campos = cls._mapa[posicao]
        return klass(
            dados['nome'], dados['idade'], dados['nacionalidade'],
            *[dados[c] for c in campos]
        )

    @classmethod
    def carregar_json(cls, caminho: str) -> list[Jogador]:
        with open(caminho, encoding='utf-8') as f:
            return [cls.criar(d) for d in json.load(f)]
