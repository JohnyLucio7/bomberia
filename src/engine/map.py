import pygame

from src.engine.utils import SpriteSheet

class Map:
    def __init__(self, spritesheet_path):
        self.tile_size = 16
        self.scale = 4
        self.display_tile_size = self.tile_size * self.scale

        # Tabuleiro 8x8 + Borda de 1 tile = 10x10
        self.grid_size = 8
        self.total_size = self.grid_size + 2

        self.ss = SpriteSheet(spritesheet_path)
        self.border_sprite = self._get_sprite(48, 48)
        self.wall_sprite = self._get_sprite(48, 48) # Por enquanto mesmo da borda
        self.block_sprite = self._get_sprite(64, 48) # Sprite de bloco (x=64, y=48)

        self.floor_color = (34, 139, 34)

        # Grid lógico: 0: vazio, 1: parede, 2: bloco
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self._setup_initial_map()

    def _setup_initial_map(self):
        # Paredes fixas (padrão bomberman: intercaladas)
        # Em grid 8x8, vamos usar range(1, 7, 2) para garantir que as extremidades (0 e 7) fiquem livres
        for row in range(1, self.grid_size - 1, 2):
            for col in range(1, self.grid_size - 1, 2):
                self.grid[row][col] = 1

        # Adicionar alguns blocos destrutíveis aleatórios (exemplo simples)
        import random
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col] == 0:
                    # Não colocar blocos nos cantos (spawn dos players)
                    if (row < 2 and col < 2) or (row > 5 and col > 5):
                        continue
                    if random.random() < 0.7: # 70% de chance de bloco
                        self.grid[row][col] = 2

    def _get_sprite(self, x, y):
        image = self.ss.get_image(x, y, self.tile_size, self.tile_size)
        return pygame.transform.scale(image, (self.display_tile_size, self.display_tile_size))

    def draw(self, screen, offset_x, offset_y):
        for row in range(self.total_size):
            for col in range(self.total_size):
                x = offset_x + col * self.display_tile_size
                y = offset_y + row * self.display_tile_size

                # Borda externa
                if row == 0 or row == self.total_size - 1 or col == 0 or col == self.total_size - 1:
                    screen.blit(self.border_sprite, (x, y))
                else:
                    # Grid interno 8x8
                    inner_row = row - 1
                    inner_col = col - 1
                    tile_type = self.grid[inner_row][inner_col]

                    # Desenha o chão primeiro
                    pygame.draw.rect(screen, self.floor_color, (x, y, self.display_tile_size, self.display_tile_size))

                    if tile_type == 1:
                        screen.blit(self.wall_sprite, (x, y))
                    elif tile_type == 2:
                        screen.blit(self.block_sprite, (x, y))

                    # Grade sutil
                    pygame.draw.rect(screen, (0, 0, 0), (x, y, self.display_tile_size, self.display_tile_size), 1)

