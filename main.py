import pygame
import sys
from src.engine.game import Game
from src.engine.menu import MainMenu, AgentSelectMenu
from src.engine.tournament import run_tournament
from src.agents.mcts_agent import MCTSAgent
from src.agents.minimax_agent import MinimaxAgent
from src.stats.aggregate import build_report
from src.stats import plots


_AI_ROWS = [
    {"label": "Game Mode", "options": ["Smooth", "Step-by-Step"], "key": "mode"},
    {"label": "Player 1",  "options": ["MCTS", "Minimax"],        "key": "agent1_key"},
    {"label": "Player 2",  "options": ["MCTS", "Minimax"],        "key": "agent2_key"},
]
_HUMAN_ROWS = [
    {"label": "Game Mode", "options": ["Smooth", "Step-by-Step"], "key": "mode"},
    {"label": "Opponent",  "options": ["MCTS", "Minimax"],        "key": "agent2_key"},
]


def _make_agents(config):
    def _build(key, player_id):
        v = config.get(key, "Human")
        if v == "MCTS":    return MCTSAgent(player_id, time_limit=0.3)
        if v == "Minimax": return MinimaxAgent(player_id, depth=2)
        return None
    mode_label = config.get("mode", "Smooth")
    mode  = "SMOOTH" if mode_label == "Smooth" else "STEP"
    a1    = _build("agent1_key", 1)
    a2    = _build("agent2_key", 2)
    names = (config.get("agent1_key", "Human"), config.get("agent2_key", "Human"))
    return a1, a2, names, mode


def _ask_int(prompt, default):
    try:
        raw = input(prompt).strip()
        return int(raw) if raw else default
    except (ValueError, EOFError):
        return default


def run_tournament_flow(screen, n_matches=20):
    print("\n=== TORNEIO (headless) — MCTS vs Minimax ===")
    print(f"Rodando {n_matches} partidas (sem renderização)...")

    def progress(i, total, winner, turns):
        print(f"  partida {i}/{total}: vencedor={winner} em {turns} turnos")

    run_tournament(screen, n_matches=n_matches, progress_cb=progress)
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

    # Pega número de partidas via argumento (opcional)
    n_matches = 20
    if len(sys.argv) > 1:
        try:
            n_matches = int(sys.argv[1])
        except ValueError:
            pass

    # Configurações básicas
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    FPS = 60

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bomberia AI Testbed")
    clock = pygame.time.Clock()

    menu       = MainMenu(screen)
    agent_menu = None
    game       = None

    state = "MENU"

    running = True
    while running:
        if state == "MENU":
            mode = menu.handle_input()
            if mode == "QUIT":
                running = False
            elif mode == "TOURNAMENT":
                run_tournament_flow(screen, n_matches=n_matches)
            elif mode == "STATS":
                run_stats_flow()
            elif mode:
                if mode == "SMOOTH":
                    agent_menu = AgentSelectMenu(screen, _AI_ROWS, defaults=[0, 0, 1])
                elif mode == "STEP":
                    agent_menu = AgentSelectMenu(screen, _AI_ROWS, defaults=[1, 0, 0])
                elif mode == "HUMAN_VS_AI":
                    agent_menu = AgentSelectMenu(screen, _HUMAN_ROWS, defaults=[0, 0])
                state = "AGENT_SELECT"

            menu.draw()
            pygame.display.flip()

        elif state == "AGENT_SELECT":
            result = agent_menu.handle_input()
            if result == "QUIT":
                running = False
            elif result == "BACK":
                state = "MENU"
            elif result is not None:
                a1, a2, names, game_mode = _make_agents(result)
                game = Game(screen, mode=game_mode, agent1=a1, agent2=a2,
                            agent_names=names, record=True, source="interactive")
                state = "GAME"

            agent_menu.draw()
            pygame.display.flip()

        elif state == "GAME":
            for event in pygame.event.get(pygame.QUIT):
                running = False

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
