import json
import os

APP_NAME = "GemYT"


def get_data_path():
    base = os.getenv("LOCALAPPDATA")  # Windows
    path = os.path.join(base, APP_NAME)

    if not os.path.exists(path):
        os.makedirs(path)

    return os.path.join(path, "data.json")


FILE = get_data_path()


def load_data():
    if not os.path.exists(FILE):
        return {"history": [], "settings": {}}

    with open(FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)