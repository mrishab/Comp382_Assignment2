import json
import os

class AppConfig:
    def __init__(self):
        # Loading strings
        json_path = os.path.join(os.path.dirname(__file__), 'strings/en.json')
        self.set_attributes_from_json(json_path)

        # JSON Overrides and configs
        self.window_width = 1000
        self.window_height = 600

    def set_attributes_from_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for key, value in data.items():
            setattr(self, key, value)