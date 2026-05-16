class SimulatedState:
    def __init__(self, grid, p1_pos, p2_pos, bombs=None, explosions=None):
        self.grid = [row[:] for row in grid]
        self.p1_pos = p1_pos 
        self.p2_pos = p2_pos 
        self.bombs = [list(b) for b in bombs] if bombs else []
        self.explosions = [list(e) for e in explosions] if explosions else []
        
    def clone(self):
        return SimulatedState(self.grid, self.p1_pos, self.p2_pos, self.bombs, self.explosions)

    def is_valid_pos(self, r, c, player_id=None, ignore_bombs=False):
        if not (0 <= r < 8 and 0 <= c < 8): return False
        if self.grid[r][c] in [1, 2]: return False
        
        # Body Blocking: O outro jogador é um obstáculo
        if player_id is not None:
            opp_pos = self.p2_pos if player_id == 1 else self.p1_pos
            if r == opp_pos[0] and c == opp_pos[1]:
                return False

        if not ignore_bombs:
            for br, bc, _, _ in self.bombs:
                if br == r and bc == c: return False
        return True

    def get_possible_actions(self, player_id):
        actions = ["IDLE"]
        r, c = self.p1_pos if player_id == 1 else self.p2_pos
        for move, (dr, dc) in {"UP":(-1,0), "DOWN":(1,0), "LEFT":(0,-1), "RIGHT":(0,1)}.items():
            if self.is_valid_pos(r + dr, c + dc, player_id=player_id): actions.append(move)
        
        has_bomb = any(b[3] == player_id for b in self.bombs)
        if not has_bomb:
            if self._will_bomb_hit_target(r, c, player_id) and self.has_escape_route(r, c, player_id):
                actions.append("BOMB")
        return actions

    def _will_bomb_hit_target(self, r, c, p_id):
        opp = self.p2_pos if p_id == 1 else self.p1_pos
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            for dist in range(1, 3):
                nr, nc = r + dr * dist, c + dc * dist
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if nr == opp[0] and nc == opp[1]: return True
                    if self.grid[nr][nc] == 2: return True
                    if self.grid[nr][nc] == 1: break 
                else: break
        return False

    def has_escape_route(self, r, c, p_id):
        temp_bombs = self.bombs + [[r, c, 2.5, 99]]
        s_map = self._calculate_safety_map(temp_bombs)
        q, v = [(r, c)], {(r, c)}
        opp_pos = self.p2_pos if p_id == 1 else self.p1_pos
        while q:
            cr, cc = q.pop(0)
            if s_map[cr][cc] == 0: return True
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = cr+dr, cc+dc
                if 0 <= nr < 8 and 0 <= nc < 8 and self.grid[nr][nc] == 0:
                    if nr == opp_pos[0] and nc == opp_pos[1]: continue # Body block
                    is_b = any(b[0] == nr and b[1] == nc for b in self.bombs)
                    if not is_b and (nr, nc) not in v:
                        v.add((nr, nc)); q.append((nr, nc))
        return False

    def get_safety_map(self):
        return self._calculate_safety_map(self.bombs)

    def _calculate_safety_map(self, bombs_to_check):
        s_map = [[0 for _ in range(8)] for _ in range(8)]
        for er, ec, _ in self.explosions:
            if 0 <= er < 8 and 0 <= ec < 8: s_map[er][ec] = 1
        for br, bc, _, _ in bombs_to_check:
            s_map[br][bc] = 1
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                for dist in range(1, 3):
                    nr, nc = br + dr * dist, bc + dc * dist
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        if self.grid[nr][nc] != 0: break
                        s_map[nr][nc] = 1
                    else: break
        return s_map

    def apply_action(self, p_id, action):
        if p_id == 1:
            r, c = self.p1_pos
            if action == "UP": self.p1_pos = (r-1, c)
            elif action == "DOWN": self.p1_pos = (r+1, c)
            elif action == "LEFT": self.p1_pos = (r, c-1)
            elif action == "RIGHT": self.p1_pos = (r, c+1)
            elif action == "BOMB": self.bombs.append([r, c, 2.5, 1])
        else:
            r, c = self.p2_pos
            if action == "UP": self.p2_pos = (r-1, c)
            elif action == "DOWN": self.p2_pos = (r+1, c)
            elif action == "LEFT": self.p2_pos = (r, c-1)
            elif action == "RIGHT": self.p2_pos = (r, c+1)
            elif action == "BOMB": self.bombs.append([r, c, 2.5, 2])

    def step_time(self, dt=0.5):
        new_b = []
        for b in self.bombs:
            b[2] -= dt
            if b[2] <= 0: self._explode(b[0], b[1])
            else: new_b.append(b)
        self.bombs = new_b
        new_e = []
        for e in self.explosions:
            e[2] -= dt
            if e[2] > 0: new_e.append(e)
        self.explosions = new_e

    def _explode(self, r, c):
        self.explosions.append([r, c, 0.5])
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            for dist in range(1, 3):
                nr, nc = r + dr * dist, c + dc * dist
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if self.grid[nr][nc] == 1: break
                    if self.grid[nr][nc] == 2:
                        self.grid[nr][nc] = 0
                        self.explosions.append([nr, nc, 0.5])
                        break
                    self.explosions.append([nr, nc, 0.5])
                else: break

    def check_winner(self):
        p1_h = any(e[0] == self.p1_pos[0] and e[1] == self.p1_pos[1] for e in self.explosions)
        p2_h = any(e[0] == self.p2_pos[0] and e[1] == self.p2_pos[1] for e in self.explosions)
        if p1_h and p2_h: return "DRAW"
        if p1_h: return 2
        if p2_h: return 1
        return None
