"""Exact Cover."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem
from .sets_common import (
    enumerate_set_systems,
    masks,
    random_sets,
    set_system_size,
    validate_set_system,
)


class ExactCover(Problem):
    """Exact Cover.

    Instance: {"universe_size": u, "sets": [[element, ...], ...]}
      * The universe is the elements 0..u-1.
      * Each set lists distinct elements of the universe, in any order. A set
        may be empty, and the same set may appear more than once.

    Yes iff some of the sets contain every element of the universe exactly
    once: the chosen sets are pairwise disjoint and their union is the whole
    universe.

    Edge cases: u = 0 is yes (choose no sets). Empty sets never matter. Two
    copies of the same non-empty set can never both be chosen.
    """

    name = "Exact Cover"
    # Universe size <= 3: every collection of distinct subsets (278).
    exhaustive_scale = 3

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_set_system(instance, {"universe_size", "sets"})

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        return exact_cover_exists(instance["universe_size"], masks(instance["sets"]))

    @classmethod
    def size(cls, instance: Instance) -> int:
        return set_system_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = universe size. Half the draws plant a hidden exact cover
        among random sets, so yes-instances are not rare."""
        sets = random_sets(rng, scale, max_sets=2 * scale + 1)
        if rng.random() < 0.5 and scale > 0:
            elements = list(range(scale))
            rng.shuffle(elements)
            cuts = sorted(rng.sample(range(1, scale), rng.randint(0, scale - 1)))
            for start, end in zip([0, *cuts], [*cuts, scale]):
                sets.append(sorted(elements[start:end]))
            rng.shuffle(sets)
        return {"universe_size": scale, "sets": sets}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        for universe_size, sets in enumerate_set_systems(scale):
            yield {"universe_size": universe_size, "sets": sets}


def exact_cover_exists(universe_size: int, set_masks: list[int]) -> bool:
    """Backtracking (Knuth's Algorithm X without dancing links): cover the
    uncovered element with the fewest compatible sets first."""
    full = (1 << universe_size) - 1
    candidates = list({m for m in set_masks if m})

    def search(covered: int) -> bool:
        if covered == full:
            return True
        uncovered = full & ~covered
        best: list[int] | None = None
        for e in range(universe_size):
            if uncovered >> e & 1:
                options = [m for m in candidates if m >> e & 1 and not m & covered]
                if not options:
                    return False
                if best is None or len(options) < len(best):
                    best = options
        assert best is not None
        return any(search(covered | mask) for mask in best)

    return search(0)
