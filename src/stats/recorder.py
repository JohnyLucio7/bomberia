import json
import os
from datetime import datetime

class MatchRecorder:
    def __init__(self, agent_names, source):
        self.agent_names = agent_names
        self.source = source
        self.start_time = datetime.now().isoformat()
        self.turns = 0
        self.decisions = {1: [], 2: []}
        self.bombs_placed = {1: 0, 2: 0}
        self.blocks_destroyed = {1: 0, 2: 0}
        self.deaths = []
        self.distances = []
        self.suicides = {1: 0, 2: 0}

    def on_tick(self, distance=None):
        self.turns += 1
        if distance is not None:
            self.distances.append(distance)

    def on_decision(self, player_id, duration):
        self.decisions[player_id].append(duration)

    def on_bomb(self, player_id):
        self.bombs_placed[player_id] += 1

    def on_blocks(self, player_id, count):
        self.blocks_destroyed[player_id] += count

    def on_death(self, victim_id, killer_id):
        self.deaths.append({"victim": victim_id, "killer": killer_id})
        if victim_id == killer_id:
            self.suicides[victim_id] += 1

    def finalize(self, winner_side):
        avg_decision = {
            pid: (sum(dists) / len(dists)) if dists else 0 
            for pid, dists in self.decisions.items()
        }
        avg_dist = (sum(self.distances) / len(self.distances)) if self.distances else 0
        
        return {
            "timestamp": self.start_time,
            "source": self.source,
            "agents": list(self.agent_names),
            "winner": winner_side,
            "turns": self.turns,
            "avg_decision_time": avg_decision,
            "avg_distance": avg_dist,
            "bombs_placed": self.bombs_placed,
            "blocks_destroyed": self.blocks_destroyed,
            "deaths": self.deaths,
            "suicides": self.suicides
        }
