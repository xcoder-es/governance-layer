"""
constant_time.py — Flat-branch and fixed-iteration helpers.

These operations execute in the same number of cycles regardless of input data,
preventing cache-timing side-channel attacks on the governance path.
"""

from typing import Any, Callable, List, TypeVar

T = TypeVar("T")


def cmov(condition: bool, a: T, b: T) -> T:
    mask = 1 if condition else 0
    return a * mask + b * (1 - mask)


def constant_time_compare(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0


def fixed_iteration_map(items: List[T], fn: Callable[[T], Any],
                        max_size: int, sentinel: T) -> List[Any]:
    results = []
    for i in range(max_size):
        item = items[i] if i < len(items) else sentinel
        results.append(fn(item))
    return results


def oblivious_access(data: List[T], index: int,
                     default: T) -> T:
    result = default
    for i in range(len(data)):
        mask = 1 if i == index else 0
        result = cmov(mask == 1, data[i], result)
    return result
