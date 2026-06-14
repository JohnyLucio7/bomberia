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

## Estatísticas e Monitoramento!

O projeto conta com um sistema de telemetria para avaliar o desempenho das IAs:

- **Distribuição de Vitórias:** Compara o percentual de vitórias entre MCTS, Minimax e Empates.
- **Índice de Agressividade:** Escala de 0 a 10 baseada na proximidade média entre os agentes. Valores altos indicam comportamento de caça; valores baixos indicam foco em exploração/defesa.
- **Evolução da Duração:** Monitora o número de turnos por partida com uma média móvel para identificar se os jogos estão ficando mais eficientes.
- **Taxa de Suicídio:** Contabiliza mortes causadas pela própria bomba, ajudando a identificar falhas críticas de lógica.
- **Tempo de Decisão:** Monitora o custo computacional de cada agente (em milissegundos).
- **Métricas de Eficiência:** Média de blocos destruídos e bombas colocadas, indicando o nível de atividade no mapa.

Ao final de cada torneio, um **Dashboard Unificado** é gerado em `stats/plots/dashboard.png` com todas essas visões integradas.
