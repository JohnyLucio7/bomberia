import pygame
from src.engine.utils import SpriteSheet

class Player:
    def __init__(self, x, y, spritesheet_path, tint_color=None):
        self.x = x
        self.y = y
        self.tile_size = 16
        self.scale = 4  # 64 pixels
        self.speed = 4  
        self.tint_color = tint_color

        # Alinhamento no grid
        self.target_x = x
        self.target_y = y

        self.ss = SpriteSheet(spritesheet_path)

        self.animations = {
            "run_left":  [self._get_frame(0, 0), self._get_frame(16, 0), self._get_frame(32, 0)],
            "run_down":  [self._get_frame(48, 0), self._get_frame(64, 0), self._get_frame(80, 0)],
            "run_right": [self._get_frame(0, 16), self._get_frame(16, 16), self._get_frame(32, 16)],
            "run_up":    [self._get_frame(48, 16), self._get_frame(64, 16), self._get_frame(80, 16)],
            "death":     [self._get_frame(x * 16, 32) for x in range(7)]
        }

        self.current_anim = "run_down"
        self.frame_index = 0
        self.anim_speed = 0.15
        self.anim_timer = 0
        self.is_dead = False
        self.death_finished = False

    def _get_frame(self, x, y):
        image = self.ss.get_image(x, y, 16, 16)
        scaled = pygame.transform.scale(image, (16 * self.scale, 16 * self.scale))
        if self.tint_color:
            scaled.fill(self.tint_color, special_flags=pygame.BLEND_RGBA_MULT)
        return scaled

    def get_grid_pos(self, offset_x, offset_y, tile_size):
        # Centralizar detecção no sprite
        center_x = self.x + (self.tile_size * self.scale) // 2
        center_y = self.y + (self.tile_size * self.scale) // 2
        r = int((center_y - offset_y) // tile_size) - 1
        c = int((center_x - offset_x) // tile_size) - 1
        return (max(0, r), max(0, c))

    def update(self, dt, game_map, offset_x, offset_y, bombs=[], action=None, other_player=None):
        if self.is_dead:
            if not self.death_finished:
                self.anim_timer += dt
                if self.anim_timer >= self.anim_speed:
                    self.anim_timer = 0
                    if self.frame_index < len(self.animations["death"]) - 1:
                        self.frame_index += 1
                    else:
                        self.death_finished = True
            return

        p_size = self.tile_size * self.scale
        display_tile_size = game_map.display_tile_size

        # Atualizar estado de bombas internas
        col_width = p_size * 0.6
        col_height = p_size * 0.4
        player_rect = pygame.Rect(self.x + (p_size - col_width)/2, self.y + (p_size - col_height), 
                                col_width, col_height)
        for bomb in bombs:
            if self in bomb.players_inside:
                bomb_rect = pygame.Rect(bomb.x, bomb.y, p_size, p_size)
                if not player_rect.colliderect(bomb_rect):
                    bomb.players_inside.remove(self)

        # Se já chegou no target, aceitar novo input
        if self.x == self.target_x and self.y == self.target_y:
            if action and action != "IDLE" and action != "BOMB":
                dx, dy = 0, 0
                if action == "LEFT": dx = -1; self.current_anim = "run_left"
                elif action == "RIGHT": dx = 1; self.current_anim = "run_right"
                elif action == "UP": dy = -1; self.current_anim = "run_up"
                elif action == "DOWN": dy = 1; self.current_anim = "run_down"
                
                new_target_x = self.x + dx * display_tile_size
                new_target_y = self.y + dy * display_tile_size
                
                # Check collision for the target tile
                if not self._check_collision(new_target_x + (p_size - col_width)/2, 
                                           new_target_y + (p_size - col_height), 
                                           col_width, col_height, game_map, offset_x, offset_y, bombs, other_player):
                    self.target_x = new_target_x
                    self.target_y = new_target_y
            else:
                self.frame_index = 0

        # Mover em direção ao target
        if self.x != self.target_x or self.y != self.target_y:
            move_step = self.speed
            if abs(self.target_x - self.x) < move_step: self.x = self.target_x
            else: self.x += move_step if self.target_x > self.x else -move_step
            
            if abs(self.target_y - self.y) < move_step: self.y = self.target_y
            else: self.y += move_step if self.target_y > self.y else -move_step
            
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_anim])

    def _check_collision(self, x, y, width, height, game_map, offset_x, offset_y, bombs=[], other_player=None):
        player_rect = pygame.Rect(x, y, width, height)
        
        # Colisão com outro jogador (Body Blocking)
        if other_player and not other_player.is_dead:
            p_size = self.tile_size * self.scale
            # Usamos a mesma bounding box proporcional para o outro player
            other_col_width = p_size * 0.6
            other_col_height = p_size * 0.4
            other_rect = pygame.Rect(other_player.x + (p_size - other_col_width)/2, 
                                   other_player.y + (p_size - other_col_height), 
                                   other_col_width, other_col_height)
            if player_rect.colliderect(other_rect):
                return True

        # Colisão com Bombas
        for bomb in bombs:
            if self not in bomb.players_inside:
                bomb_rect = pygame.Rect(bomb.x, bomb.y, self.tile_size * self.scale, self.tile_size * self.scale)
                if player_rect.colliderect(bomb_rect):
                    return True
        
        tile_size = game_map.display_tile_size
        for row in range(game_map.total_size):
            for col in range(game_map.total_size):
                is_obstacle = False
                if row == 0 or row == game_map.total_size - 1 or col == 0 or col == game_map.total_size - 1:
                    is_obstacle = True
                else:
                    inner_row = row - 1
                    inner_col = col - 1
                    if game_map.grid[inner_row][inner_col] in [1, 2]:
                        is_obstacle = True
                
                if is_obstacle:
                    tile_rect = pygame.Rect(offset_x + col * tile_size, offset_y + row * tile_size, tile_size, tile_size)
                    if player_rect.colliderect(tile_rect):
                        return True
        return False

    def draw(self, screen):
        image = self.animations[self.current_anim][self.frame_index]
        screen.blit(image, (self.x, self.y))
