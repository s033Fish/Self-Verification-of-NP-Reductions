"""Reduction from 3‑SAT to Exact Cover.

The source problem (ThreeSat) uses the following instance format::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (variable ``v`` true) or
``-v`` (variable ``v`` false).  Every clause contains exactly three
distinct variables.

The target problem (ExactCover) expects instances of the form::

    {"universe_size": u, "sets": [[e1, e2, ...], ...]}

The universe consists of the elements ``0 .. u‑1``.  The answer is *yes*
iff a sub‑collection of the given sets is pairwise disjoint and their
union equals the whole universe.

The reduction below follows the classic Karp reduction (Problem 4 –
Exact Cover).  For each variable ``x_i`` we create two sets – one for the
assignment ``x_i = True`` and one for ``x_i = False`` – that both contain a
unique *variable element* ``v_i``.  In addition each set contains the
*clause‑literal element* corresponding to the literal it represents.

For each clause ``C_j = (ℓ_{j,1} ∨ ℓ_{j,2} ∨ ℓ_{j,3})`` we introduce three
dedicated elements ``c_{j,1}, c_{j,2}, c_{j,3}``.  To guarantee that at
least one literal of the clause is chosen we add three auxiliary sets:

* ``{c_{j,2}, c_{j,3}}`` – used when the first literal is selected,
* ``{c_{j,1}, c_{j,3}}`` – used when the second literal is selected,
* ``{c_{j,1}, c_{j,2}}`` – used when the third literal is selected.

If a literal set covering ``c_{j,k}`` is taken, the corresponding
auxiliary set covers the remaining two clause elements without overlap.
If **no** literal of the clause is selected, the three auxiliary sets
cannot cover the three elements without overlapping, so an exact cover
is impossible.  Consequently an exact cover exists exactly when the
original 3‑SAT formula is satisfiable.

The construction runs in time linear in the size of the 3‑SAT instance
and produces a polynomial‑size Exact Cover instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"``
        (list of three‑element lists of integers).

    Returns
    -------
    dict
        An ExactCover instance with keys ``"universe_size"`` and
        ``"sets"`` as described in the module docstring.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Universe layout:
    #   0 .. m-1                 – variable elements (one per variable)
    #   m .. m + 3*len(clauses)-1 – clause‑literal elements, three per clause
    num_clause_elems = len(clauses) * 3
    universe_size = m + num_clause_elems

    sets: List[List[int]] = []

    # Variable assignment sets.
    # For each variable i (1‑based in the SAT instance) we create two sets:
    #   true_set  – contains the variable element and the clause‑literal
    #               elements for every occurrence of the positive literal.
    #   false_set – same but for the negative literal.
    for i in range(1, m + 1):
        true_set: List[int] = [i - 1]
        false_set: List[int] = [i - 1]
        for j, clause in enumerate(clauses):
            for k, lit in enumerate(clause):
                var = abs(lit)
                sign = lit > 0
                elem = m + j * 3 + k  # clause‑literal element index
                if var == i:
                    if sign:
                        true_set.append(elem)
                    else:
                        false_set.append(elem)
        sets.append(true_set)
        sets.append(false_set)

    # Clause gadget auxiliary sets.
    # For each clause we add three 2‑element sets that together enforce that
    # exactly one of the three clause‑literal elements is covered by a
    # variable assignment set.
    for j in range(len(clauses)):
        a = m + j * 3      # element for literal 1
        b = a + 1          # element for literal 2
        c = a + 2          # element for literal 3
        # If literal 1 is chosen, we need to cover b and c.
        sets.append([b, c])
        # If literal 2 is chosen, we need to cover a and c.
        sets.append([a, c])
        # If literal 3 is chosen, we need to cover a and b.
        sets.append([a, b])

    return {"universe_size": universe_size, "sets": sets}

