import json


def save_to_json(data,session):
    file = f"db/{session}/settings.json"
    with open(file, 'w') as f:
        json.dump(data, f)
