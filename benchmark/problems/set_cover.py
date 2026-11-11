"""Set Cover."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem, require_int
from .sets_common import (
    enumerate_set_systems,
    masks,
    random_sets,
    set_system_size,
    validate_set_system,
)


class SetCover(Problem):
    """Set Cover.

    Instance: {"universe_size": u, "sets": [[element, ...], ...], "k": k}
      * The universe is the elements 0..u-1.
      * Each set lists distinct elements of the universe, in any order. A set
        may be empty, and the same set may appear more than once.
      * k is any integer.

    Yes iff AT MOST k of the sets together contain every element of the
    universe.

    Edge cases: k < 0 is always no. u = 0 is yes for every k >= 0 (choosing
    no sets covers the empty universe). If some element is in no set, the
    answer is no.
    """

    name = "Set Cover"
    # Universe size <= 3: every collection of distinct subsets, every k from
    # 0 to the number of sets.
    exhaustive_scale = 3

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_set_system(instance, {"universe_size", "sets", "k"})
        assert isinstance(instance, dict)
        require_int(instance["k"], "k")

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        k = instance["k"]
        if k < 0:
            return False
        minimum = min_set_cover(instance["universe_size"], masks(instance["sets"]))
        return minimum is not None and minimum <= k

    @classmethod
    def size(cls, instance: Instance) -> int:
        return set_system_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = universe size."""
        sets = random_sets(rng, scale, max_sets=2 * scale + 1)
        return {"universe_size": scale, "sets": sets, "k": rng.randint(0, len(sets))}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        for universe_size, sets in enumerate_set_systems(scale):
            for k in range(len(sets) + 1):
                yield {"universe_size": universe_size, "sets": sets, "k": k}


def min_set_cover(universe_size: int, set_masks: list[int]) -> int | None:
    """Smallest number of sets covering the universe, or None if impossible.
    Branch and bound: some set containing the uncovered element with the
    fewest options must be chosen."""
    full = (1 << universe_size) - 1
    candidates = sorted({m for m in set_masks if m}, key=lambda m: -m.bit_count())
    union = 0
    for mask in candidates:
        union |= mask
    if union != full:
        return None
    best = len(candidates)

    def search(covered: int, used: int) -> None:
        nonlocal best
        if covered == full:
            best = min(best, used)
            return
        if used + 1 >= best:
            return
        uncovered = full & ~covered
        element, options = -1, []
        for e in range(universe_size):
            if uncovered >> e & 1:
                containing = [m for m in candidates if m >> e & 1]
                if element == -1 or len(containing) < len(options):
                    element, options = e, containing
        options.sort(key=lambda m: -(m & ~covered).bit_count())
        for mask in options:
            search(covered | mask, used + 1)

    search(0, 0)
    return best
