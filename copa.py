from abc import ABC, abstractmethod

class Jogador(ABC):
    def __init__(self, nome, idade, nacionalidade):
        self.nome = nome
        self.idade = idade
        self.nacionalidade = nacionalidade

    @abstractmethod
    def calcular_overall(self):
        pass


class Atacante(Jogador):
    def __init__(self, nome, idade, nacionalidade, velocidade, chute, passe, drible, defesa, fisico):
        super().__init__(nome, idade, nacionalidade)
        self.velocidade = velocidade
        self.chute = chute
        self.passe = passe
        self.drible = drible
        self.defesa = defesa
        self.fisico = fisico

    @abstractmethod
    def calcular_overall(self):
        pass

class Goleiro(Jogador):
    def __init__(self, nome, idade, nacionalidade, elasticidade, manejo, chute, reflexo, posicionamento, velocidade):
        super().__init__(nome,idade,nacionalidade)
        self.elasticidade = elasticidade
        self.manejo = manejo
        self.chute = chute
        self.reflexo = reflexo
        self.posicionamento = posicionamento
        self.velocidade = velocidade
    
    @abstractmethod
    def calcular_overall(self):
        pass