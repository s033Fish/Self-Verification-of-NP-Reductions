"""3-SAT: satisfiability of CNF formulas with exactly three literals per clause."""

from __future__ import annotations

import random
from collections.abc import Iterator
from itertools import combinations, product

from .base import Instance, Problem, require, require_keys, validate_cnf


class ThreeSat(Problem):
    """3-SAT.

    Instance: {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
      * Variables are 1..m. A literal is +v (v is true) or -v (v is false).
      * Every clause has exactly 3 literals on 3 different variables, so a
        clause may not repeat a variable or contain both v and -v.
      * Literal order inside a clause and clause order do not matter. The
        same clause may appear more than once.
      * Variables need not all appear in a clause.

    Yes iff some assignment of true/false to variables 1..m makes every
    clause contain at least one true literal.

    Edge cases: a formula with no clauses is satisfiable (yes), for any m,
    including m = 0. A formula with clauses needs m >= 3.
    """

    name = "3-SAT"
    # num_vars <= 3: every set of distinct clauses (259 formulas). Only one is
    # unsatisfiable (all 8 clauses on 3 variables), so random_instance is what
    # supplies most no-instances; test reductions with both.
    exhaustive_scale = 3

    @classmethod
    def validate(cls, instance: object) -> None:
        require_keys(instance, {"num_vars", "clauses"})
        assert isinstance(instance, dict)
        validate_cnf(instance["clauses"], instance["num_vars"])
        for clause in instance["clauses"]:
            require(len(clause) == 3, f"clause {clause!r} must have exactly 3 literals")
            require(
                len({abs(literal) for literal in clause}) == 3,
                f"clause {clause!r} must use 3 different variables",
            )

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        return _satisfiable([frozenset(clause) for clause in instance["clauses"]])

    @classmethod
    def size(cls, instance: Instance) -> int:
        return instance["num_vars"] + 3 * len(instance["clauses"])

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = number of variables. The clause count is drawn from 2 to 10
        per variable, which gives roughly half satisfiable formulas for 3 to 8
        variables. (Small formulas need more clauses per variable to become
        unsatisfiable than the asymptotic threshold of about 4.3.)"""
        if scale < 3:
            return {"num_vars": scale, "clauses": []}
        clauses = []
        for _ in range(rng.randint(2 * scale, 10 * scale)):
            variables = rng.sample(range(1, scale + 1), 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in sorted(variables)])
        return {"num_vars": scale, "clauses": clauses}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        """Every formula with num_vars <= scale whose clauses are distinct.
        The count grows as 2^(8 * C(m, 3)): 256 formulas at m = 3, but about
        4 billion at m = 4, so keep scale at 3."""
        for num_vars in range(scale + 1):
            all_clauses = [
                [sign * v for sign, v in zip(signs, variables)]
                for variables in combinations(range(1, num_vars + 1), 3)
                for signs in product((1, -1), repeat=3)
            ]
            for mask in range(1 << len(all_clauses)):
                yield {
                    "num_vars": num_vars,
                    "clauses": [
                        clause for index, clause in enumerate(all_clauses)
                        if mask >> index & 1
                    ],
                }


def _satisfiable(clauses: list[frozenset[int]]) -> bool:
    """Exact DPLL search: unit propagation plus branching. Exponential in the
    worst case, but far faster than trying all 2^m assignments, which matters
    when 3-SAT is the target of a reduction and instances get large."""
    while True:
        if not clauses:
            return True
        if any(not clause for clause in clauses):
            return False
        unit = next((clause for clause in clauses if len(clause) == 1), None)
        if unit is None:
            break
        clauses = _assign(clauses, next(iter(unit)))
    literal = next(iter(min(clauses, key=len)))
    return _satisfiable(_assign(clauses, literal)) or _satisfiable(
        _assign(clauses, -literal)
    )


def _assign(clauses: list[frozenset[int]], literal: int) -> list[frozenset[int]]:
    """Make `literal` true: drop satisfied clauses, remove its negation."""
    return [clause - {-literal} for clause in clauses if literal not in clause]
