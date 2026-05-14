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
        self.tiles = [grid_pos] 
        self.scale = scale
        
        # Carregar animação de explosão (80x80 total, 4 frames -> assumindo 20x20 cada)
        from src.engine.utils import SpriteSheet
        ss = SpriteSheet("assets/sprites/Bomberman-Explosion.png")
        self.frames = []
        for i in range(4):
            # Recorta frame 20x20 e escala para o tamanho do tile (um pouco maior para sobrepor)
            frame = ss.get_image(i * 20, 0, 20, 20)
            self.frames.append(pygame.transform.scale(frame, (int(20 * scale), int(20 * scale))))
        
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.5 / 4 # Divide o tempo total pelos frames
        
        # Calcular propagação
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            for r in range(1, bomb_range + 1):
                nr, nc = grid_pos[0] + dr * r, grid_pos[1] + dc * r
                if 0 <= nr < game_map.grid_size and 0 <= nc < game_map.grid_size:
                    if game_map.grid[nr][nc] == 1: 
                        break
                    self.tiles.append((nr, nc))
                    if game_map.grid[nr][nc] == 2: 
                        game_map.grid[nr][nc] = 0
                        break
                else:
                    break

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.finished = True
        
        # Animação
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = min(self.frame_index + 1, len(self.frames) - 1)

    def draw(self, screen, offset_x, offset_y, tile_size):
        # Centralizar o sprite de 20px (escalado) no tile de 16px (escalado)
        # 20 * 4 = 80px, 16 * 4 = 64px. Diferença de 16px -> -8px de offset.
        sprite_offset = (20 * self.scale - tile_size) // 2
        
        for r, c in self.tiles:
            draw_x = offset_x + (c + 1) * tile_size - sprite_offset
            draw_y = offset_y + (r + 1) * tile_size - sprite_offset
            screen.blit(self.frames[self.frame_index], (draw_x, draw_y))
