import math
from src.agents.base_agent import BaseAgent

class MinimaxAgent(BaseAgent):
    def __init__(self, player_id, depth=2):
        super().__init__(player_id)
        self.depth = depth
        self.pos_history = []

    def get_action(self, state):
        safety_map = state.get_safety_map()
        my_pos = state.p1_pos if self.player_id == 1 else state.p2_pos

        # Camada reativa: fuga se em perigo
        if safety_map[my_pos[0]][my_pos[1]] == 1:
            queue, visited = [(my_pos, None)], {my_pos}
            while queue:
                (r, c), first_move = queue.pop(0)
                if safety_map[r][c] == 0:
                    return first_move if first_move else "IDLE"
                for mv, (dr, dc) in {"UP":(-1,0), "DOWN":(1,0), "LEFT":(0,-1), "RIGHT":(0,1)}.items():
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < state.rows and 0 <= nc < state.cols:
                        if state.grid[nr][nc] == 0 and (nr, nc) not in visited:
                            if not any(b[0] == nr and b[1] == nc for b in state.bombs):
                                visited.add((nr, nc))
                                queue.append(((nr, nc), first_move if first_move else mv))
            return "IDLE"

        # Se há bomba ativa próxima e estamos seguros, fica parado
        is_danger_near = any(
            abs(my_pos[0]-br) + abs(my_pos[1]-bc) <= 3
            for br, bc, _, _ in state.bombs
        ) or any(
            abs(my_pos[0]-er) + abs(my_pos[1]-ec) <= 2
            for er, ec, _ in state.explosions
    )
        if is_danger_near:
            return "IDLE"

        # Minimax para estratégia
        possible_actions = state.get_possible_actions(self.player_id)
        non_idle = [a for a in possible_actions if a != "IDLE" and a != "BOMB"]
        if non_idle:
            possible_actions = non_idle + (["BOMB"] if "BOMB" in possible_actions else [])
        if not possible_actions:
            return "IDLE"

        best_action = "IDLE"
        best_val = -math.inf

        my_pos = state.p1_pos if self.player_id == 1 else state.p2_pos

        for action in possible_actions:
            new_state = state.clone()
            new_state.apply_action(self.player_id, action)
            val = self.minimax(new_state, self.depth * 2 - 1, False, -math.inf, math.inf)

            new_pos = new_state.p1_pos if self.player_id == 1 else new_state.p2_pos
            if new_pos in self.pos_history:
                val -= 80

            if val > best_val:
                best_val = val
                best_action = action
            elif val == best_val and action != "IDLE" and best_action == "IDLE":
                best_action = action

        # Atualiza histórico (mantém só as últimas 2 posições)
        self.pos_history.append(my_pos)
        if len(self.pos_history) > 2:
            self.pos_history.pop(0)

        return best_action

    def minimax(self, state, depth, is_my_turn, alpha=-math.inf, beta=math.inf):
        winner = state.check_winner()
        if winner == self.player_id: return 1000 + depth
        if winner == "DRAW": return 0
        if winner is not None: return -1000 - depth

        if depth == 0:
            return self.evaluate(state)

        opp_id = 2 if self.player_id == 1 else 1

        if is_my_turn:
            max_eval = -math.inf
            for action in state.get_possible_actions(self.player_id):
                child = state.clone()
                child.apply_action(self.player_id, action)
                eval = self.minimax(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            for action in state.get_possible_actions(opp_id):
                child = state.clone()
                child.apply_action(opp_id, action)
                child.step_time(0.5)
                eval = self.minimax(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval

    def evaluate(self, state):
        score = 0
        my_r, my_c = state.p1_pos if self.player_id == 1 else state.p2_pos
        opp_r, opp_c = state.p2_pos if self.player_id == 1 else state.p1_pos
            
        def get_path_dist(start, target, grid, rows, cols):
            q, v = [(start, 0)], {start}
            while q:
                (r, c), d = q.pop(0)
                if (r, c) == target: return d
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr,nc) not in v:
                        v.add((nr,nc)); q.append(((nr,nc), d+1))
            return 99

        dist = get_path_dist((my_r, my_c), (opp_r, opp_c), state.grid, state.rows, state.cols)
        if dist == 99:
            dist = abs(my_r - opp_r) + abs(my_c - opp_c)
        score -= dist * 10

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = my_r+dr, my_c+dc
            if 0 <= nr < state.rows and 0 <= nc < state.cols:
                if state.grid[nr][nc] == 2:
                    score += 20

        def get_adj_blocks(r, c, state):
            count = 0
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < state.rows and 0 <= nc < state.cols and state.grid[nr][nc] == 2:
                    count += 1
            return count

        def get_danger_score(r, c, bombs, state):
            penalty = 0
            for br, bc, timer, owner in bombs:  # adiciona owner no unpack
                in_range = False
                if r == br and abs(c - bc) <= 2:
                    step = 1 if c > bc else -1
                    blocked = any(state.grid[br][bc + i*step] != 0 for i in range(1, abs(c-bc)))
                    if not blocked: in_range = True
                elif c == bc and abs(r - br) <= 2:
                    step = 1 if r > br else -1
                    blocked = any(state.grid[br + i*step][bc] != 0 for i in range(1, abs(r-br)))
                    if not blocked: in_range = True
                if in_range:
                    base = 500 / timer if timer > 1.0 else 10000 / (timer + 0.1)
                    # Penalidade extra para bomba própria -- prioridade máxima de fuga
                    if in_range:
                        penalty += 500 / timer if timer > 1.0 else 10000 / (timer + 0.1)
            return penalty

        score -= get_danger_score(my_r, my_c, state.bombs, state)
        score += get_danger_score(opp_r, opp_c, state.bombs, state)

        for br, bc, timer, owner in state.bombs:
            adj = get_adj_blocks(br, bc, state)
            if owner == self.player_id: score += adj * 300
            else: score -= adj * 300

        for er, ec, _ in state.explosions:
            if my_r == er and my_c == ec: score -= 10000
            if opp_r == er and opp_c == ec: score += 10000

        return score
