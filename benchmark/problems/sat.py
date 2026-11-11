"""SAT: satisfiability of CNF formulas with clauses of any length."""

from __future__ import annotations

import random
from collections.abc import Iterator
from itertools import product

from .base import Instance, Problem, require_keys, validate_cnf
from .cnf_common import formula_size, satisfiable


class Sat(Problem):
    """SAT (CNF satisfiability).

    Instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
      * Variables are 1..m. A literal is +v (v is true) or -v (v is false).
      * A clause is a list of any number of literals, including none.
        Literals may repeat, and a clause may contain both v and -v.
      * Literal order inside a clause and clause order do not matter. The
        same clause may appear more than once.
      * Variables need not all appear in a clause.

    Yes iff some assignment of true/false to variables 1..m makes every
    clause contain at least one true literal.

    Edge cases: a formula with no clauses is satisfiable (yes). An empty
    clause [] can never be satisfied, so any formula containing one is no.
    """

    name = "SAT"
    # num_vars <= 2: every set of distinct clauses, where a clause uses each
    # variable at most once (522 formulas). num_vars = 3 would be 2^27.
    exhaustive_scale = 2

    @classmethod
    def validate(cls, instance: object) -> None:
        require_keys(instance, {"num_vars", "clauses"})
        assert isinstance(instance, dict)
        validate_cnf(instance["clauses"], instance["num_vars"])

    @classmethod
    def is_yes(cls, instance: Instance) -> bool:
        return satisfiable(instance["clauses"])

    @classmethod
    def size(cls, instance: Instance) -> int:
        return formula_size(instance)

    @classmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """scale = number of variables. Clause lengths are 1 to 4 (capped at
        the number of variables), and clause counts 1 to 4 per variable."""
        if scale == 0:
            return {"num_vars": 0, "clauses": rng.choice([[], [[]]])}
        clauses = []
        for _ in range(rng.randint(1, 4 * scale)):
            variables = rng.sample(range(1, scale + 1), rng.randint(1, min(4, scale)))
            clauses.append([v if rng.random() < 0.5 else -v for v in sorted(variables)])
        return {"num_vars": scale, "clauses": clauses}

    @classmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        """Every formula with num_vars <= scale whose clauses are distinct and
        use each variable at most once (3^m possible clauses, including [])."""
        for num_vars in range(scale + 1):
            all_clauses = [
                [sign * v for sign, v in zip(signs, range(1, num_vars + 1)) if sign]
                for signs in product((0, 1, -1), repeat=num_vars)
            ]
            for mask in range(1 << len(all_clauses)):
                yield {
                    "num_vars": num_vars,
                    "clauses": [c for i, c in enumerate(all_clauses) if mask >> i & 1],
                }
