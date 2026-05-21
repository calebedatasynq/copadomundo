# Copa Card Manager — Descrição do Projeto

## Visão Geral

O **Copa Card Manager** é um sistema de gerenciamento de jogadores da Copa do Mundo desenvolvido em Python com interface gráfica. O sistema permite cadastrar, visualizar e comparar jogadores de diferentes seleções, exibindo seus atributos técnicos em cards visuais inspirados no estilo do FIFA Ultimate Team.

O projeto foi concebido para a disciplina de Programação Orientada a Objetos, aplicando de forma prática e integrada os quatro pilares fundamentais do paradigma: herança, abstração, encapsulamento e polimorfismo.

---

## Funcionalidades

- Cadastro de jogadores com nome, idade, nacionalidade e atributos técnicos
- Cálculo automático do overall (nota geral) baseado na posição do jogador
- Visualização de cards individuais por jogador
- Comparação lado a lado entre dois jogadores
- Filtro por seleção e por posição
- Listagem e ordenação do elenco por overall

---

## Modelagem Orientada a Objetos

### Hierarquia de Classes

A classe `Jogador` é abstrata e serve como base para todas as posições. Ela contém os atributos e comportamentos comuns a qualquer jogador, como nome, idade e nacionalidade. As classes concretas — `Atacante`, `MeioCampo`, `Defensor` e `Goleiro` — herdam de `Jogador` e especializam seus atributos e a lógica de cálculo do overall.

```
Jogador (abstrata)
├── Atacante
├── MeioCampo
├── Defensor
└── Goleiro

Selecao
└── contém lista de Jogador

Copa
└── contém lista de Selecao
```

---

## Aplicação dos Pilares de POO

### 1. Herança
As classes `Atacante`, `MeioCampo`, `Defensor` e `Goleiro` herdam os atributos e métodos comuns da classe `Jogador`, evitando repetição de código. Cada subclasse adiciona apenas os atributos específicos da sua posição.

### 2. Abstração
A classe `Jogador` define o método abstrato `calcular_overall()`, estabelecendo um contrato que todas as subclasses devem cumprir. O sistema sabe que todo jogador possui um overall, mas delega o cálculo para cada posição — que possui critérios distintos de avaliação.

### 3. Encapsulamento
Os atributos dos jogadores são privados e acessados exclusivamente por meio de getters e setters. Os setters realizam validações, como garantir que atributos técnicos estejam entre 0 e 99 e que a idade seja compatível com a de um atleta profissional.

### 4. Polimorfismo
O método `calcular_overall()` é chamado de forma idêntica para qualquer jogador, independente da posição. Cada classe calcula o overall com pesos diferentes: um atacante é avaliado principalmente por chute e velocidade, enquanto um goleiro é avaliado por reflexo e posicionamento. A interface gráfica também se beneficia do polimorfismo ao renderizar cards com cores distintas por posição, usando o mesmo método de exibição.

---

## Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python 3.x | Linguagem principal |
| CustomTkinter | Interface gráfica moderna |
| Pillow (PIL) | Manipulação de imagens nos cards |

---

## Estrutura de Arquivos

```
copa_card_manager/
├── main.py                  # Ponto de entrada da aplicação
├── models/
│   ├── jogador.py           # Classe abstrata Jogador
│   ├── atacante.py
│   ├── meiocampo.py
│   ├── defensor.py
│   ├── goleiro.py
│   └── selecao.py
├── views/
│   ├── tela_principal.py    # Tela inicial com listagem
│   ├── tela_cadastro.py     # Formulário de cadastro
│   ├── tela_card.py         # Visualização do card do jogador
│   └── tela_comparacao.py   # Comparação entre dois jogadores
└── assets/
    └── bandeiras/           # Imagens das bandeiras das seleções
```

---

## Exemplo de Funcionamento

O usuário abre o sistema e visualiza uma lista de seleções cadastradas. Ao selecionar uma seleção, vê todos os jogadores do elenco com seus overalls. Ao clicar em um jogador, um card é exibido com seus atributos dispostos visualmente. O usuário pode também selecionar dois jogadores e acionar a comparação, que exibe os atributos lado a lado com destaque para o melhor em cada categoria.

---

## Conclusão

O Copa Card Manager é um projeto que vai além da simples implementação dos conceitos de POO — ele os utiliza de forma que cada decisão de design de classe resolve um problema real do sistema. A escolha da Copa do Mundo como tema torna o domínio do problema familiar e facilita a compreensão da modelagem, enquanto a interface gráfica agrega valor de apresentação e demonstra a separação entre lógica de negócio e camada de visualização.
