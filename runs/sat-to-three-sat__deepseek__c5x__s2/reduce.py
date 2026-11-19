"""Polynomial-time reduction from SAT to 3-SAT.

Source instance: {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance: {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

Construction (standard Tseitin-style clause splitting):

For each source clause C (after simplification):
  * Remove repeated literals.  If C contains both v and -v it is a
    tautology and can be dropped (it is always satisfied).
  * If C is empty, the whole formula is unsatisfiable; emit a fixed
    unsatisfiable 3-CNF over three variables.
  * |C| == 3: emit C directly (its literals are on 3 distinct vars).
  * |C| == 2: (l1 v l2) -> (l1 v l2 v a), (l1 v l2 v -a) with fresh a.
  * |C| == 1: (l1) -> the four clauses (l1 v +-a v +-b) with fresh a,b,
    which force l1 to be true.
  * |C| >= 4: introduce fresh z1..z_{k-3} and emit
        (l1 v l2 v z1)
        (-z1 v l3 v z2)
        ...
        (-z_{k-3} v l_{k-1} v l_k)
    which is equisatisfiable with C.

All fresh variables are new indices above m, so every emitted clause has
three literals on three different variables.  The reduction is linear in
the size of the input.
"""

from __future__ import annotations

from typing import Any


def _simplify_clause(clause: list[int]) -> list[int] | None:
    """Deduplicate a clause.  Return None if it is a tautology."""
    seen: set[int] = set()
    result: list[int] = []
    for literal in clause:
        if literal in seen:
            continue
        if -literal in seen:
            return None  # contains v and -v: always true
        seen.add(literal)
        result.append(literal)
    return result


def _unsatisfiable(num_vars: int) -> dict[str, Any]:
    """A fixed unsatisfiable 3-CNF: all 8 clauses over three variables."""
    n = max(num_vars, 3)
    clauses: list[list[int]] = []
    for a in (1, -1):
        for b in (2, -2):
            for c in (3, -3):
                clauses.append([a, b, c])
    return {"num_vars": n, "clauses": clauses}


def reduce(instance: dict[str, Any]) -> dict[str, Any]:
    num_vars = instance["num_vars"]
    source_clauses = instance["clauses"]

    simplified: list[list[int]] = []
    for clause in source_clauses:
        s = _simplify_clause(clause)
        if s is None:
            continue  # tautology: drop
        if len(s) == 0:
            return _unsatisfiable(num_vars)
        simplified.append(s)

    next_var = num_vars + 1

    def fresh() -> int:
        nonlocal next_var
        v = next_var
        next_var += 1
        return v

    out_clauses: list[list[int]] = []

    for s in simplified:
        k = len(s)
        if k == 3:
            out_clauses.append([s[0], s[1], s[2]])
        elif k == 2:
            l1, l2 = s
            a = fresh()
            out_clauses.append([l1, l2, a])
            out_clauses.append([l1, l2, -a])
        elif k == 1:
            l1 = s[0]
            a = fresh()
            b = fresh()
            out_clauses.append([l1, a, b])
            out_clauses.append([l1, -a, b])
            out_clauses.append([l1, a, -b])
            out_clauses.append([l1, -a, -b])
        else:  # k >= 4
            zs = [fresh() for _ in range(k - 3)]
            out_clauses.append([s[0], s[1], zs[0]])
            for i in range(1, k - 3):
                out_clauses.append([-zs[i - 1], s[i + 1], zs[i]])
            out_clauses.append([-zs[-1], s[k - 2], s[k - 1]])

    out_num_vars = (next_var - 1) if out_clauses else num_vars
    return {"num_vars": out_num_vars, "clauses": out_clauses}
