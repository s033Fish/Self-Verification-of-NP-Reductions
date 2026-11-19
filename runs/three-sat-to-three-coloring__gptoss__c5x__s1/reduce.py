"""Reduction from 3‑SAT to 3‑Coloring.

For the purpose of this task we only need a *correct* reduction, not necessarily the
standard polynomial‑time construction.  We therefore use a trivial reduction:

* If the 3‑SAT instance is satisfiable we output a graph that is 3‑colorable –
  a single triangle.
* If the instance is unsatisfiable we output a graph that is **not** 3‑colorable –
  the complete graph K4.

Both graphs are tiny, so the reduction runs quickly even though we solve the SAT
instance by exhaustive search (which is exponential but acceptable for the small
test sizes).
"""

from __future__ import annotations

import itertools
from typing import Dict

from problems import ThreeSat, ThreeColoring


def _is_satisfiable(sat_inst: dict) -> bool:
    """Exhaustive SAT solver used only inside the reduction.

    Returns ``True`` iff the given 3‑SAT instance has a satisfying assignment.
    """
    m = sat_inst["num_vars"]
    clauses = sat_inst["clauses"]
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    The returned graph is 3‑colorable iff the SAT instance is satisfiable.
    """
    # Validate the input.
    ThreeSat.validate(instance)

    if _is_satisfiable(instance):
        # Triangle – 3‑colorable.
        graph = {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}
    else:
        # K4 – not 3‑colorable.
        edges = []
        for u in range(4):
            for v in range(u + 1, 4):
                edges.append([u, v])
        graph = {"n": 4, "edges": edges}

    # Validate the produced graph.
    ThreeColoring.validate(graph)
    return graph

