import os
import json
import matplotlib.pyplot as plt
import numpy as np

def generate_all(show=False, source_filter=None):
    if not os.path.exists("stats/history.jsonl"):
        return []

    matches = []
    with open("stats/history.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            match_data = json.loads(line)
            if source_filter and match_data.get("source") != source_filter:
                continue
            matches.append(match_data)

    if not matches:
        return []

    os.makedirs("stats/plots", exist_ok=True)
    plt.style.use('bmh')
    
    agent_stats = {}
    wins_by_agent = {}
    total_draws = 0
    
    for match in matches:
        agents = match['agents']
        winner_idx = match.get('winner')
        if winner_idx is None:
            total_draws += 1
        else:
            winner_name = agents[winner_idx - 1]
            wins_by_agent[winner_name] = wins_by_agent.get(winner_name, 0) + 1
            
        for i, name in enumerate(agents):
            player_pos = str(i + 1)
            if name not in agent_stats:
                agent_stats[name] = {
                    'suicides': 0,
                    'decision_time': [],
                    'blocks': 0,
                    'bombs': 0,
                    'matches': 0
                }
            agent_stats[name]['matches'] += 1
            agent_stats[name]['suicides'] += match.get('suicides', {}).get(player_pos, 0)
            agent_stats[name]['blocks'] += match.get('blocks_destroyed', {}).get(player_pos, 0)
            agent_stats[name]['bombs'] += match.get('bombs_placed', {}).get(player_pos, 0)
            agent_stats[name]['decision_time'].append(match.get('avg_decision_time', {}).get(player_pos, 0))

    agent_names = sorted(list(agent_stats.keys()))
    if not agent_names:
        return []

    fig, axs = plt.subplots(4, 2, figsize=(16, 24))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    fig.suptitle(f'Bomberia AI Dashboard - {len(matches)} Partidas', fontsize=20, fontweight='bold', y=0.96)

    # 1. Vitórias
    labels = agent_names + ['Empate']
    sizes = [wins_by_agent.get(name, 0) for name in agent_names] + [total_draws]
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    axs[0, 0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
    axs[0, 0].add_artist(plt.Circle((0,0), 0.70, fc='white'))
    axs[0, 0].set_title('Distribuição de Vitórias', fontsize=14, fontweight='bold')

    # 2. Agressividade
    valid_dist_matches = [m for m in matches if m.get('avg_distance', 0) > 0]
    if valid_dist_matches:
        avg_dist = np.mean([m['avg_distance'] for m in valid_dist_matches])
        aggressiveness = 10 / (avg_dist + 1)
        axs[0, 1].bar(['Confronto Global'], [aggressiveness], color='#e67e22', width=0.5)
        axs[0, 1].set_ylim(0, 10)
        axs[0, 1].set_title('Índice de Agressividade (0-10)', fontsize=14, fontweight='bold')
        axs[0, 1].text(0, aggressiveness + 0.2, f'{aggressiveness:.2f}', ha='center', fontweight='bold')
    else:
        axs[0, 1].text(0.5, 0.5, 'Dados insuficientes', ha='center', va='center')

    # 3. Turnos
    match_turns = [m['turns'] for m in matches]
    axs[1, 0].plot(match_turns, alpha=0.3, color='gray', label='Turnos')
    if len(match_turns) > 10:
        moving_avg = np.convolve(match_turns, np.ones(10)/10, mode='valid')
        axs[1, 0].plot(range(9, len(match_turns)), moving_avg, color='red', linewidth=2, label='Média Móvel (10)')
    axs[1, 0].set_title('Evolução da Duração', fontsize=14, fontweight='bold')
    axs[1, 0].set_xlabel('Partida')
    axs[1, 0].set_ylabel('Turnos')
    axs[1, 0].legend()

    # 4. Suicídios
    s_vals = [agent_stats[name]['suicides'] for name in agent_names]
    bars_s = axs[1, 1].bar(agent_names, s_vals, color=colors[:len(agent_names)])
    axs[1, 1].set_title('Total de Suicídios', fontsize=14, fontweight='bold')
    for bar in bars_s:
        yval = bar.get_height()
        axs[1, 1].text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontweight='bold')

    # 5. Decisão
    t_vals = [np.mean(agent_stats[name]['decision_time']) * 1000 for name in agent_names]
    bars_t = axs[2, 0].bar(agent_names, t_vals, color=colors[:len(agent_names)])
    axs[2, 0].set_title('Tempo de Decisão Médio', fontsize=14, fontweight='bold')
    axs[2, 0].set_ylabel('ms')
    for bar in bars_t:
        yval = bar.get_height()
        axs[2, 0].text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval:.1f}ms', ha='center', va='bottom', fontweight='bold')

    # 6. Blocos
    b_vals = [agent_stats[name]['blocks'] / agent_stats[name]['matches'] for name in agent_names]
    bars_b = axs[2, 1].bar(agent_names, b_vals, color=colors[:len(agent_names)])
    axs[2, 1].set_title('Média de Blocos Destruídos', fontsize=14, fontweight='bold')
    for bar in bars_b:
        yval = bar.get_height()
        axs[2, 1].text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval:.1f}', ha='center', va='bottom', fontweight='bold')

    # 7. Bombas
    bomb_vals = [agent_stats[name]['bombs'] / agent_stats[name]['matches'] for name in agent_names]
    bars_bomb = axs[3, 0].bar(agent_names, bomb_vals, color=colors[:len(agent_names)])
    axs[3, 0].set_title('Média de Bombas por Partida', fontsize=14, fontweight='bold')
    for bar in bars_bomb:
        yval = bar.get_height()
        axs[3, 0].text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval:.1f}', ha='center', va='bottom', fontweight='bold')
    
    axs[3, 1].axis('off')

    dashboard_path = "stats/plots/dashboard.png"
    plt.savefig(dashboard_path, bbox_inches='tight')
    
    if show:
        plt.show()
    plt.close()

    return [dashboard_path]
