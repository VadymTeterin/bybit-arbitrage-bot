import json

def save_cache_to_disk(cache_dict, filename="symbols_cache.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cache_dict, f)

def load_cache_from_disk(filename="symbols_cache.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
