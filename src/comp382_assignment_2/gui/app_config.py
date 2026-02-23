import json
import os

_GUI_DIR = os.path.dirname(__file__)


class AppConfig:
    def __init__(self):
        self.set_attributes_from_json(os.path.join(_GUI_DIR, "strings/en.json"))
        self.set_attributes_from_json(os.path.join(_GUI_DIR, "languages.json"))

        # Window dimensions
        self.window_width = 1400
        self.window_height = 900

    def set_attributes_from_json(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in data.items():
            setattr(self, key, value)
