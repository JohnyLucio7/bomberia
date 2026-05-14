import pygame
from src.engine.player import Player
from src.engine.map import Map

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        spritesheet_path = "assets/sprites/Bomberman-spritesheet.png"
        self.map = Map(spritesheet_path)
        
        # Calcular offset para centralizar o mapa (10x10 tiles de 32x32 pixels)
        map_pixel_size = self.map.total_size * self.map.display_tile_size
        self.offset_x = (self.width - map_pixel_size) // 2
        self.offset_y = (self.height - map_pixel_size) // 2
        
        # Posicionar player no centro do grid interno 8x8
        # O grid interno começa após a borda (1 tile de 32px)
        self.player = Player(
            self.offset_x + self.map.display_tile_size * 4, 
            self.offset_y + self.map.display_tile_size * 4, 
            spritesheet_path
        )
        self.clock = pygame.time.Clock()
        
    def update(self):
        dt = self.clock.tick(60) / 1000.0
        self.player.update(dt)
        
    def draw(self):
        self.screen.fill((50, 50, 50))  # Fundo cinza escuro
        self.map.draw(self.screen, self.offset_x, self.offset_y)
        self.player.draw(self.screen)
