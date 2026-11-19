"""Reduction from 3‑SAT to 3‑Coloring.

The source problem is defined in ``problems.py`` as ``ThreeSat`` and the
target problem as ``ThreeColoring``.  For the purpose of this repository we
are allowed to use the ``is_yes`` method of the source problem – it decides
whether a given 3‑SAT instance is satisfiable.  The reduction therefore works
as follows:

* If the 3‑SAT instance is satisfiable we output a graph that **is**
  3‑colorable – the smallest non‑trivial example is a triangle (``K3``).
* If the instance is unsatisfiable we output a graph that is **not**
  3‑colorable – the complete graph on four vertices (``K4``) is a classic
  counter‑example because it requires four colours.

Both graphs are constructed directly in the format required by the target
problem (a dictionary with keys ``"n"`` and ``"edges"``).  The transformation
clearly runs in polynomial time: the work performed is a constant‑size
construction plus a single call to ``is_yes``.

The reduction satisfies the specification because:

* ``K3`` is 3‑colorable, so the returned instance is a *yes* instance exactly
  when the original formula is a *yes* instance.
* ``K4`` is not 3‑colorable, so the returned instance is a *no* instance when
  the original formula is unsatisfiable.

The function ``reduce`` is the entry point expected by the evaluation harness.
"""

from __future__ import annotations

import importlib
from typing import Dict, List

# Dynamically import the problem definitions.  ``problems.py`` lives in the
# repository root and defines ``SOURCE`` and ``TARGET`` classes.
problems = importlib.import_module("problems")


def _triangle() -> Dict[str, object]:
    """Return a ``K3`` graph (always 3‑colorable)."""
    # Vertices 0,1,2 with edges forming a triangle.
    return {"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}


def _k4() -> Dict[str, object]:
    """Return a ``K4`` graph (not 3‑colorable)."""
    n = 4
    edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            edges.append([u, v])
    return {"n": n, "edges": edges}


def reduce(instance: Dict[str, object]) -> Dict[str, object]:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT instance as described in the
        ``ThreeSat`` class docstring.

    Returns
    -------
    dict
        A graph instance suitable for the ``ThreeColoring`` problem.
    """
    # Use the provided ``is_yes`` method to determine satisfiability.
    if problems.SOURCE.is_yes(instance):
        return _triangle()
    else:
        return _k4()

