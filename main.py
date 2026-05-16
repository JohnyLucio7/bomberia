import pygame
import sys
from src.engine.game import Game
from src.engine.menu import MainMenu
from src.agents.mcts_agent import MCTSAgent

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
            elif mode:
                # Inicializar jogo com base no modo
                if mode == "SMOOTH":
                    game = Game(screen, mode="SMOOTH", 
                               agent1=MCTSAgent(1), agent2=MCTSAgent(2))
                elif mode == "STEP":
                    game = Game(screen, mode="STEP", 
                               agent1=MCTSAgent(1), agent2=MCTSAgent(2))
                elif mode == "HUMAN_VS_AI":
                    game = Game(screen, mode="SMOOTH", 
                               agent1=None, agent2=MCTSAgent(2))
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
