import pygame
from src.engine.utils import SpriteSheet

class Player:
    def __init__(self, x, y, spritesheet_path):
        self.x = x
        self.y = y
        self.tile_size = 16
        self.scale = 4  # Aumentado para melhor visibilidade
        self.speed = 4  # Aumentado proporcionalmente

        self.ss = SpriteSheet(spritesheet_path)

        # Cada frame tem 16x16. 
        # Linha 0 (y=0): Left (x=0, 16, 32), Down (x=48, 64, 80)
        # Linha 1 (y=16): Right (x=0, 16, 32), Up (x=48, 64, 80)

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
        self.is_moving = False
        self.is_dead = False
        self.death_finished = False
        self.direction = pygame.Vector2(0, 0)

    def _get_frame(self, x, y):
        image = self.ss.get_image(x, y, 16, 16)
        return pygame.transform.scale(image, (16 * self.scale, 16 * self.scale))

    def update(self, dt, game_map, offset_x, offset_y):
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

        keys = pygame.key.get_pressed()
        self.direction = pygame.Vector2(0, 0)
        self.is_moving = False
        
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.current_anim = "run_left"
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.current_anim = "run_right"
            self.is_moving = True
        elif keys[pygame.K_UP]:
            self.direction.y = -1
            self.current_anim = "run_up"
            self.is_moving = True
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.current_anim = "run_down"
            self.is_moving = True
            
        if self.is_moving:
            # Tamanho real do player na tela
            p_size = self.tile_size * self.scale # 64
            # Bounding box reduzida para colisão (mais permissiva, centralizada nos pés)
            # Bombermans geralmente têm colisão menor que o sprite para facilitar navegação
            col_width = p_size * 0.6
            col_height = p_size * 0.4
            
            # Movimento X com colisão
            new_x = self.x + self.direction.x * self.speed
            if not self._check_collision(new_x + (p_size - col_width)/2, self.y + (p_size - col_height), 
                                       col_width, col_height, game_map, offset_x, offset_y):
                self.x = new_x

            # Movimento Y com colisão
            new_y = self.y + self.direction.y * self.speed
            if not self._check_collision(self.x + (p_size - col_width)/2, new_y + (p_size - col_height), 
                                       col_width, col_height, game_map, offset_x, offset_y):
                self.y = new_y
            
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_anim])
        else:
            self.frame_index = 0

    def _check_collision(self, x, y, width, height, game_map, offset_x, offset_y):
        # Retângulo de colisão do player
        player_rect = pygame.Rect(x, y, width, height)
        
        # Verificar apenas tiles próximos para performance
        # Converter coordenadas de tela para grid
        tile_size = game_map.display_tile_size
        
        for row in range(game_map.total_size):
            for col in range(game_map.total_size):
                # Borda externa
                is_obstacle = False
                if row == 0 or row == game_map.total_size - 1 or col == 0 or col == game_map.total_size - 1:
                    is_obstacle = True
                else:
                    inner_row = row - 1
                    inner_col = col - 1
                    if game_map.grid[inner_row][inner_col] in [1, 2]: # Parede ou Bloco
                        is_obstacle = True
                
                if is_obstacle:
                    tile_x = offset_x + col * tile_size
                    tile_y = offset_y + row * tile_size
                    tile_rect = pygame.Rect(tile_x, tile_y, tile_size, tile_size)
                    
                    if player_rect.colliderect(tile_rect):
                        return True
        return False


    def draw(self, screen):
        image = self.animations[self.current_anim][self.frame_index]
        screen.blit(image, (self.x, self.y))
