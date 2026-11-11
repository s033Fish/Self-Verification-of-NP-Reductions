"""1-in-3-SAT: every clause has exactly one true variable (positive form)."""

from __future__ import annotations

import random
from collections.abc import Iterator

from .base import Instance, Problem
from .cnf_common import (
    enumerate_three_literal_formulas,
    formula_size,
    random_three_literal_formula,
    satisfiable,
    validate_three_literal_formula,
)


class OneInThreeSat(Problem):
    """1-in-3-SAT (positive one-in-three satisfiability).

    Instance: {"num_vars": m, "clauses": [[a, b, c], ...]}
      * Variables are 1..m.
      * Every clause lists exactly 3 different variables, all as positive
        integers: negated literals are not allowed in this problem.
      * Variable order inside a clause and clause order do not matter. The
        same clause may appear more than once.
      * Variables need not all appear in a clause.

    Yes iff some assignment of true/false to variables 1..m makes EXACTLY ONE
    of the three variables in every clause true.

    Edge cases: a formula with no clauses is yes, for any m, including
    m = 0. A formula with clauses needs m >= 3.
    """

    name = "1-in-3-SAT"
    # num_vars <= 5: every set of distinct clauses (1,045 formulas).
    exhaustive_scale = 5

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_three_literal_formula(instance, positive_only=True)

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        # Exactly one of a, b, c: at least one, and no two together.
        expanded = []
        for a, b, c in instance["clauses"]:
            expanded += [[a, b, c], [-a, -b], [-a, -c], [-b, -c]]
        return satisfiable(expanded)

    @classmethod
    def size(cls, instance: Instance) -> int:
        return formula_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = number of variables; 0.3 to 1.5 clauses per variable."""
        return random_three_literal_formula(rng, scale, (0.3, 1.5), positive_only=True)

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        return enumerate_three_literal_formulas(scale, positive_only=True)
