import pygame
from src.engine.player import Player

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Centralizar o player (considerando escala 2x = 32x32)
        self.player = Player(self.width // 2 - 16, self.height // 2 - 16, "assets/sprites/Bomberman-spritesheet.png")
        self.clock = pygame.time.Clock()
        
    def update(self):
        dt = self.clock.tick(60) / 1000.0  # Delta time em segundos
        self.player.update(dt)
        
    def draw(self):
        self.screen.fill((34, 139, 34))  # Verde grama
        self.player.draw(self.screen)
