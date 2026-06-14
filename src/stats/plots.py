import os
import json
import matplotlib.pyplot as plt
import numpy as np

def generate_all(show=False):
    if not os.path.exists("stats/history.jsonl"):
        return []

    matches = []
    with open("stats/history.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            matches.append(json.loads(line))

    if not matches:
        return []

    os.makedirs("stats/plots", exist_ok=True)
    paths = []
    
    # Estilo geral
    plt.style.use('bmh')
    agent1_name = matches[0]['agents'][0]
    agent2_name = matches[0]['agents'][1]
    colors = ['#2ecc71', '#3498db', '#e74c3c']

    # Criar uma figura grande para o Dashboard (2x2 subplots)
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    fig.suptitle(f'Bomberia AI Dashboard - {len(matches)} Partidas', fontsize=20, fontweight='bold', y=0.95)

    # 1. Gráfico de Vitórias (Donut)
    p1_wins = sum(1 for m in matches if m['winner'] == 1)
    p2_wins = sum(1 for m in matches if m['winner'] == 2)
    draws = len(matches) - p1_wins - p2_wins
    labels = [agent1_name, agent2_name, 'Empate']
    sizes = [p1_wins, p2_wins, draws]
    
    axs[0, 0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
    center_circle = plt.Circle((0,0), 0.70, fc='white')
    axs[0, 0].add_artist(center_circle)
    axs[0, 0].set_title('Distribuição de Vitórias', fontsize=14, fontweight='bold')

    # 2. Gráfico de Agressividade Global
    valid_matches = [m for m in matches if 'avg_distance' in m and m['avg_distance'] > 0]
    if valid_matches:
        avg_dist = np.mean([m['avg_distance'] for m in valid_matches])
        aggressiveness = 10 / (avg_dist + 1)
        axs[0, 1].bar(['Confronto Global'], [aggressiveness], color='#e67e22', width=0.5)
        axs[0, 1].set_ylim(0, 10)
        axs[0, 1].set_title('Índice de Agressividade (0-10)', fontsize=14, fontweight='bold')
        axs[0, 1].grid(axis='y', linestyle='--', alpha=0.7)
        for i, v in enumerate([aggressiveness]):
            axs[0, 1].text(i, v + 0.2, f'{v:.2f}', ha='center', fontweight='bold')
    else:
        axs[0, 1].text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center')

    # 3. Evolução de Duração (Média Móvel)
    turns = [m['turns'] for m in matches]
    axs[1, 0].plot(turns, alpha=0.3, color='gray', label='Turnos')
    if len(turns) > 10:
        moving_avg = np.convolve(turns, np.ones(10)/10, mode='valid')
        axs[1, 0].plot(range(9, len(turns)), moving_avg, color='red', linewidth=2, label='Média Móvel (10)')
    axs[1, 0].set_title('Evolução da Duração', fontsize=14, fontweight='bold')
    axs[1, 0].set_xlabel('Partida')
    axs[1, 0].set_ylabel('Turnos')
    axs[1, 0].legend()

    # 4. Total de Suicídios
    s1 = sum(m.get('suicides', {}).get('1', 0) for m in matches)
    s2 = sum(m.get('suicides', {}).get('2', 0) for m in matches)
    bars = axs[1, 1].bar([agent1_name, agent2_name], [s1, s2], color=['#2ecc71', '#3498db'])
    axs[1, 1].set_title('Total de Suicídios', fontsize=14, fontweight='bold')
    axs[1, 1].set_ylabel('Ocorrências')
    for bar in bars:
        yval = bar.get_height()
        axs[1, 1].text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontweight='bold')

    # Salvar o Dashboard completo
    dashboard_path = "stats/plots/dashboard.png"
    plt.savefig(dashboard_path, bbox_inches='tight')
    paths.append(dashboard_path)
    
    if show:
        plt.show()
    
    plt.close()

    return paths
