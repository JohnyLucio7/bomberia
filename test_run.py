import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
from src.engine.tournament import run_tournament

def test():
    pygame.init()
    # No dummy mode, o set_mode ainda é necessário para inicializar certas partes do pygame
    screen = pygame.display.set_mode((800, 800))
    
    print("Iniciando teste de torneio (2 partidas)...")
    
    def progress(i, total, winner, turns):
        print(f"  Partida {i}/{total}: Vencedor={winner} em {turns} turnos")

    try:
        run_tournament(screen, n_matches=2, progress_cb=progress)
        print("Teste concluído com sucesso!")
    except Exception as e:
        print(f"Erro durante o teste: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    test()
