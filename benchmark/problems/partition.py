"""Partition."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem, require_keys
from .numbers_common import (
    numbers_size,
    small_number_lists,
    subset_sum_reachable,
    validate_numbers,
)


class Partition(Problem):
    """Partition.

    Instance: {"numbers": [a1, a2, ...]}
      * The numbers are non-negative integers of any size; values may repeat.

    Yes iff the positions can be split into two groups whose numbers have
    equal sums (every position goes in exactly one group).

    Edge cases: an empty list is yes (two empty groups). An odd total is
    always no. Zeros never change the answer.
    """

    name = "Partition"
    # Lists of length <= 4 with values 0..3 (341 lists).
    exhaustive_scale = 4

    @classmethod
    def validate(cls, instance: object) -> None:
        require_keys(instance, {"numbers"})
        assert isinstance(instance, dict)
        validate_numbers(instance["numbers"])

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        total = sum(instance["numbers"])
        return total % 2 == 0 and subset_sum_reachable(instance["numbers"], total // 2)

    @classmethod
    def size(cls, instance: Instance) -> int:
        return numbers_size(instance["numbers"])

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = how many numbers. Half the draws are built from two halves
        with equal sums (yes); the rest are random."""
        if rng.random() < 0.5 and scale >= 2:
            left = [rng.randint(1, 30) for _ in range(scale // 2)]
            right = [rng.randint(1, 30) for _ in range(scale - scale // 2 - 1)]
            gap = sum(left) - sum(right)
            if gap > 0:
                right.append(gap)
            else:
                left.append(-gap)
            numbers = left + right
            rng.shuffle(numbers)
            return {"numbers": numbers}
        return {"numbers": [rng.randint(1, 30) for _ in range(scale)]}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        """Small values only (0..3), as numbers are unbounded."""
        for numbers in small_number_lists(scale):
            yield {"numbers": numbers}
