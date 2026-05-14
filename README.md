# Bomberia - AI Testing Environment

Este projeto é um ambiente simplificado do Bomberman para testar agentes de IA usando métodos de Monte Carlo (MCTS).

## Setup do Ambiente

Recomendamos o uso de um ambiente virtual (`venv`):

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Estrutura do Projeto

- `assets/sprites/`: Local para colocar o spritesheet do Bomberman.
- `src/`: Código fonte do jogo.
  - `src/engine/`: Lógica do jogo, física e renderização.
  - `src/agents/`: Implementações dos agentes de IA (Monte Carlo, etc).
- `main.py`: Ponto de entrada do jogo.

## Como Executar
```bash
python main.py
```
