"""Subset Sum."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem, require_int, require_keys
from .numbers_common import (
    bits,
    numbers_size,
    small_number_lists,
    subset_sum_reachable,
    validate_numbers,
)


class SubsetSum(Problem):
    """Subset Sum.

    Instance: {"numbers": [a1, a2, ...], "target": t}
      * The numbers are non-negative integers of any size; values may repeat.
      * The target is any integer.

    Yes iff some sub-list of the numbers (each position used at most once)
    sums to exactly t.

    Edge cases: t = 0 is always yes (the empty sub-list). t < 0 is always
    no. An empty list is yes only for t = 0.
    """

    name = "Subset Sum"
    # Lists of length <= 3 with values 0..3, every target 0..sum+1.
    exhaustive_scale = 3

    @classmethod
    def validate(cls, instance: object) -> None:
        require_keys(instance, {"numbers", "target"})
        assert isinstance(instance, dict)
        validate_numbers(instance["numbers"])
        require_int(instance["target"], "target")

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        return subset_sum_reachable(instance["numbers"], instance["target"])

    @classmethod
    def size(cls, instance: Instance) -> int:
        return numbers_size(instance["numbers"]) + bits(instance["target"])

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = how many numbers. Half the targets are the sum of a random
        sub-list (yes); the rest are random (usually no)."""
        numbers = [rng.randint(1, 50) for _ in range(scale)]
        if rng.random() < 0.5:
            target = sum(x for x in numbers if rng.random() < 0.5)
        else:
            target = rng.randint(0, sum(numbers) + 1)
        return {"numbers": numbers, "target": target}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        """Small values only (0..3): numbers are unbounded, so 'every
        instance' means every list and target in that range."""
        for numbers in small_number_lists(scale):
            for target in range(sum(numbers) + 2):
                yield {"numbers": numbers, "target": target}
