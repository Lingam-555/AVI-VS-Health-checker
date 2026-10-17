from dataclasses import dataclass

@dataclass
class VirtualService:
    name: str
    status : str
    latency_ms : int

def virtualservices(virtual_services: dict) -> VirtualService:

    vs = VirtualService(name = virtual_services["name"], status = virtual_services["status"], latency_ms = virtual_services["latency_ms"])
    return vs
