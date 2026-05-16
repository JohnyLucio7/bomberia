import pygame
from src.engine.player import Player
from src.engine.map import Map
from src.engine.bomb import Bomb, Explosion
from src.engine.simulation import SimulatedState

class Game:
    def __init__(self, screen, mode="SMOOTH", agent1=None, agent2=None):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.mode = mode
        self.agent1 = agent1
        self.agent2 = agent2
        
        self.spritesheet_path = "assets/sprites/Bomberman-spritesheet.png"
        self.map = Map(self.spritesheet_path)
        
        map_pixel_size = self.map.total_size * self.map.display_tile_size
        self.offset_x = (self.width - map_pixel_size) // 2
        self.offset_y = (self.height - map_pixel_size) // 2
        
        self.player1 = Player(
            self.offset_x + self.map.display_tile_size * 1, 
            self.offset_y + self.map.display_tile_size * 1, 
            self.spritesheet_path
        )
        self.player2 = Player(
            self.offset_x + self.map.display_tile_size * 8, 
            self.offset_y + self.map.display_tile_size * 8, 
            self.spritesheet_path,
            tint_color=(100, 100, 255)
        )
        self.bombs = []
        self.explosions = []
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.winner = None
        self.font = pygame.font.SysFont("Arial", 48, bold=True)
        self.waiting_for_step = False

    def reset_game(self):
        self.map = Map(self.spritesheet_path)
        self.player1 = Player(
            self.offset_x + self.map.display_tile_size * 1, 
            self.offset_y + self.map.display_tile_size * 1, 
            self.spritesheet_path
        )
        self.player2 = Player(
            self.offset_x + self.map.display_tile_size * 8, 
            self.offset_y + self.map.display_tile_size * 8, 
            self.spritesheet_path,
            tint_color=(100, 100, 255)
        )
        self.bombs = []
        self.explosions = []
        self.game_over = False
        self.winner = None
        self.waiting_for_step = False

    def get_simulated_state(self):
        grid = [row[:] for row in self.map.grid]
        p1_pos = self.player1.get_grid_pos(self.offset_x, self.offset_y, self.map.display_tile_size)
        p2_pos = self.player2.get_grid_pos(self.offset_x, self.offset_y, self.map.display_tile_size)
        
        bombs = []
        for b in self.bombs:
            owner_id = 1 if b.owner == self.player1 else 2
            bombs.append([b.grid_pos[0], b.grid_pos[1], b.timer, owner_id])
            
        explosions = []
        for exp in self.explosions:
            for r, c, _ in exp.tiles:
                explosions.append([r, c, exp.timer])
                
        return SimulatedState(grid, p1_pos, p2_pos, bombs, explosions)

    def handle_input(self):
        if self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.reset_game()
            return None, None

        keys = pygame.key.get_pressed()
        p1_action = "IDLE"
        p2_action = "IDLE"

        # Step mode handling
        if self.mode == "STEP" and self.waiting_for_step:
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_RETURN:
                    self.waiting_for_step = False
                    break
            if self.waiting_for_step: return None, None

        # Player 1 Logic
        if self.agent1:
            if self.player1.x == self.player1.target_x and self.player1.y == self.player1.target_y:
                p1_action = self.agent1.get_action(self.get_simulated_state())
        else:
            if keys[pygame.K_a]: p1_action = "LEFT"
            elif keys[pygame.K_d]: p1_action = "RIGHT"
            elif keys[pygame.K_w]: p1_action = "UP"
            elif keys[pygame.K_s]: p1_action = "DOWN"
            if keys[pygame.K_SPACE]: p1_action = "BOMB"

        # Player 2 Logic
        if self.agent2:
            if self.player2.x == self.player2.target_x and self.player2.y == self.player2.target_y:
                p2_action = self.agent2.get_action(self.get_simulated_state())
        else:
            if keys[pygame.K_LEFT]: p2_action = "LEFT"
            elif keys[pygame.K_RIGHT]: p2_action = "RIGHT"
            elif keys[pygame.K_UP]: p2_action = "UP"
            elif keys[pygame.K_DOWN]: p2_action = "DOWN"
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]: p2_action = "BOMB"

        if self.mode == "STEP":
            self.waiting_for_step = True

        return p1_action, p2_action

    def _place_bomb(self, player):
        grid_pos = player.get_grid_pos(self.offset_x, self.offset_y, self.map.display_tile_size)
        r, c = grid_pos
        if not any(b.grid_pos == (r, c) for b in self.bombs):
            p_bombs = [b for b in self.bombs if b.owner == player]
            if len(p_bombs) < 1:
                new_bomb = Bomb(
                    self.offset_x + (c + 1) * self.map.display_tile_size,
                    self.offset_y + (r + 1) * self.map.display_tile_size,
                    (r, c),
                    self.spritesheet_path
                )
                new_bomb.owner = player
                new_bomb.players_inside.add(player)
                self.bombs.append(new_bomb)

    def update(self):
        # Cap dt para evitar que o tempo "pule" se a IA demorar (max 30 FPS logic speed)
        dt = min(self.clock.tick(60) / 1000.0, 0.033)
        p1_act, p2_act = self.handle_input()
        
        if self.game_over or (p1_act is None and p2_act is None):
            return

        if p1_act == "BOMB": self._place_bomb(self.player1)
        if p2_act == "BOMB": self._place_bomb(self.player2)

        self.player1.update(dt, self.map, self.offset_x, self.offset_y, self.bombs, p1_act, other_player=self.player2)
        self.player2.update(dt, self.map, self.offset_x, self.offset_y, self.bombs, p2_act, other_player=self.player1)
        
        for bomb in self.bombs[:]:
            bomb.update(dt)
            if bomb.exploded:
                self.explosions.append(Explosion(bomb.x, bomb.y, bomb.grid_pos, bomb.range, self.map))
                self.bombs.remove(bomb)
        
        for exp in self.explosions[:]:
            exp.update(dt)
            if exp.finished: self.explosions.remove(exp)

        self._check_death(self.player1)
        self._check_death(self.player2)

    def _check_death(self, player):
        if player.is_dead:
            if player.death_finished:
                self.game_over = True
                self.winner = "Player 2" if player == self.player1 else "Player 1"
            return
        r, c = player.get_grid_pos(self.offset_x, self.offset_y, self.map.display_tile_size)
        for exp in self.explosions:
            if any(tr == r and tc == c for tr, tc, _ in exp.tiles):
                player.is_dead = True
                player.current_anim = "death"
                player.frame_index = 0
                return
        
    def draw(self):
        self.screen.fill((50, 50, 50))
        self.map.draw(self.screen, self.offset_x, self.offset_y)
        for b in self.bombs: b.draw(self.screen)
        for e in self.explosions: e.draw(self.screen, self.offset_x, self.offset_y, self.map.display_tile_size)
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0,0))
            res = f"GAME OVER - {self.winner} WINS!" if self.winner else "GAME OVER"
            t1 = self.font.render(res, True, (255, 255, 255))
            t2 = self.font.render("Press 'R' to Restart", True, (200, 200, 200))
            self.screen.blit(t1, t1.get_rect(center=(self.width//2, self.height//2 - 20)))
            self.screen.blit(t2, t2.get_rect(center=(self.width//2, self.height//2 + 40)))
