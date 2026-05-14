import pygame

class Map:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        # 0: Empty, 1: Wall (Indestructible), 2: Block (Destructible)

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(screen, (50, 50, 50), rect)
                elif self.grid[y][x] == 2:
                    pygame.draw.rect(screen, (139, 69, 19), rect)
