import pygame

class Bomb:
    def __init__(self, x, y, grid_pos, spritesheet_path, scale=4):
        self.x = x
        self.y = y
        self.grid_pos = grid_pos # (row, col)
        self.timer = 2.5 
        self.exploded = False
        self.range = 2
        self.scale = scale
        
        from src.engine.utils import SpriteSheet
        ss = SpriteSheet(spritesheet_path)
        
        # Animação da bomba: Linha 4 (y=48), Frames 1, 2, 3 (x=0, 16, 32)
        self.frames = [
            self._get_scaled_frame(ss, 0, 48),
            self._get_scaled_frame(ss, 16, 48),
            self._get_scaled_frame(ss, 32, 48)
        ]
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.2

    def _get_scaled_frame(self, ss, x, y):
        image = ss.get_image(x, y, 16, 16)
        return pygame.transform.scale(image, (16 * self.scale, 16 * self.scale))

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.exploded = True
        
        # Ciclo de animação
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], (self.x, self.y))

class Explosion:
    def __init__(self, x, y, grid_pos, bomb_range, game_map, scale=4):
        self.x = x
        self.y = y
        self.grid_pos = grid_pos
        self.timer = 0.5 
        self.finished = False
        self.scale = scale
        
        from src.engine.utils import SpriteSheet
        ss = SpriteSheet("assets/sprites/Bomberman-spritesheet.png")
        
        # Estrutura dos 4 frames da explosão (9 tiles por frame)
        # Cada entrada: (row, col) base (o centro da explosão no spritesheet)
        frame_centers = [(7, 3), (7, 8), (12, 3), (12, 8)]
        self.frames_tiles = []
        
        for r_base, c_base in frame_centers:
            # Dicionário de tiles para este frame
            tiles = {
                'center':    self._get_tile(ss, r_base, c_base),
                'up_mid':    self._get_tile(ss, r_base - 1, c_base),
                'up_end':    self._get_tile(ss, r_base - 2, c_base),
                'down_mid':  self._get_tile(ss, r_base + 1, c_base),
                'down_end':  self._get_tile(ss, r_base + 2, c_base),
                'left_mid':  self._get_tile(ss, r_base, c_base - 1),
                'left_end':  self._get_tile(ss, r_base, c_base - 2),
                'right_mid': self._get_tile(ss, r_base, c_base + 1),
                'right_end': self._get_tile(ss, r_base, c_base + 2),
            }
            self.frames_tiles.append(tiles)
            
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.5 / 4
        
        # Calcular propagação com tipos de tile
        self.tiles = [(grid_pos[0], grid_pos[1], 'center')]
        
        directions = {
            (0, 1):  ('right_mid', 'right_end'),
            (0, -1): ('left_mid', 'left_end'),
            (1, 0):  ('down_mid', 'down_end'),
            (-1, 0): ('up_mid', 'up_end')
        }
        
        for (dr, dc), (mid_type, end_type) in directions.items():
            for r in range(1, bomb_range + 1):
                nr, nc = grid_pos[0] + dr * r, grid_pos[1] + dc * r
                if 0 <= nr < game_map.grid_size and 0 <= nc < game_map.grid_size:
                    tile_at_map = game_map.grid[nr][nc]
                    if tile_at_map == 1: # Parede indestrutível
                        break
                    
                    is_last = (r == bomb_range)
                    
                    if tile_at_map == 2: # Bloco destrutível
                        game_map.grid[nr][nc] = 0
                        self.tiles.append((nr, nc, end_type))
                        break
                    
                    if is_last:
                        self.tiles.append((nr, nc, end_type))
                    else:
                        self.tiles.append((nr, nc, mid_type))
                else:
                    break

    def _get_tile(self, ss, r, c):
        # L5C3 -> (5-1)*16, (3-1)*16
        image = ss.get_image((c - 1) * 16, (r - 1) * 16, 16, 16)
        return pygame.transform.scale(image, (16 * self.scale, 16 * self.scale))

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.finished = True
        
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = min(self.frame_index + 1, len(self.frames_tiles) - 1)

    def draw(self, screen, offset_x, offset_y, tile_size):
        current_tileset = self.frames_tiles[self.frame_index]
        for r, c, part_type in self.tiles:
            draw_x = offset_x + (c + 1) * tile_size
            draw_y = offset_y + (r + 1) * tile_size
            screen.blit(current_tileset[part_type], (draw_x, draw_y))
