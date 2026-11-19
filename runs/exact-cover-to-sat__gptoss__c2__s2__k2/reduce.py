"""Reduction from Exact Cover to SAT.

The source problem is *Exact Cover* with instances of the form::

    {"universe_size": u, "sets": [[element, ...], ...]}

The target problem is *SAT* (CNF) with instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Variables are numbered from ``1`` to ``m``.  A literal is represented by an
integer: a positive integer ``v`` denotes the literal ``+v`` (variable ``v``
is true) and a negative integer ``-v`` denotes ``-v`` (variable ``v`` is
false).  A clause is a list of literals; a formula is a list of clauses.

The reduction creates one Boolean variable for each set in the exact‑cover
instance.  The variable is true exactly when the corresponding set is chosen
in the cover.

For every element ``e`` of the universe we enforce two constraints:

* **Coverage** – at least one of the sets containing ``e`` must be chosen.
  This is encoded as a single clause that is the disjunction of the
  corresponding positive literals.
* **Uniqueness** – at most one of those sets may be chosen, otherwise ``e``
  would appear more than once.  For each unordered pair of sets ``i`` and ``j``
  that both contain ``e`` we add the clause ``(-i ∨ -j)``.

If an element is not contained in any set we add an empty clause ``[]`` which
is unsatisfiable, correctly reflecting that the original instance has no
exact cover.

The construction runs in time polynomial in the size of the input (the
number of sets and the total number of element occurrences).
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce an Exact Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list
        of lists of ints).  The format follows the description in
        ``problems.py``.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py`` – a mapping
        with ``"num_vars"`` and ``"clauses"``.
    """

    u: int = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m: int = len(sets)

    clauses: List[List[int]] = []

    # For each element of the universe we collect the indices of sets that
    # contain it.  Indices are 0‑based internally; SAT variables are 1‑based.
    for e in range(u):
        containing = [idx for idx, s in enumerate(sets) if e in s]

        if not containing:
            # Element e cannot be covered – the exact‑cover instance is a
            # definite NO.  An empty clause makes the SAT instance unsatisfiable.
            clauses.append([])
            continue

        # At least one of the containing sets must be chosen.
        clauses.append([idx + 1 for idx in containing])

        # At most one – for every pair add a clause forbidding both to be true.
        for i in range(len(containing)):
            for j in range(i + 1, len(containing)):
                clauses.append([-(containing[i] + 1), -(containing[j] + 1)])

    # Edge case: empty universe (u == 0) yields no clauses, which is trivially
    # satisfiable.  The number of variables is still the number of sets.
    return {"num_vars": m, "clauses": clauses}

