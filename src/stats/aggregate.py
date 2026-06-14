import json
import os

def build_report():
    if not os.path.exists("stats/history.jsonl"):
        return "Nenhum dado de histórico encontrado."
    
    matches = []
    with open("stats/history.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            matches.append(json.loads(line))
            
    if not matches:
        return "Histórico vazio."

    total = len(matches)
    p1_wins = sum(1 for m in matches if m['winner'] == 1)
    p2_wins = sum(1 for m in matches if m['winner'] == 2)
    draws = total - p1_wins - p2_wins
    
    # Recentes (últimas 10)
    recent = matches[-10:]
    r_total = len(recent)
    r1_wins = sum(1 for m in recent if m['winner'] == 1)
    r2_wins = sum(1 for m in recent if m['winner'] == 2)
    
    avg_dist_all = sum(m.get('avg_distance', 0) for m in matches) / total
    p1_suicides = sum(m.get('suicides', {}).get('1', 0) for m in matches)
    p2_suicides = sum(m.get('suicides', {}).get('2', 0) for m in matches)
    
    agent1 = matches[0]['agents'][0]
    agent2 = matches[0]['agents'][1]

    report = [
        "=== RELATÓRIO DE PERFORMANCE HISTÓRICA ===",
        f"Total de partidas: {total}",
        f"Vitorias {agent1} (P1): {p1_wins} ({p1_wins/total:.1%})",
        f"Vitorias {agent2} (P2): {p2_wins} ({p2_wins/total:.1%})",
        f"Empates/Timeouts: {draws} ({draws/total:.1%})",
        "",
        f"=== DESEMPENHO RECENTE (Últimas {r_total} partidas) ===",
        f"Vitorias {agent1}: {r1_wins} ({r1_wins/r_total:.1%})",
        f"Vitorias {agent2}: {r2_wins} ({r2_wins/r_total:.1%})",
        "",
        "--- Métricas de Comportamento (Global) ---",
        f"Distância média entre jogadores: {avg_dist_all:.2f} blocos",
        f"Suicídios {agent1} (P1): {p1_suicides}",
        f"Suicídios {agent2} (P2): {p2_suicides}",
        "-------------------------------"
    ]
    return "\n".join(report)
