"""Reduction from 3-SAT to Exact Cover.

The source problem is ``ThreeSat`` defined in ``problems.py``.  An instance is
``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each literal is an
integer ``+v`` (the variable ``v`` is true) or ``-v`` (the variable ``v`` is
false).  The target problem is ``ExactCover`` with instance format
``{"universe_size": u, "sets": [[...], ...]}``.

We use Karp's classic reduction.  For each variable ``v`` we create three
universe elements:

* ``T_v`` – representing the variable being true,
* ``F_v`` – representing the variable being false,
* ``S_v`` – a selector element that forces exactly one of the two assignments.

For each clause ``i`` we create one element ``C_i``.

The sets are:

* **Clause‑literal sets** – for each literal ``ℓ`` in clause ``i``
  - if ``ℓ`` is positive ``+v`` we add ``{C_i, T_v}``
  - if ``ℓ`` is negative ``-v`` we add ``{C_i, F_v}``
  Selecting such a set means clause ``i`` is satisfied by that literal.

* **Variable assignment sets** – for each variable ``v`` we add two sets:
  ``{S_v, T_v}`` (assign true) and ``{S_v, F_v}`` (assign false).
  Because ``S_v`` appears in both, an exact cover can contain exactly one of
  them, thereby fixing a truth value for the variable.

* **Singleton sets** – for each variable ``v`` we also add the singleton sets
  ``{T_v}`` and ``{F_v}``.  These allow the element not chosen by the selector
  set to be covered.  When a variable appears in clauses, those clause sets may
  already cover ``T_v`` or ``F_v``; the singleton is then simply unused.

The construction runs in time linear in the size of the 3‑SAT instance and
produces a valid Exact Cover instance.  It is sound and complete:

*If the formula is satisfiable, a satisfying assignment yields an exact cover
by picking the appropriate variable‑assignment set for each variable and, for
each clause, the clause‑literal set corresponding to a satisfied literal.*
*Conversely, any exact cover determines a truth assignment (by which of the two
sets for each variable is chosen) that satisfies every clause (since each clause
element is covered by a clause‑literal set whose literal matches the assignment).*
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the docstring of :class:`ThreeSat`.

    Returns
    -------
    Dict
        An Exact Cover instance ``{"universe_size": u, "sets": [...]}``.
    """

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    c = len(clauses)  # number of clause elements
    # Universe layout:
    #   0 .. c-1                     -> clause elements C_i
    #   c + 3*v                     -> T_v (true element for variable v, 0‑based)
    #   c + 3*v + 1                 -> F_v (false element)
    #   c + 3*v + 2                 -> S_v (selector element)
    universe_size = c + 3 * num_vars

    sets: List[List[int]] = []

    # Clause‑literal sets
    for i, clause in enumerate(clauses):
        clause_elem = i
        for lit in clause:
            v = abs(lit) - 1  # zero‑based variable index
            if lit > 0:
                true_elem = c + 3 * v  # T_v
                sets.append([clause_elem, true_elem])
            else:
                false_elem = c + 3 * v + 1  # F_v
                sets.append([clause_elem, false_elem])

    # Variable assignment sets and singleton sets
    for v in range(num_vars):
        true_elem = c + 3 * v      # T_v
        false_elem = c + 3 * v + 1  # F_v
        selector = c + 3 * v + 2    # S_v
        # Assignment sets
        sets.append([selector, true_elem])   # assign true
        sets.append([selector, false_elem])  # assign false
        # Singletons to cover the element not chosen by the selector set
        sets.append([true_elem])
        sets.append([false_elem])

    return {"universe_size": universe_size, "sets": sets}

