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
        sub-list (yes); 3 in 10 are random from 0 to sum + 1 (usually no);
        1 in 10 are negative; 1 in 10 are a power of two above the sum plus
        a reachable sum (no, but with the low bits of a yes)."""
        numbers = [rng.randint(1, 50) for _ in range(scale)]
        total = sum(numbers)
        roll = rng.random()
        if roll < 0.5:
            target = sum(x for x in numbers if rng.random() < 0.5)
        elif roll < 0.8:
            target = rng.randint(0, total + 1)
        elif roll < 0.9:
            target = -rng.randint(1, total + 2)
        else:
            reachable = sum(x for x in numbers if rng.random() < 0.5)
            target = (1 << (total.bit_length() + rng.randint(1, 3))) + reachable
        return {"numbers": numbers, "target": target}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        """Small values only (0..3): numbers are unbounded, so 'every
        instance' means every list with every target from 0 to sum + 1, plus
        targets outside that range that the spec allows: two negative ones,
        and three above the sum (one of them a power of two above the sum,
        and one that adds 1 to it, which share their low bits with small
        reachable sums: they catch reductions that drop high bits)."""
        for numbers in small_number_lists(scale):
            total = sum(numbers)
            high = 1 << (total.bit_length() + 1)
            targets = list(range(total + 2)) + [-1, -(total + 2), 2 * (total + 2), high, high + 1]
            for target in dict.fromkeys(targets):  # no repeats, order kept
                yield {"numbers": numbers, "target": target}