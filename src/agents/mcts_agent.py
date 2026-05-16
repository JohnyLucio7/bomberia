import math
import random
import time
from src.agents.base_agent import BaseAgent

class MCTSNode:
    def __init__(self, state, parent=None, move=None, player_id=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.player_id = player_id 
        self.children = []
        self.wins = 0
        self.visits = 0
        self.next_player = 1 if player_id == 2 else 2
        self.untried_moves = state.get_possible_actions(self.next_player)

    def uct_select_child(self):
        log_v = math.log(self.visits)
        return sorted(self.children, key=lambda c: c.wins / c.visits + 1.41 * math.sqrt(log_v / c.visits))[-1]

    def add_child(self, move, state):
        n = MCTSNode(state=state, parent=self, move=move, player_id=self.next_player)
        self.untried_moves.remove(move)
        self.children.append(n)
        return n

    def update(self, result):
        self.visits += 1
        self.wins += result

class MCTSAgent(BaseAgent):
    def __init__(self, player_id, time_limit=0.015):
        super().__init__(player_id)
        self.time_limit = time_limit

    def get_action(self, state):
        start_time = time.perf_counter()
        safety_map = state.get_safety_map()
        my_pos = state.p1_pos if self.player_id == 1 else state.p2_pos
        
        # 1. SEGURANÇA MÁXIMA: Se estiver em perigo, foge direto (BFS)
        if safety_map[my_pos[0]][my_pos[1]] == 1:
            best_escape = self._find_nearest_safe_tile_move(state, my_pos, safety_map)
            if best_escape: return best_escape

        # 2. PACIÊNCIA ABSOLUTA: Se houver bombas/fogo e eu já estiver seguro, FICAR PARADO.
        has_danger = len(state.bombs) > 0 or len(state.explosions) > 0
        if has_danger and safety_map[my_pos[0]][my_pos[1]] == 0:
            return "IDLE"

        # 3. MCTS para decidir entre explodir bloco ou caçar inimigo
        root = MCTSNode(state=state, player_id=2 if self.player_id == 1 else 1)
        while time.perf_counter() - start_time < self.time_limit:
            node = root
            state_sim = state.clone()
            while node.untried_moves == [] and node.children != []:
                node = node.uct_select_child()
                state_sim.apply_action(node.player_id, node.move)
                if node.player_id == 2: state_sim.step_time(0.5)
            if node.untried_moves != []:
                m = random.choice(node.untried_moves)
                state_sim.apply_action(node.next_player, m)
                if node.next_player == 2: state_sim.step_time(0.5)
                node = node.add_child(m, state_sim.clone())
            
            # Rollout
            for _ in range(6):
                winner = state_sim.check_winner()
                if winner is not None: break
                state_sim.apply_action(1, random.choice(state_sim.get_possible_actions(1)))
                state_sim.apply_action(2, random.choice(state_sim.get_possible_actions(2)))
                state_sim.step_time(0.5)
            
            result = self.evaluate_state(state_sim)
            curr = node
            while curr is not None:
                reward = result if curr.player_id == 1 else -result
                curr.update(reward)
                curr = curr.parent

        if not root.children: return "IDLE"
        
        # Escolha final com filtro de segurança
        sorted_children = sorted(root.children, key=lambda c: c.visits, reverse=True)
        for child in sorted_children:
            temp_s = state.clone()
            temp_s.apply_action(self.player_id, child.move)
            new_p = temp_s.p1_pos if self.player_id == 1 else temp_s.p2_pos
            if safety_map[new_p[0]][new_p[1]] == 0:
                return child.move
        return sorted_children[0].move

    def _find_nearest_safe_tile_move(self, state, start_pos, safety_map):
        queue = [(start_pos, [])]
        visited = {start_pos}
        while queue:
            (r, c), path = queue.pop(0)
            if safety_map[r][c] == 0: return path[0] if path else "IDLE"
            for mv, (dr, dc) in {"UP":(-1,0), "DOWN":(1,0), "LEFT":(0,-1), "RIGHT":(0,1)}.items():
                nr, nc = r+dr, c+dc
                if 0 <= nr < 8 and 0 <= nc < 8 and state.grid[nr][nc] == 0 and (nr, nc) not in visited:
                    if not any(b[0] == nr and b[1] == nc for b in state.bombs):
                        visited.add((nr, nc)); queue.append(((nr, nc), path + [mv]))
        return None

    def evaluate_state(self, state):
        winner = state.check_winner()
        if winner == 1: return 1.0
        if winner == 2: return -1.0
        
        p1r, p1c = state.p1_pos
        p2r, p2c = state.p2_pos
        
        # Sobrevivência (Penalidade por fogo)
        p1_h = any(e[0] == p1r and e[1] == p1c for e in state.explosions)
        p2_h = any(e[0] == p2r and e[1] == p2c for e in state.explosions)
        if p1_h: return -0.99
        if p2_h: return 0.99

        # ESTRATÉGIA:
        # Se existe caminho livre até o inimigo -> Caçar inimigo
        # Se não existe -> Caçar bloco mais próximo
        def get_dist_to_target(start, target_type, s):
            q = [(start, 0)]
            v = {start}
            while q:
                (r, c), d = q.pop(0)
                if target_type == "OPP":
                    opp = s.p2_pos if self.player_id == 1 else s.p1_pos
                    if r == opp[0] and c == opp[1]: return d
                elif target_type == "BLOCK":
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < 8 and 0 <= nc < 8 and s.grid[nr][nc] == 2: return d
                
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and s.grid[nr][nc] == 0 and (nr, nc) not in v:
                        v.add((nr, nc)); q.append(((nr, nc), d + 1))
            return 99

        p1_to_p2 = get_dist_to_target(state.p1_pos, "OPP", state)
        p1_to_block = get_dist_to_target(state.p1_pos, "BLOCK", state)
        p2_to_p1 = get_dist_to_target(state.p2_pos, "OPP", state)
        p2_to_block = get_dist_to_target(state.p2_pos, "BLOCK", state)

        # Pontuação P1
        score1 = (16 - p1_to_p2) / 20.0 if p1_to_p2 < 99 else (16 - p1_to_block) / 40.0
        # Pontuação P2
        score2 = (16 - p2_to_p1) / 20.0 if p2_to_p1 < 99 else (16 - p2_to_block) / 40.0
        
        return score1 - score2
