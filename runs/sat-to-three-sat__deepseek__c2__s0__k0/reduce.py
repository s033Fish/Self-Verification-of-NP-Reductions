"""Polynomial-time reduction from SAT to 3-SAT.

The source SAT instance may contain clauses of any length, including empty
clauses, repeated literals, and tautological clauses.  The target 3-SAT
instance must contain only clauses of exactly three literals on three
different variables.

The construction below is the standard equisatisfiable one:

* empty clause        -> a fixed unsatisfiable 3-SAT formula
* tautology          -> dropped (always true)
* unit clause        -> 4 clauses using 2 fresh variables
* 2-literal clause   -> 2 clauses using 1 fresh variable
* 3-literal clause   -> unchanged
* k-literal (k >= 4) -> k-2 clauses using k-3 fresh variables
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def _unsatisfiable_three_sat() -> Instance:
    """A small 3-SAT formula that is false under every assignment."""
    return {
        "num_vars": 3,
        "clauses": [
            [1, 2, 3],
            [1, 2, -3],
            [1, -2, 3],
            [1, -2, -3],
            [-1, 2, 3],
            [-1, 2, -3],
            [-1, -2, 3],
            [-1, -2, -3],
        ],
    }


def reduce(instance: Instance) -> Instance:
    """Return a 3-SAT instance satisfiable iff `instance` is satisfiable."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # First normalise each source clause: remove duplicate literals and
    # discard tautologies.  An empty clause is immediately unsatisfiable.
    normalised: list[list[int]] = []
    for clause in clauses:
        seen: set[int] = set()
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            seen.add(literal)
        if tautology:
            continue

        deduped: list[int] = []
        seen = set()
        for literal in clause:
            if literal not in seen:
                seen.add(literal)
                deduped.append(literal)

        if not deduped:
            # The source has an empty clause, so it is unsatisfiable.
            return _unsatisfiable_three_sat()

        normalised.append(deduped)

    next_var = num_vars + 1
    target_clauses: list[list[int]] = []

    for clause in normalised:
        length = len(clause)

        if length == 1:
            # (l) is equivalent to the conjunction of all four clauses
            # (l v a v b), (l v a v -b), (l v -a v b), (l v -a v -b).
            literal = clause[0]
            a = next_var
            b = next_var + 1
            next_var += 2
            target_clauses.append([literal, a, b])
            target_clauses.append([literal, a, -b])
            target_clauses.append([literal, -a, b])
            target_clauses.append([literal, -a, -b])

        elif length == 2:
            # (l1 v l2) is equivalent to
            # (l1 v l2 v a) and (l1 v l2 v -a).
            l1, l2 = clause
            a = next_var
            next_var += 1
            target_clauses.append([l1, l2, a])
            target_clauses.append([l1, l2, -a])

        elif length == 3:
            # Already a valid 3-SAT clause: after de-duplication and
            # tautology removal its three literals use three variables.
            target_clauses.append([clause[0], clause[1], clause[2]])

        else:
            # Chain construction for a clause with k >= 4 literals:
            #   (l1 v l2 v y1)
            #   (-y1 v l3 v y2)
            #   ...
            #   (-y_{k-3} v l_{k-1} v l_k)
            # This is satisfiable iff the original clause is satisfiable.
            aux = list(range(next_var, next_var + length - 3))
            next_var += length - 3

            target_clauses.append([clause[0], clause[1], aux[0]])
            for i in range(1, length - 3):
                target_clauses.append([-aux[i - 1], clause[i + 1], aux[i]])
            target_clauses.append([-aux[-1], clause[length - 2], clause[length - 1]])

    return {"num_vars": next_var - 1, "clauses": target_clauses}
