import pygame
import sys
from src.engine.game import Game

def main():
    pygame.init()
    
    # Configurações básicas
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    FPS = 60
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bomberia AI Testbed")
    clock = pygame.time.Clock()
    
    game = Game(screen)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
