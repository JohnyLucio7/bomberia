import json
import os

def save_match_record(record):
    os.makedirs("stats", exist_ok=True)
    with open("stats/history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
