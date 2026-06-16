import json
from datetime import datetime

class MatchRecorder:
    def __init__(self, agent_names, source):
        self.agent_names = agent_names
        self.source = source
        self.start_time = datetime.now().isoformat()
        self.turns = 0
        self.decision_durations = {1: [], 2: []}
        self.bombs_count = {1: 0, 2: 0}
        self.blocks_destroyed_count = {1: 0, 2: 0}
        self.deaths_log = []
        self.player_distances = []
        self.suicides_count = {1: 0, 2: 0}

    def record_tick(self, distance=None):
        self.turns += 1
        if distance is not None:
            self.player_distances.append(distance)

    def record_decision(self, player_id, duration):
        self.decision_durations[player_id].append(duration)

    def record_bomb_placed(self, player_id):
        self.bombs_count[player_id] += 1

    def record_blocks_destroyed(self, player_id, count):
        self.blocks_destroyed_count[player_id] += count

    def record_death(self, victim_id, killer_id):
        self.deaths_log.append({"victim": victim_id, "killer": killer_id})
        if victim_id == killer_id:
            self.suicides_count[victim_id] += 1

    def get_final_payload(self, winner_side):
        avg_decision = {
            pid: (sum(durs) / len(durs)) if durs else 0 
            for pid, durs in self.decision_durations.items()
        }
        avg_dist = (sum(self.player_distances) / len(self.player_distances)) if self.player_distances else 0
        
        return {
            "timestamp": self.start_time,
            "source": self.source,
            "agents": list(self.agent_names),
            "winner": winner_side,
            "turns": self.turns,
            "avg_decision_time": avg_decision,
            "avg_distance": avg_dist,
            "bombs_placed": self.bombs_count,
            "blocks_destroyed": self.blocks_destroyed_count,
            "deaths": self.deaths_log,
            "suicides": self.suicides_count
        }
