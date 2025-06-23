import os, sys, types
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import PIL.ImageFont
PIL.ImageFont.truetype = lambda *a, **kw: None
# Stub visionModel module required by app.py
visionModel = types.ModuleType("visionModel")
visionModel.getPredictionJson = lambda *args, **kwargs: None
visionModel.getPredictionLabels = lambda *args, **kwargs: None
sys.modules["visionModel"] = visionModel

import pytest
from app import calculate_distance


def test_zero_distance():
    coord = (37.7749, -122.4194)
    assert calculate_distance(coord, coord) == pytest.approx(0.0, abs=1e-9)


def test_known_distance():
    coord1 = (0.0, 0.0)
    coord2 = (0.0, 1.0)  # 1 degree east at equator
    distance = calculate_distance(coord1, coord2)
    assert distance == pytest.approx(111194.9266, rel=1e-4)


