"""Data processing utilities for filtering and smoothing."""

from typing import List


def moving_average(values: List[float]) -> float:
    """Calculate the moving average of a list of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def rearrange_circular_buffer(new_value: float, buffer: List[float]) -> List[float]:
    """Add new value to circular buffer, removing oldest value."""
    buffer = buffer[1:] + [new_value]
    return buffer
