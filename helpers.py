import json
import os
import sys

DATA_FILE = "data.json"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "history": [],
            "settings": {
                "theme": "Ruby",
                "quality": "Best",
                "download_path": os.getcwd(),
                "playlist": False
            }
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)