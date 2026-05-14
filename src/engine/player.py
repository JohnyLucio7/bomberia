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
            "run_up":    [self._get_frame(48, 16), self._get_frame(64, 16), self._get_frame(80, 16)]
        }

        self.current_anim = "run_down"
        self.frame_index = 0
        self.anim_speed = 0.15
        self.anim_timer = 0
        self.is_moving = False
        self.direction = pygame.Vector2(0, 0)

    def _get_frame(self, x, y):
        image = self.ss.get_image(x, y, 16, 16)
        return pygame.transform.scale(image, (16 * self.scale, 16 * self.scale))

    def update(self, dt):
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
            self.x += self.direction.x * self.speed
            self.y += self.direction.y * self.speed
            
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_anim])
        else:
            self.frame_index = 0


    def draw(self, screen):
        image = self.animations[self.current_anim][self.frame_index]
        screen.blit(image, (self.x, self.y))
