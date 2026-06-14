import json
import os

def build_report():
    if not os.path.exists("stats/history.jsonl"):
        return "Nenhum dado de histórico encontrado."

    matches = []
    with open("stats/history.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            m = json.loads(line)
            if m.get("source") == "batch":  # só partidas do torneio
                matches.append(m)

    if not matches:
        return "Nenhuma partida de torneio encontrada."

    total = len(matches)

    # Acumuladores por NOME do agente, não por posição (P1/P2)
    wins = {}
    draws = 0
    suicides = {}
    blocks = {}
    bombs = {}
    decision_time = {}
    counts = {}  # quantas partidas cada agente participou (para médias)

    for m in matches:
        agents = m['agents']  # [nome_p1, nome_p2] dessa partida
        winner_idx = m.get('winner')

        if winner_idx is None:
            draws += 1
        else:
            winner_name = agents[winner_idx - 1]
            wins[winner_name] = wins.get(winner_name, 0) + 1

        for pos, name in zip(['1', '2'], agents):
            counts[name] = counts.get(name, 0) + 1
            suicides[name] = suicides.get(name, 0) + m.get('suicides', {}).get(pos, 0)
            blocks[name] = blocks.get(name, 0) + m.get('blocks_destroyed', {}).get(pos, 0)
            bombs[name] = bombs.get(name, 0) + m.get('bombs_placed', {}).get(pos, 0)
            decision_time[name] = decision_time.get(name, 0) + m.get('avg_decision_time', {}).get(pos, 0)

    avg_dist_all = sum(m.get('avg_distance', 0) for m in matches) / total

    # Recentes (últimas 10)
    recent = matches[-10:]
    r_total = len(recent)
    r_wins = {}
    r_draws = 0
    for m in recent:
        winner_idx = m.get('winner')
        if winner_idx is None:
            r_draws += 1
        else:
            winner_name = m['agents'][winner_idx - 1]
            r_wins[winner_name] = r_wins.get(winner_name, 0) + 1

    # Nomes dos agentes (assume só 2 nomes distintos no histórico)
    agent_names = list(counts.keys())
    if len(agent_names) != 2:
        return f"Histórico contém nomes de agentes inconsistentes: {agent_names}"
    agent1, agent2 = agent_names

    report = [
        "=== RELATÓRIO DE PERFORMANCE HISTÓRICA ===",
        f"Total de partidas: {total}",
        f"Vitorias {agent1}: {wins.get(agent1, 0)} ({wins.get(agent1, 0)/total:.1%})",
        f"Vitorias {agent2}: {wins.get(agent2, 0)} ({wins.get(agent2, 0)/total:.1%})",
        f"Empates/Timeouts: {draws} ({draws/total:.1%})",
        "",
        f"=== DESEMPENHO RECENTE (Últimas {r_total} partidas) ===",
        f"Vitorias {agent1}: {r_wins.get(agent1, 0)} ({r_wins.get(agent1, 0)/r_total:.1%})",
        f"Vitorias {agent2}: {r_wins.get(agent2, 0)} ({r_wins.get(agent2, 0)/r_total:.1%})",
        "",
        "--- Eficiência e Tempo ---",
        f"Tempo de Decisão (médio): {agent1}: {(decision_time[agent1]/counts[agent1])*1000:.2f}ms "
        f"| {agent2}: {(decision_time[agent2]/counts[agent2])*1000:.2f}ms",
        f"Blocos/Partida (médio): {agent1}: {blocks[agent1]/counts[agent1]:.1f} "
        f"| {agent2}: {blocks[agent2]/counts[agent2]:.1f}",
        f"Bombas/Partida (médio): {agent1}: {bombs[agent1]/counts[agent1]:.1f} "
        f"| {agent2}: {bombs[agent2]/counts[agent2]:.1f}",
        "",
        "--- Métricas de Comportamento (Global) ---",
        f"Distância média entre jogadores: {avg_dist_all:.2f} blocos",
        f"Suicídios {agent1}: {suicides[agent1]}",
        f"Suicídios {agent2}: {suicides[agent2]}",
        "-------------------------------"
    ]
    return "\n".join(report)