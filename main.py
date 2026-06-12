import pygame
import sys
from src.engine.game import Game
from src.engine.menu import MainMenu
from src.engine.tournament import run_tournament
from src.agents.mcts_agent import MCTSAgent
from src.agents.minimax_agent import MinimaxAgent
from src.stats.aggregate import build_report
from src.stats import plots


def _ask_int(prompt, default):
    try:
        raw = input(prompt).strip()
        return int(raw) if raw else default
    except (ValueError, EOFError):
        return default


def run_tournament_flow(screen):
    print("\n=== TORNEIO (headless) — MCTS vs Minimax ===")
    n = _ask_int("Quantas partidas? [20]: ", 20)
    print(f"Rodando {n} partidas (sem renderização)...")

    def progress(i, total, winner, turns):
        print(f"  partida {i}/{total}: vencedor={winner} em {turns} turnos")

    run_tournament(screen, n_matches=n, progress_cb=progress)
    print(build_report())
    paths = plots.generate_all(show=True)
    if paths:
        print("\nGráficos gerados:")
        for p in paths:
            print(f"  {p}")
    print("Voltando ao menu...\n")


def run_stats_flow():
    print(build_report())
    paths = plots.generate_all(show=True)
    if not paths:
        print("Sem dados para gerar gráficos ainda.")
    else:
        print("\nGráficos gerados:")
        for p in paths:
            print(f"  {p}")
    print("Voltando ao menu...\n")


def main():
    pygame.init()

    # Configurações básicas
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    FPS = 60

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bomberia AI Testbed")
    clock = pygame.time.Clock()

    menu = MainMenu(screen)
    game = None

    state = "MENU"

    running = True
    while running:
        if state == "MENU":
            mode = menu.handle_input()
            if mode == "QUIT":
                running = False
            elif mode == "TOURNAMENT":
                run_tournament_flow(screen)
            elif mode == "STATS":
                run_stats_flow()
            elif mode:
                # Inicializar jogo com base no modo
                if mode == "SMOOTH":
                    game = Game(screen, mode="SMOOTH",
                                agent1=MCTSAgent(1, time_limit=0.03), agent2=MinimaxAgent(2, depth=1),
                                agent_names=("MCTS", "Minimax"), record=True, source="interactive")
                elif mode == "STEP":
                    game = Game(screen, mode="STEP",
                                agent1=MCTSAgent(1), agent2=MCTSAgent(2))
                elif mode == "HUMAN_VS_AI":
                    game = Game(screen, mode="SMOOTH",
                                agent1=None, agent2=MCTSAgent(2),
                                agent_names=("Human", "MCTS"), record=True, source="interactive")
                state = "GAME"

            menu.draw()
            pygame.display.flip()

        elif state == "GAME":
            for event in pygame.event.get(pygame.QUIT):
                running = False

            # Atalho para voltar ao menu
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                state = "MENU"

            game.update()
            game.draw()

            pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
