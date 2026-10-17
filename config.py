import json

def load_config(path:str) -> dict | None:
    try:
        with open(path,'r') as file:
            data = json.load(file)
            if not isinstance(data,dict):
                print("'data' must be a dict")
                return None
            return data
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        return None
    except FileNotFoundError as e:
        print(f"Data File doesn't exist: {e}")
        return None