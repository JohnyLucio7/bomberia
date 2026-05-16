import math
from src.agents.base_agent import BaseAgent

class MinimaxAgent(BaseAgent):
    def __init__(self, player_id, depth=2):
        super().__init__(player_id)
        self.depth = depth

    def get_action(self, state):
        best_action = "IDLE"
        
        possible_actions = state.get_possible_actions(self.player_id)
        if not possible_actions:
            return "IDLE"
            
        if self.player_id == 1: # Maximizing
            best_val = -math.inf
            for action in possible_actions:
                new_state = state.clone()
                new_state.apply_action(1, action)
                val = self.minimax(new_state, self.depth * 2 - 1, False)
                # print(f"P1 Action {action}: {val}") # Debug
                if val > best_val:
                    best_val = val
                    best_action = action
                elif val == best_val and action != "IDLE" and best_action == "IDLE":
                    best_action = action
        else: # Minimizing
            best_val = math.inf
            for action in possible_actions:
                new_state = state.clone()
                new_state.apply_action(2, action)
                val = self.minimax(new_state, self.depth * 2 - 1, True)
                # print(f"P2 Action {action}: {val}") # Debug
                if val < best_val:
                    best_val = val
                    best_action = action
                elif val == best_val and action != "IDLE" and best_action == "IDLE":
                    best_action = action
                    
        return best_action

    def minimax(self, state, depth, is_maximizing, alpha=-math.inf, beta=math.inf):
        winner = state.check_winner()
        if winner == 1: return 1000 + depth
        if winner == 2: return -1000 - depth
        if winner == "DRAW": return 0
        
        if depth == 0:
            return self.evaluate(state)
        
        if is_maximizing:
            max_eval = -math.inf
            actions = state.get_possible_actions(1)
            for action in actions:
                child = state.clone()
                child.apply_action(1, action)
                eval = self.minimax(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            actions = state.get_possible_actions(2)
            for action in actions:
                child = state.clone()
                child.apply_action(2, action)
                child.step_time(1.0)
                eval = self.minimax(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha: break
            return min_eval

    def evaluate(self, state):
        score = 0
        p1r, p1c = state.p1_pos
        p2r, p2c = state.p2_pos

        # 1. Distância Manhattan (Suave, para não dominar a segurança)
        dist = abs(p1r - p2r) + abs(p1c - p2c)
        score -= dist * 5

        def get_adj_blocks(r, c, grid):
            count = 0
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and grid[nr][nc] == 2:
                    count += 1
            return count

        # 2. Segurança Contra Bombas (Aprimorada)
        def get_danger_score(r, c, bombs, grid):
            penalty = 0
            for br, bc, timer, _ in bombs:
                in_range = False
                if r == br and abs(c - bc) <= 2:
                    step = 1 if c > bc else -1
                    blocked = False
                    for i in range(1, abs(c - bc)):
                        if grid[br][bc + i * step] != 0:
                            blocked = True; break
                    if not blocked: in_range = True
                elif c == bc and abs(r - br) <= 2:
                    step = 1 if r > br else -1
                    blocked = False
                    for i in range(1, abs(r - br)):
                        if grid[br + i * step][bc] != 0:
                            blocked = True; break
                    if not blocked: in_range = True

                if in_range:
                    # Penalidade agora é menor quando a bomba acabou de ser plantada (timer=3.0)
                    # Mas explode (penalidade gigante) se o timer estiver perto de 0
                    if timer > 1.0:
                        penalty += 100 / timer # Penalidade moderada, permite planejar
                    else:
                        penalty += 5000 / (timer + 0.1) # Pânico total
            return penalty

        score -= get_danger_score(p1r, p1c, state.bombs, state.grid)
        score += get_danger_score(p2r, p2c, state.bombs, state.grid)

        # 3. Recompensa por Bombas "Úteis" (Muito maior para vencer o medo inicial)
        for br, bc, timer, owner in state.bombs:
            adj = get_adj_blocks(br, bc, state.grid)
            if owner == 1: score += adj * 300 # Aumentado significativamente
            else: score -= adj * 300

        # 4. Recompensa por blocos destruídos (Estado futuro)
        # O Minimax agora verá que após o step_time, se o bloco sumiu, o score melhora
        # Mas como o grid muda, precisamos de uma forma de valorizar o "vazio" onde antes tinha bloco
        # Por enquanto, o bônus de adj_blocks já ajuda.

        # 5. Sobrevivência em explosões ativas
        for er, ec, _ in state.explosions:
            if p1r == er and p1c == ec: score -= 10000
            if p2r == er and p2c == ec: score += 10000

        return score
