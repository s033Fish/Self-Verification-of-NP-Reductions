"""Fast exact deciders for the verifier: CNF encodings solved by CaDiCaL.

This module is NEVER bundled into a task's problems.py (make_task.py only
bundles the problem modules), so agents never see these encodings: the
3-colouring one is the gold answer to the three-coloring-to-sat task.
The library reaches it through base.fast_decide(), which returns None when
the module or python-sat is unavailable (as in an agent's sandbox), and the
library then falls back to its pure-Python search. Both give the same
answer; this one is just fast on large instances.
"""

from __future__ import annotations


def _solve(clauses: list[list[int]]) -> bool | None:
    try:
        from pysat.solvers import Solver
    except ImportError:
        return None
    if any(not clause for clause in clauses):
        return False
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        return bool(solver.solve())


def three_colourable(n: int, neighbours: list[list[int]]) -> bool | None:
    """One variable per (vertex, colour): exactly one colour per vertex, no
    edge inside a colour. Vertex 0 gets colour 0 (colours are symmetric)."""
    def var(v: int, c: int) -> int:
        return 3 * v + c + 1

    clauses = []
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])
        clauses += [[-var(v, a), -var(v, b)] for a, b in ((0, 1), (0, 2), (1, 2))]
        clauses += [[-var(v, c), -var(w, c)] for w in neighbours[v] if w > v for c in range(3)]
    if n:
        clauses.append([var(0, 0)])
    return _solve(clauses)


DECIDERS = {"three_colourable": three_colourable}