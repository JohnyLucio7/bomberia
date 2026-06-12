import pygame

from src.engine.game import Game
from src.agents.mcts_agent import MCTSAgent
from src.agents.minimax_agent import MinimaxAgent


def _make_agent(name, player_id, mcts_time_limit, minimax_depth):
    if name == "MCTS":
        return MCTSAgent(player_id, time_limit=mcts_time_limit)
    if name == "Minimax":
        return MinimaxAgent(player_id, depth=minimax_depth)
    raise ValueError(f"Agente desconhecido: {name}")


def run_tournament(screen, n_matches=20, swap_sides=True, max_turns=3000,
                   mcts_time_limit=0.02, minimax_depth=1, progress_cb=None):
    """Roda N partidas MCTS vs Minimax em modo headless (sem renderização).

    - swap_sides: alterna quem joga como jogador 1/2 a cada partida (fairness).
    - max_turns: cap anti-stalemate; ao atingir, a partida é registrada como empate/timeout.
    - progress_cb(i, n, winner_name, turns): callback opcional de progresso.

    Cada partida é anexada a stats/history.jsonl com source="batch".
    Retorna o nº de partidas concluídas.
    """
    completed = 0
    for m in range(n_matches):
        if swap_sides and m % 2 == 1:
            side1_name, side2_name = "Minimax", "MCTS"
        else:
            side1_name, side2_name = "MCTS", "Minimax"

        agent1 = _make_agent(side1_name, 1, mcts_time_limit, minimax_depth)
        agent2 = _make_agent(side2_name, 2, mcts_time_limit, minimax_depth)

        game = Game(screen, mode="SMOOTH", agent1=agent1, agent2=agent2,
                    agent_names=(side1_name, side2_name), record=True,
                    source="batch", headless=True)

        while not game.game_over and game.recorder.turns < max_turns:
            game.update()
            pygame.event.pump()  # mantém o SO ciente de que a janela está viva

        if not game.game_over:
            # Timeout / stalemate: finaliza como empate
            game.winner = None
            game.finalize_record()

        completed += 1
        if progress_cb:
            if game.winner == "Player 1":
                winner_name = side1_name
            elif game.winner == "Player 2":
                winner_name = side2_name
            else:
                winner_name = "DRAW/timeout"
            progress_cb(m + 1, n_matches, winner_name, game.recorder.turns)

    return completed
