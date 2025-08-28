"""Utility functions for geometric calculations."""

from math import hypot
from typing import Tuple


def midpoint(p1, p2) -> Tuple[int, int]:
    """Calculate the midpoint between two points."""
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)


def calculate_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two points."""
    return hypot(point1[0] - point2[0], point1[1] - point2[1])
