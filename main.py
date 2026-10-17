import os
import sys
from classifier import classify_vs
from summary import summarise
from config import load_config
from labels import UNKNOWN
from models import virtualservices
from exceptions import VSdataError
from client import AviHttpClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR,"config.json")

def main():
    settings = load_config(CONFIG_FILE)
    if settings is None:
        sys.exit(1)
    try:
        warning_threshold = settings["warning"]
        critical_threshold = settings["critical"]
        base_url = settings["url"]
        username = settings["username"]
        max_pages = settings["max_pages"]
    except KeyError as e:
        print(f"Invalid Key:{CONFIG_FILE} is missing the key {e}")
        sys.exit(1)
    list_result = []
    client = AviHttpClient(base_url,username,max_pages)
    try:
        client.login()
        vs_data = client.list_all_vs()
    except VSdataError as e:
        print(e)
        sys.exit(1)
    for entry in vs_data:
        try:
            vs = virtualservices(entry)
        except KeyError:
            health = {"name": entry.get("name"), "health": UNKNOWN}
        health = classify_vs(vs,warning_threshold,critical_threshold)
        list_result.append(health)
    result = summarise(list_result)
    healthy_count = result.get("Healthy_count")
    down_count = result.get("Down_count")
    critical = result.get("Critical_count")
    warning = result.get("Warning_count")
    unknown = result.get("Unknown_count")
    print(f"Healthy count : {healthy_count}")
    print(f"Down count: {down_count}")
    print(f"Critical count : {critical}")
    print(f"Warning count : {warning}")
    print(f"Unknown count : {unknown}")
    for non_healthy in result.get("Non-healthy_vs"):
        print(non_healthy)


if __name__== "__main__":
    main()