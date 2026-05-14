import pygame
from src.engine.utils import SpriteSheet

class Player:
    def __init__(self, x, y, spritesheet_path):
        self.x = x
        self.y = y
        self.tile_size = 16
        self.scale = 2  # Aumentar para 32x32 para melhor visibilidade
        self.speed = 2
        
        self.ss = SpriteSheet(spritesheet_path)

        # Cada frame tem 16x16. 
        # Linha 0 (y=0): Left (x=0, 16, 32), Down (x=48, 64, 80)
        # Linha 1 (y=16): Right (x=0, 16, 32), Up (x=48, 64, 80)

        self.animations = {
            "run_left":  [self._get_frame(0, 0), self._get_frame(16, 0), self._get_frame(32, 0)],
            "run_down":  [self._get_frame(48, 0), self._get_frame(64, 0), self._get_frame(80, 0)],
            "run_right": [self._get_frame(0, 16), self._get_frame(16, 16), self._get_frame(32, 16)],
            "run_up":    [self._get_frame(48, 16), self._get_frame(64, 16), self._get_frame(80, 16)]
        }

        self.current_anim = "run_down"
        self.frame_index = 0
        self.anim_speed = 0.15
        self.anim_timer = 0
        self.is_moving = False
        self.direction = pygame.Vector2(0, 0)

        # Rotina de teste: 3 passos em cada direção
        # Cada passo ~32 pixels (tamanho do player escalado)
        self.test_routine = [
            ("run_left", pygame.Vector2(-1, 0), 32 * 3),
            ("run_down", pygame.Vector2(0, 1), 32 * 3),
            ("run_right", pygame.Vector2(1, 0), 32 * 3),
            ("run_up", pygame.Vector2(0, -1), 32 * 3)
        ]
        self.routine_idx = 0
        self.target_dist = self.test_routine[0][2]
        self.traveled = 0

    def _get_frame(self, x, y):
        image = self.ss.get_image(x, y, 16, 16)
        return pygame.transform.scale(image, (16 * self.scale, 16 * self.scale))


    def update(self, dt):
        if self.routine_idx < len(self.test_routine):
            anim, dir_vec, dist = self.test_routine[self.routine_idx]
            self.current_anim = anim
            self.direction = dir_vec
            self.is_moving = True
            
            move_step = self.direction * self.speed
            self.x += move_step.x
            self.y += move_step.y
            self.traveled += self.speed
            
            if self.traveled >= dist:
                self.traveled = 0
                self.routine_idx = (self.routine_idx + 1) % len(self.test_routine)
        
        # Animação
        if self.is_moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_anim])
        else:
            self.frame_index = 0 # Idle seria o primeiro frame ou o último parado

    def draw(self, screen):
        image = self.animations[self.current_anim][self.frame_index]
        screen.blit(image, (self.x, self.y))
