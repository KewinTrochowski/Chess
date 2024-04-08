import json


def save_to_json(data):
    file = "db/settings.json"
    with open(file, 'w') as f:
        json.dump(data, f)
