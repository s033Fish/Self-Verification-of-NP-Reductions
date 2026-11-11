"""Helpers shared by the set-system problems.

Instance shape: {"universe_size": u, "sets": [[element, ...], ...], ...}.
Elements are 0..u-1. Each set lists distinct elements in any order; a set may
be empty, and the same set may appear more than once in the collection.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from itertools import combinations

from .base import Instance, is_int, require, require_int, require_keys


def validate_set_system(instance: object, keys: set[str]) -> None:
    require_keys(instance, keys)
    assert isinstance(instance, dict)
    universe_size = instance["universe_size"]
    require_int(universe_size, "universe_size", minimum=0)
    sets = instance["sets"]
    require(isinstance(sets, list), "sets must be a list")
    for subset in sets:
        require(isinstance(subset, list), f"each set must be a list, got {subset!r}")
        for element in subset:
            require(is_int(element), f"elements must be ints, got {element!r}")
            require(
                0 <= element < universe_size,
                f"element {element} is outside 0..{universe_size - 1}",
            )
        require(len(set(subset)) == len(subset), f"set {subset!r} repeats an element")


def set_system_size(instance: Instance) -> int:
    return (
        instance["universe_size"]
        + len(instance["sets"])
        + sum(len(subset) for subset in instance["sets"])
    )


def masks(sets: list[list[int]]) -> list[int]:
    result = []
    for subset in sets:
        mask = 0
        for element in subset:
            mask |= 1 << element
        result.append(mask)
    return result


def enumerate_set_systems(scale: int) -> Iterator[tuple[int, list[list[int]]]]:
    """Every collection of distinct subsets of a universe of size <= scale.
    There are 2^(2^u) collections: 256 at u = 3, 65,536 at u = 4."""
    for universe_size in range(scale + 1):
        all_subsets = [
            list(subset)
            for size in range(universe_size + 1)
            for subset in combinations(range(universe_size), size)
        ]
        for mask in range(1 << len(all_subsets)):
            yield universe_size, [
                s for i, s in enumerate(all_subsets) if mask >> i & 1
            ]


def random_sets(rng: random.Random, universe_size: int, max_sets: int) -> list[list[int]]:
    density = rng.uniform(0.15, 0.6)
    return [
        [e for e in range(universe_size) if rng.random() < density]
        for _ in range(rng.randint(1, max_sets))
    ]
