import pygame

from src.engine.utils import SpriteSheet

class Map:
    def __init__(self, spritesheet_path):
        self.tile_size = 16
        self.scale = 2
        self.display_tile_size = self.tile_size * self.scale
        
        # Tabuleiro 8x8 + Borda de 1 tile em cada lado = 10x10
        self.grid_size = 8
        self.total_size = self.grid_size + 2
        
        self.ss = SpriteSheet(spritesheet_path)
        self.border_sprite = self._get_sprite(48, 48)
        self.floor_color = (34, 139, 34) # Verde grama

    def _get_sprite(self, x, y):
        image = self.ss.get_image(x, y, self.tile_size, self.tile_size)
        return pygame.transform.scale(image, (self.display_tile_size, self.display_tile_size))

    def draw(self, screen, offset_x, offset_y):
        for row in range(self.total_size):
            for col in range(self.total_size):
                x = offset_x + col * self.display_tile_size
                y = offset_y + row * self.display_tile_size
                
                # Se for a borda
                if row == 0 or row == self.total_size - 1 or col == 0 or col == self.total_size - 1:
                    screen.blit(self.border_sprite, (x, y))
                else:
                    # Chão (interno 8x8)
                    pygame.draw.rect(screen, self.floor_color, (x, y, self.display_tile_size, self.display_tile_size))
                    # Opcional: desenhar grid sutil
                    pygame.draw.rect(screen, (0, 0, 0), (x, y, self.display_tile_size, self.display_tile_size), 1)
