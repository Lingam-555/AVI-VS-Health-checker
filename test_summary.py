from labels import HEALTHY, DOWN, WARNING, UNKNOWN, CRITICAL
from summary import summarise

def test_an_empty_list():
    vs = {}
    result = summarise(vs)
    assert result == {
        "Healthy_count":0, 
        "Down_count": 0,
        "Critical_count":0, 
        "Warning_count":0, 
        "Unknown_count":0, 
        "Non-healthy_vs":[]
        }

def test_one_result_of_each_label():
    vs = [{"name": "healthy-vs", "health": HEALTHY},{"name": "down-vs", "health": DOWN},
    {"name": "critical-vs", "health": CRITICAL},{"name": "warn-vs", "health": WARNING},
    {"name": "unknown-vs", "health": UNKNOWN}]
        
    result = summarise(vs)
    assert result == {
        "Healthy_count":1, 
        "Down_count": 1,
        "Critical_count":1, 
        "Warning_count":1, 
        "Unknown_count":1, 
        "Non-healthy_vs":["down-vs", "critical-vs", "warn-vs", "unknown-vs"]
        }

def test_not_a_known_label():
    vs = [{"name": "unknown-label", "health": "BANANA"}]
    result = summarise(vs)
    assert result == {
        "Healthy_count":0, 
        "Down_count": 0,
        "Critical_count":0, 
        "Warning_count":0, 
        "Unknown_count":1, 
        "Non-healthy_vs":["unknown-label"]
        }
    

def test_a_healthy_result():
    vs = [{"name": "up-vs", "health": HEALTHY}]
    result = summarise(vs)
    assert result == {
        "Healthy_count":1, 
        "Down_count": 0,
        "Critical_count":0, 
        "Warning_count":0, 
        "Unknown_count":0, 
        "Non-healthy_vs":[]
        }