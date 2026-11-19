"""Reduction from 3‑SAT to Exact Cover.

The source problem is defined by ``ThreeSat`` (see ``problems.py``) with an
instance of the form ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where
each literal is a string ``"+v"`` (variable *v* should be true) or ``"-v"``
*(variable *v* should be false).  Every clause contains exactly three literals on
distinct variables.

The target problem is ``ExactCover`` with an instance ``{"universe_size": u,
"sets": [[e, ...], ...]}``.  The goal is to choose a collection of the given
sets that are pairwise disjoint and whose union is the whole universe ``0..u-1``.

The classic polynomial‑time reduction works as follows:

* For each variable ``x_i`` we create a *variable element* ``v_i`` (index
  ``i-1``).  Two sets are created for the variable – one representing the
  assignment ``x_i = True`` and one representing ``x_i = False``.  Both sets
  contain ``v_i`` so that exactly one of them must be chosen in any exact cover.

* For each clause ``C_j`` we create a *clause element`` ``c_j`` (index
  ``m + j``).  The clause element is added to the set of a literal that would
  satisfy the clause.  Consequently, covering ``c_j`` forces the selection of a
  literal that makes the clause true.

If the formula is satisfiable, picking for each variable the set that matches
the satisfying assignment covers every variable element and each clause
element exactly once.  Conversely, any exact cover yields a consistent truth
assignment (because each variable element appears in exactly two sets) that
covers all clause elements, hence satisfies the formula.

The reduction runs in time linear in the size of the 3‑SAT instance.
"""

from typing import List, Dict, Any


def _parse_literal(lit: str) -> (int, bool):
    """Return ``(var, sign)`` where ``sign`` is ``True`` for a positive literal.

    The literal format is ``"+v"`` or ``"-v"`` with ``v`` a positive integer.
    """
    if not lit:
        raise ValueError("Empty literal")
    sign = lit[0] == "+"
    var = int(lit[1:])
    return var, sign


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑literal lists).  Literals are strings ``"+v"``/``"-v"``.

    Returns
    -------
    dict
        An Exact Cover instance ``{"universe_size": u, "sets": [...]}`` that
        is a yes‑instance iff the given 3‑SAT instance is satisfiable.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[str]] = instance.get("clauses", [])

    # Edge case: no clauses – the formula is always satisfiable.
    # We can safely return an empty universe which is a trivial yes‑instance.
    if not clauses:
        return {"universe_size": 0, "sets": []}

    num_clauses = len(clauses)
    universe_size = m + num_clauses

    # Prepare two sets for each variable.
    true_sets: List[List[int]] = []
    false_sets: List[List[int]] = []
    for i in range(1, m + 1):
        var_elem = i - 1  # element representing variable i
        true_sets.append([var_elem])
        false_sets.append([var_elem])

    # Populate clause elements.
    for j, clause in enumerate(clauses):
        clause_elem = m + j
        for lit in clause:
            var, sign = _parse_literal(lit)
            if not (1 <= var <= m):
                continue
            if sign:
                true_sets[var - 1].append(clause_elem)
            else:
                false_sets[var - 1].append(clause_elem)

    # Combine all sets into a single list.
    sets: List[List[int]] = []
    for ts, fs in zip(true_sets, false_sets):
        sets.append(ts)
        sets.append(fs)

    return {"universe_size": universe_size, "sets": sets}

