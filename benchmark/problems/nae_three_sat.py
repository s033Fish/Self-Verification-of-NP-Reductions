"""NAE-3-SAT: not-all-equal satisfiability with three literals per clause."""

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


class NaeThreeSat(Problem):
    """NAE-3-SAT (not-all-equal 3-SAT).

    Instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
      * Variables are 1..m. A literal is +v (v is true) or -v (v is false).
      * Every clause has exactly 3 literals on 3 different variables, so a
        clause may not repeat a variable or contain both v and -v.
      * Literal order inside a clause and clause order do not matter. The
        same clause may appear more than once.
      * Variables need not all appear in a clause.

    Yes iff some assignment of true/false to variables 1..m makes every
    clause contain at least one true literal AND at least one false literal
    (the three literals are not all equal).

    Edge cases: a formula with no clauses is yes, for any m, including
    m = 0. A formula with clauses needs m >= 3.
    """

    name = "NAE-3-SAT"
    # num_vars <= 3: every set of distinct clauses (259 formulas).
    exhaustive_scale = 3

    @classmethod
    def validate(cls, instance: object) -> None:
        validate_three_literal_formula(instance)

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        # Not all equal = at least one true (the clause) and at least one
        # false (the clause with every literal negated).
        expanded = []
        for clause in instance["clauses"]:
            expanded.append(clause)
            expanded.append([-literal for literal in clause])
        return satisfiable(expanded)

    @classmethod
    def size(cls, instance: Instance) -> int:
        return formula_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = number of variables; 1 to 5 clauses per variable."""
        return random_three_literal_formula(rng, scale, (1, 5))

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        return enumerate_three_literal_formulas(scale)
