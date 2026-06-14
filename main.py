import pygame
import sys
from src.engine.game import Game
from src.engine.menu import MainMenu, AgentSelectMenu
from src.engine.tournament import run_tournament
from src.agents.mcts_agent import MCTSAgent
from src.agents.minimax_agent import MinimaxAgent
from src.stats.aggregate import build_report
from src.stats import plots


_MCTS_TIMES = {"30ms": 0.03, "100ms": 0.1, "300ms": 0.3, "500ms": 0.5}
_MM_DEPTHS  = {"1": 1, "2": 2, "3": 3, "4": 4}

_AI_ROWS = [
    {"label": "Game Mode",        "options": ["Smooth", "Step-by-Step"],          "key": "mode"},
    {"label": "Player 1",         "options": ["MCTS", "Minimax"],                  "key": "agent1_key"},
    {"label": "  MCTS Time",      "options": ["30ms", "100ms", "300ms", "500ms"], "key": "agent1_mcts_time",  "sub": True},
    {"label": "  Minimax Depth",  "options": ["1", "2", "3", "4"],                "key": "agent1_mm_depth",   "sub": True},
    {"label": "Player 2",         "options": ["MCTS", "Minimax"],                  "key": "agent2_key"},
    {"label": "  MCTS Time",      "options": ["30ms", "100ms", "300ms", "500ms"], "key": "agent2_mcts_time",  "sub": True},
    {"label": "  Minimax Depth",  "options": ["1", "2", "3", "4"],                "key": "agent2_mm_depth",   "sub": True},
]
_HUMAN_ROWS = [
    {"label": "Game Mode",       "options": ["Smooth", "Step-by-Step"],          "key": "mode"},
    {"label": "AI Opponent",     "options": ["MCTS", "Minimax"],                  "key": "agent2_key"},
    {"label": "  MCTS Time",     "options": ["30ms", "100ms", "300ms", "500ms"], "key": "agent2_mcts_time",  "sub": True},
    {"label": "  Minimax Depth", "options": ["1", "2", "3", "4"],                "key": "agent2_mm_depth",   "sub": True},
]


def _make_agents(config):
    mode_label = config.get("mode", "Smooth")
    mode  = "SMOOTH" if mode_label == "Smooth" else "STEP"
    smooth = (mode == "SMOOTH")

    def _build(type_key, mcts_key, mm_key, player_id):
        v = config.get(type_key, "Human")
        if v == "MCTS":
            default_time = "30ms" if smooth else "300ms"
            t = _MCTS_TIMES.get(config.get(mcts_key, default_time), 0.03 if smooth else 0.3)
            return MCTSAgent(player_id, time_limit=t)
        if v == "Minimax":
            default_depth = "1" if smooth else "2"
            d = _MM_DEPTHS.get(config.get(mm_key, default_depth), 1 if smooth else 2)
            return MinimaxAgent(player_id, depth=d)
        return None

    a1    = _build("agent1_key", "agent1_mcts_time", "agent1_mm_depth", 1)
    a2    = _build("agent2_key", "agent2_mcts_time", "agent2_mm_depth", 2)
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
                    # Smooth, P1=MCTS/30ms/d1, P2=Minimax/30ms/d1
                    agent_menu = AgentSelectMenu(screen, _AI_ROWS, defaults=[0, 0, 0, 0, 1, 0, 0])
                elif mode == "STEP":
                    # Step, P1=MCTS/300ms/d2, P2=MCTS/300ms/d2
                    agent_menu = AgentSelectMenu(screen, _AI_ROWS, defaults=[1, 0, 2, 1, 0, 2, 1])
                elif mode == "HUMAN_VS_AI":
                    # Smooth, oponent=MCTS/30ms/d1
                    agent_menu = AgentSelectMenu(screen, _HUMAN_ROWS, defaults=[0, 0, 0, 0])
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
