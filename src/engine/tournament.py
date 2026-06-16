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


def run_tournament(screen, n_matches=20, swap_sides=True, max_turns=1000,
                   mcts_time_limit=0.3, minimax_depth=1, progress_cb=None):
    """Roda N partidas MCTS vs Minimax em modo headless (sem renderização)."""
    completed = 0
    stats = {"MCTS": 0, "Minimax": 0, "DRAW/timeout": 0}

    font = pygame.font.SysFont("Arial", 24)
    font_bold = pygame.font.SysFont("Arial", 32, bold=True)

    def draw_progress(current, total, last_winner=None):
        screen.fill((30, 30, 30))
        title = font_bold.render(f"TOURNAMENT PROGRESS: {current}/{total}", True, (255, 200, 0))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 100)))

        y = 200
        for name, wins in stats.items():
            color = (200, 200, 200)
            if name == "MCTS": color = (100, 100, 255)
            if name == "Minimax": color = (255, 100, 100)

            txt = font.render(f"{name}: {wins} wins", True, color)
            screen.blit(txt, txt.get_rect(center=(screen.get_width() // 2, y)))
            y += 40

        if last_winner:
            msg = font.render(f"Last Match: {last_winner}", True, (150, 150, 150))
            screen.blit(msg, msg.get_rect(center=(screen.get_width() // 2, y + 40)))

        pygame.display.flip()

    for m in range(n_matches):
        draw_progress(m, n_matches)

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

        if game.winner == "Player 1":
            winner_name = side1_name
        elif game.winner == "Player 2":
            winner_name = side2_name
        else:
            winner_name = "DRAW/timeout"
            
        stats[winner_name] += 1
        completed += 1
        
        if progress_cb:
            progress_cb(m + 1, n_matches, winner_name, game.recorder.turns)

    # Final update after last match
    draw_progress(n_matches, n_matches, winner_name)
    return completed
