import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = [
    ["notepad", "*.txt", "{text}"],
]

def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)

def load_config():
    ensure_config_exists()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
