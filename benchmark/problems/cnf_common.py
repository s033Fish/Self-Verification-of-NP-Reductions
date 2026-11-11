"""Helpers shared by the satisfiability problems.

Formulas follow base.py: {"num_vars": m, "clauses": [[literal, ...], ...]}
with DIMACS-style literals over variables 1..m. The exact solver is the DPLL
search in three_sat.py.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from itertools import combinations, product

from .base import Instance, require, require_keys, validate_cnf
from .three_sat import _satisfiable


def satisfiable(clauses: list[list[int]]) -> bool:
    """Exact CNF satisfiability for any clause lengths."""
    return _satisfiable([frozenset(clause) for clause in clauses])


def validate_three_literal_formula(instance: object, positive_only: bool = False) -> None:
    """Exactly 3 literals per clause on 3 different variables."""
    require_keys(instance, {"num_vars", "clauses"})
    assert isinstance(instance, dict)
    validate_cnf(instance["clauses"], instance["num_vars"])
    for clause in instance["clauses"]:
        require(len(clause) == 3, f"clause {clause!r} must have exactly 3 literals")
        require(
            len({abs(literal) for literal in clause}) == 3,
            f"clause {clause!r} must use 3 different variables",
        )
        if positive_only:
            require(
                all(literal > 0 for literal in clause),
                f"clause {clause!r} must contain only positive literals",
            )


def formula_size(instance: Instance) -> int:
    return (
        instance["num_vars"]
        + len(instance["clauses"])
        + sum(len(clause) for clause in instance["clauses"])
    )


def three_literal_clauses(num_vars: int, positive_only: bool = False) -> list[list[int]]:
    """Every clause of 3 literals on 3 different variables, in a fixed order."""
    sign_choices = [(1, 1, 1)] if positive_only else list(product((1, -1), repeat=3))
    return [
        [sign * v for sign, v in zip(signs, variables)]
        for variables in combinations(range(1, num_vars + 1), 3)
        for signs in sign_choices
    ]


def enumerate_three_literal_formulas(
    scale: int, positive_only: bool = False
) -> Iterator[Instance]:
    """Every formula with num_vars <= scale whose clauses are distinct."""
    for num_vars in range(scale + 1):
        clauses = three_literal_clauses(num_vars, positive_only)
        for mask in range(1 << len(clauses)):
            yield {
                "num_vars": num_vars,
                "clauses": [c for i, c in enumerate(clauses) if mask >> i & 1],
            }


def random_three_literal_formula(
    rng: random.Random,
    num_vars: int,
    clauses_per_var: tuple[float, float],
    positive_only: bool = False,
) -> Instance:
    if num_vars < 3:
        return {"num_vars": num_vars, "clauses": []}
    low, high = clauses_per_var
    count = rng.randint(max(1, round(low * num_vars)), max(1, round(high * num_vars)))
    clauses = []
    for _ in range(count):
        variables = sorted(rng.sample(range(1, num_vars + 1), 3))
        if positive_only:
            clauses.append(variables)
        else:
            clauses.append([v if rng.random() < 0.5 else -v for v in variables])
    return {"num_vars": num_vars, "clauses": clauses}
