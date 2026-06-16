import json
import os

def build_report(source_filter=None):
    if not os.path.exists("stats/history.jsonl"):
        return "Nenhum dado de histórico encontrado."

    matches = []
    with open("stats/history.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            match_data = json.loads(line)
            if source_filter and match_data.get("source") != source_filter:
                continue
            matches.append(match_data)

    if not matches:
        return f"Nenhuma partida encontrada (filtro: {source_filter if source_filter else 'Nenhum'})."

    total_matches = len(matches)
    wins_by_agent = {}
    total_draws = 0
    suicides_by_agent = {}
    blocks_by_agent = {}
    bombs_by_agent = {}
    decision_time_by_agent = {}
    match_count_by_agent = {}

    for match in matches:
        agents = match['agents']
        winner_idx = match.get('winner')

        if winner_idx is None:
            total_draws += 1
        else:
            winner_name = agents[winner_idx - 1]
            wins_by_agent[winner_name] = wins_by_agent.get(winner_name, 0) + 1

        for i, agent_name in enumerate(agents):
            player_pos = str(i + 1)
            match_count_by_agent[agent_name] = match_count_by_agent.get(agent_name, 0) + 1
            suicides_by_agent[agent_name] = suicides_by_agent.get(agent_name, 0) + match.get('suicides', {}).get(player_pos, 0)
            blocks_by_agent[agent_name] = blocks_by_agent.get(agent_name, 0) + match.get('blocks_destroyed', {}).get(player_pos, 0)
            bombs_by_agent[agent_name] = bombs_by_agent.get(agent_name, 0) + match.get('bombs_placed', {}).get(player_pos, 0)
            decision_time_by_agent[agent_name] = decision_time_by_agent.get(agent_name, 0) + match.get('avg_decision_time', {}).get(player_pos, 0)

    avg_distance_global = sum(m.get('avg_distance', 0) for m in matches) / total_matches

    recent_matches = matches[-10:]
    recent_total = len(recent_matches)
    recent_wins = {}
    for match in recent_matches:
        winner_idx = match.get('winner')
        if winner_idx is not None:
            winner_name = match['agents'][winner_idx - 1]
            recent_wins[winner_name] = recent_wins.get(winner_name, 0) + 1

    agent_names = sorted(list(match_count_by_agent.keys()))

    report = [
        "=== RELATÓRIO DE PERFORMANCE HISTÓRICA ===",
        f"Total de partidas: {total_matches}",
        f"Empates/Timeouts: {total_draws} ({total_draws/total_matches:.1%})",
        ""
    ]

    for name in agent_names:
        w = wins_by_agent.get(name, 0)
        report.append(f"Vitorias {name}: {w} ({w/total_matches:.1%})")

    report.append("")
    report.append(f"=== DESEMPENHO RECENTE (Últimas {recent_total} partidas) ===")
    for name in agent_names:
        rw = recent_wins.get(name, 0)
        report.append(f"Vitorias {name}: {rw} ({rw/recent_total:.1%})")

    report.extend(["", "--- Eficiência e Tempo (Médias por Partida) ---"])
    
    for name in agent_names:
        count = match_count_by_agent[name]
        avg_dt = (decision_time_by_agent[name] / count) * 1000
        avg_bl = blocks_by_agent[name] / count
        avg_bm = bombs_by_agent[name] / count
        report.append(f"{name:10} | Decisão: {avg_dt:6.2f}ms | Blocos: {avg_bl:4.1f} | Bombas: {avg_bm:4.1f}")

    report.extend([
        "",
        "--- Métricas de Comportamento (Global) ---",
        f"Distância média entre jogadores: {avg_distance_global:.2f} blocos"
    ])
    
    for name in agent_names:
        report.append(f"Suicídios {name:10}: {suicides_by_agent[name]}")

    report.append("-------------------------------")
    return "\n".join(report)
