from labels import HEALTHY, DOWN, CRITICAL, WARNING, UNKNOWN
from models import virtualservices

def classify_vs(vs: virtualservices,warning:int,critical:int) -> dict:
    name = vs.name
    status = vs.status
    latency = vs.latency_ms

    if status == "OPER_DOWN":
        return {"name": name, "health": DOWN, "reason": None}
    if status != "OPER_UP":
        return {"name": name, "health": UNKNOWN,
                "reason": f"unrecognised status: {status}"}

    try:
        if latency >= critical:
            health = CRITICAL
        elif latency >= warning:
            health = WARNING
        else:
            health = HEALTHY
    except TypeError:
        return {"name": name, "health": UNKNOWN,
                "reason": f"invalid latency_ms: {latency}"}

    return {"name": name, "health": health, "reason": None}