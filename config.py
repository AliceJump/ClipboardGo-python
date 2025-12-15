import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = [
  ["notepad", "*.txt", "{text}"],
  [
    "C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE",
    "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+)",
    "/c ipm.note /m {text}"
  ],
  [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    r"((?:https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)",
    "{text}"
  ]
]

def ensure_config_exists():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)

def load_config():
    try:
        ensure_config_exists()
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError as e:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        return load_config()