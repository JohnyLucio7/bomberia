import pygame
from src.engine.player import Player
from src.engine.map import Map
from src.engine.bomb import Bomb, Explosion

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        self.spritesheet_path = "assets/sprites/Bomberman-spritesheet.png"
        self.map = Map(self.spritesheet_path)
        
        map_pixel_size = self.map.total_size * self.map.display_tile_size
        self.offset_x = (self.width - map_pixel_size) // 2
        self.offset_y = (self.height - map_pixel_size) // 2
        
        self.player = Player(
            self.offset_x + self.map.display_tile_size * 1, 
            self.offset_y + self.map.display_tile_size * 1, 
            self.spritesheet_path
        )
        self.bombs = []
        self.explosions = []
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        
    def reset_game(self):
        self.map = Map(self.spritesheet_path)
        self.player = Player(
            self.offset_x + self.map.display_tile_size * 1, 
            self.offset_y + self.map.display_tile_size * 1, 
            self.spritesheet_path
        )
        self.bombs = []
        self.explosions = []
        self.game_over = False

    def handle_input(self):
        if self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.reset_game()
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Calcular posição da bomba no grid de forma mais precisa
            # Centralizamos a detecção no meio do player (32x32 offset se player é 64x64)
            player_center_x = self.player.x + (self.player.tile_size * self.player.scale) // 2
            player_center_y = self.player.y + (self.player.tile_size * self.player.scale) // 2
            
            rel_x = player_center_x - self.offset_x
            rel_y = player_center_y - self.offset_y
            
            grid_col = int(rel_x // self.map.display_tile_size) - 1
            grid_row = int(rel_y // self.map.display_tile_size) - 1
            
            # Validar se está dentro do grid 8x8
            if 0 <= grid_row < 8 and 0 <= grid_col < 8:
                # Evitar múltiplas bombas no mesmo tile
                if not any(b.grid_pos == (grid_row, grid_col) for b in self.bombs):
                    new_bomb = Bomb(
                        self.offset_x + (grid_col + 1) * self.map.display_tile_size,
                        self.offset_y + (grid_row + 1) * self.map.display_tile_size,
                        (grid_row, grid_col),
                        self.spritesheet_path
                    )
                    self.bombs.append(new_bomb)

    def update(self):
        dt = self.clock.tick(60) / 1000.0
        self.handle_input()
        
        if self.game_over:
            return

        self.player.update(dt, self.map, self.offset_x, self.offset_y, self.bombs)
        
        # Update bombas
        for bomb in self.bombs[:]:
            bomb.update(dt)
            if bomb.exploded:
                self.explosions.append(Explosion(
                    bomb.x, bomb.y, bomb.grid_pos, 
                    bomb.range, self.map
                ))
                self.bombs.remove(bomb)
        
        # Update explosões
        for exp in self.explosions[:]:
            exp.update(dt)
            if exp.finished:
                self.explosions.remove(exp)

        # Checar colisão do player com explosões
        self._check_player_death()

    def _check_player_death(self):
        if self.player.is_dead:
            if self.player.death_finished:
                self.game_over = True
            return

        player_center_x = self.player.x + (self.player.tile_size * self.player.scale) // 2
        player_center_y = self.player.y + (self.player.tile_size * self.player.scale) // 2
        
        rel_x = player_center_x - self.offset_x
        rel_y = player_center_y - self.offset_y
        
        grid_col = int(rel_x // self.map.display_tile_size) - 1
        grid_row = int(rel_y // self.map.display_tile_size) - 1
        
        for exp in self.explosions:
            for r, c, _ in exp.tiles:
                if r == grid_row and c == grid_col:
                    self.player.is_dead = True
                    self.player.current_anim = "death"
                    self.player.frame_index = 0
                    return
        
    def draw(self):
        self.screen.fill((50, 50, 50))
        self.map.draw(self.screen, self.offset_x, self.offset_y)
        
        for bomb in self.bombs:
            bomb.draw(self.screen)
        for exp in self.explosions:
            exp.draw(self.screen, self.offset_x, self.offset_y, self.map.display_tile_size)
            
        self.player.draw(self.screen)

        if self.game_over:
            # Overlay escurecido
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0,0))
            
            text = self.font.render("GAME OVER", True, (255, 255, 255))
            restart_text = self.font.render("Press 'R' to Restart", True, (200, 200, 200))
            
            text_rect = text.get_rect(center=(self.width//2, self.height//2 - 20))
            restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 40))
            
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_text, restart_rect)
