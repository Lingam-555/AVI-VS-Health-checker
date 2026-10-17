from models import VirtualService
from classifier import classify_vs
from labels import HEALTHY, DOWN, CRITICAL, WARNING, UNKNOWN

def test_just_below_warning_limit_is_healthy():
    vs = VirtualService(name = "warn-vs", status = "OPER_UP", latency_ms=120)
    result = classify_vs(vs, 200, 500)
    assert result["health"] == HEALTHY

def test_exactly_at_warning_limit():
    vs = VirtualService(name = "warn-vs", status = "OPER_UP", latency_ms=200)
    result = classify_vs(vs, 200, 500)
    assert result["health"] == WARNING

def test_just_below_critical_limit_is_warning():
    vs = VirtualService(name = "warn-vs", status = "OPER_UP", latency_ms=499)
    result = classify_vs(vs, 200, 500)
    assert result["health"] == WARNING

def test_exactly_at_critical_limit():
    vs = VirtualService(name = "critical-vs", status = "OPER_UP", latency_ms=500)
    result = classify_vs(vs, 200, 500)
    assert result["health"] == CRITICAL

def test_oper_down_is_down():
    vs = VirtualService(name = "down-vs", status = "OPER_DOWN", latency_ms=120)
    result = classify_vs(vs, 200, 500)
    assert result["health"] == DOWN

def test_unrecognised_status_is_unknown():
    vs = VirtualService(name = "unknown-vs", status = "INVALID", latency_ms=120)
    result = classify_vs(vs, 200, 500)
    assert result["health"] == UNKNOWN

def test_text_latency_is_unknown():
    vs = VirtualService(name = "unknown-vs", status = "OPER_UP", latency_ms="abc")
    result = classify_vs(vs, 200, 500)
    assert result["health"] == UNKNOWN
