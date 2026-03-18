"""Tests for Sparktest."""
from src.core import Sparktest
def test_init(): assert Sparktest().get_stats()["ops"] == 0
def test_op(): c = Sparktest(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Sparktest(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Sparktest(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Sparktest(); r = c.process(); assert r["service"] == "sparktest"
