# snake-search-ai

Projeto de exemplo que implementa o jogo Snake usando algoritmos de busca, como Busca Gulosa e A* (A Star).

## Visão geral

O repositório contém:

- `src/main.py`: entrada do projeto com uma simulação simples da evolução do jogo.
- `src/core/`: classes básicas do jogo, incluindo tabuleiro, cobra, comida e estatísticas.
- `src/algorithms/`: implementações de algoritmos de busca e caminhos para o jogo.
- `src/ui/`: interfaces gráficas e utilitários de visualização do jogo.
- `src/simulations/`: scripts de benchmark e simulações.

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/L3onVictor/snake-search-ai
cd snake-search-ai
```

2. Crie e ative um ambiente virtual Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Como usar

Para abrir a interface do jogo e observar a tela, execute este comando a partir da raiz do projeto:

```powershell
python -m src.ui.game_ui2
```

Isso deve iniciar a interface gráfica definida em `src/ui/game_ui2.py`.

## Estrutura do projeto

- `src/ui/game_ui.py` e `src/ui/game_ui2.py`: interfaces gráficas e visualização do jogo.
- `src/core/`: classes do jogo, incluindo tabuleiro, cobra, comida e estatísticas.
- `src/algorithms/`: implementações de algoritmos de busca.

