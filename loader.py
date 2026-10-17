import json
from exceptions import VSdataError

def load_vs_data(path:str) -> list:
    try:
        with open(path,"r") as file:
            data = json.load(file)
            virtual_services = data["virtual_services"]
            if not isinstance(virtual_services,list):
                raise VSdataError(f"{path}:'virtual_services' must be a list")
        return virtual_services
    except json.JSONDecodeError as e:
        raise VSdataError(f"Invalid JSON in {path}: {e}")
    except FileNotFoundError as e:
        raise VSdataError(f"SERVER File doesn't exist: {e}")
    except KeyError as e:
        raise VSdataError(f"Invalid Keyerror in {path}: {e}")