import json


def read_json_file(file_path):
    """Reads a JSON file and returns its contents as a dictionary."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
