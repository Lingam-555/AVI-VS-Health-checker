from labels import HEALTHY, DOWN, CRITICAL, WARNING, UNKNOWN

def summarise(results: list) -> dict:
    healthy_count = 0
    down_count = 0
    critical_count = 0
    warning_count = 0
    unknown_count = 0
    non_healthy_vs = []

    for result in results:
        
        name = result.get("name")
        health = result.get("health")

        if health == CRITICAL:
            critical_count += 1
            non_healthy_vs.append(name)
        elif health == WARNING:
            warning_count += 1
            non_healthy_vs.append(name)
        elif health == UNKNOWN:
            unknown_count += 1
            non_healthy_vs.append(name)
        elif health == DOWN:
            down_count += 1
            non_healthy_vs.append(name)
        elif health == HEALTHY:
            healthy_count += 1
        else:
            unknown_count += 1
            non_healthy_vs.append(name)

    res = {
        "Healthy_count":healthy_count, 
        "Down_count": down_count,
        "Critical_count":critical_count, 
        "Warning_count":warning_count, 
        "Unknown_count":unknown_count, 
        "Non-healthy_vs":non_healthy_vs
        }

    return res