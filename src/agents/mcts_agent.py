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
        self.prev_move = "IDLE"

    def get_action(self, state):
        start_time = time.perf_counter()
        safety_map = state.get_safety_map()
        my_pos = state.p1_pos if self.player_id == 1 else state.p2_pos
        opp_pos = state.p2_pos if self.player_id == 1 else state.p1_pos
        
        # 1. FUGA IMEDIATA: Se o tile atual for perigoso, foge pelo caminho MAIS SEGURO
        if safety_map[my_pos[0]][my_pos[1]] == 1:
            best_escape = self._find_best_aggressive_safe_move(state, my_pos, opp_pos, safety_map)
            if best_escape: 
                self.prev_move = best_escape
                return best_escape

        # 2. REGRAS DE CERCAMENTO E INDEPENDÊNCIA
        dist_to_opp = abs(my_pos[0] - opp_pos[0]) + abs(my_pos[1] - opp_pos[1])
        has_bomb = not any(b[3] == self.player_id for b in state.bombs)
        
        # Se estamos MUITO próximos (raio 2), MANDATÓRIO soltar bomba
        if dist_to_opp <= 2 and has_bomb:
            if state.has_escape_route(my_pos[0], my_pos[1], self.player_id):
                return "BOMB"

        # Se já estamos seguros e há bombas por perto
        is_danger_near = False
        for br, bc, _, _ in state.bombs:
            if abs(my_pos[0]-br) + abs(my_pos[1]-bc) <= 3: is_danger_near = True; break
        if not is_danger_near:
            for er, ec, _ in state.explosions:
                if abs(my_pos[0]-er) + abs(my_pos[1]-ec) <= 2: is_danger_near = True; break
        
        if is_danger_near and safety_map[my_pos[0]][my_pos[1]] == 0:
            # NOVO: Não podem se esconder no MESMO lugar.
            # Se o oponente está no mesmo tile ou adjacente, eu devo procurar OUTRO tile seguro
            if dist_to_opp <= 1:
                # Tenta se mover para outro tile que também seja seguro
                for mv, (dr, dc) in {"UP":(-1,0), "DOWN":(1,0), "LEFT":(0,-1), "RIGHT":(0,1)}.items():
                    nr, nc = my_pos[0]+dr, my_pos[1]+dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and state.grid[nr][nc] == 0 and safety_map[nr][nc] == 0:
                        # Verifica se esse movimento nos AFASTA do oponente
                        new_dist = abs(nr - opp_pos[0]) + abs(nc - opp_pos[1])
                        if new_dist > dist_to_opp:
                            return mv
            
            # Se não tiver pra onde ir sem se matar, ou já estiver longe o suficiente, fica parado.
            self.prev_move = "IDLE"
            return "IDLE"

        # 3. MCTS para Estratégia
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
            
            for _ in range(6):
                if state_sim.check_winner() is not None: break
                state_sim.apply_action(1, random.choice(state_sim.get_possible_actions(1)))
                state_sim.apply_action(2, random.choice(state_sim.get_possible_actions(2)))
                state_sim.step_time(0.5)
            
            result = self.evaluate_state(state_sim, my_pos)
            curr = node
            while curr is not None:
                reward = result if curr.player_id == 1 else -result
                curr.update(reward)
                curr = curr.parent

        if not root.children: return "IDLE"
        
        # Filtro final de estabilidade
        sorted_children = sorted(root.children, key=lambda c: (c.visits, c.move == self.prev_move), reverse=True)
        for child in sorted_children:
            temp_s = state.clone()
            temp_s.apply_action(self.player_id, child.move)
            new_p = temp_s.p1_pos if self.player_id == 1 else temp_s.p2_pos
            if safety_map[new_p[0]][new_p[1]] == 0:
                self.prev_move = child.move
                return child.move
        return "IDLE"

    def _find_best_aggressive_safe_move(self, state, start_pos, opp_pos, safety_map):
        queue, visited = [(start_pos, [])], {start_pos}
        best_move, min_dist = None, 999
        while queue:
            (r, c), path = queue.pop(0)
            if safety_map[r][c] == 0:
                d = abs(r - opp_pos[0]) + abs(c - opp_pos[1])
                if d < min_dist:
                    min_dist = d
                    best_move = path[0] if path else "IDLE"
            for mv, (dr, dc) in {"UP":(-1,0), "DOWN":(1,0), "LEFT":(0,-1), "RIGHT":(0,1)}.items():
                nr, nc = r+dr, c+dc
                if 0 <= nr < 8 and 0 <= nc < 8 and state.grid[nr][nc] == 0 and (nr, nc) not in visited:
                    if not any(b[0] == nr and b[1] == nc for b in state.bombs):
                        visited.add((nr, nc)); queue.append(((nr, nc), path + [mv]))
        return best_move

    def evaluate_state(self, state, initial_pos):
        winner = state.check_winner()
        if winner == 1: return 1.0
        if winner == 2: return -1.0
        p1r, p1c = state.p1_pos
        p2r, p2c = state.p2_pos
        p1_h = any(e[0] == p1r and e[1] == p1c for e in state.explosions)
        p2_h = any(e[0] == p2r and e[1] == p2c for e in state.explosions)
        if p1_h: return -1.0
        if p2_h: return 1.0
        def get_dist(start, target):
            q, v = [(start, 0)], {start}
            while q:
                (r, c), d = q.pop(0)
                if r == target[0] and c == target[1]: return d
                for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and state.grid[nr][nc] == 0 and (nr, nc) not in v:
                        v.add((nr, nc)); q.append(((nr, nc), d + 1))
            return 99
        dist = get_dist(state.p1_pos, state.p2_pos)
        return (16 - dist) / 25.0 if dist < 99 else 0
