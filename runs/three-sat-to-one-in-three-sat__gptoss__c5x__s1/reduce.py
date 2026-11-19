"""Reduction from 3-SAT to 1-in-3-SAT (positive).

The source problem is defined by :class:`ThreeSat` in ``problems.py`` and the
target problem by :class:`OneInThreeSat`.  Both classes only provide a
``validate`` method; they do not contain solvers.  This module implements a
polynomial‑time many‑one reduction ``reduce`` that maps a 3‑SAT instance to a
1‑in‑3‑SAT instance such that the target instance is satisfiable iff the source
instance is.

The construction follows a classic textbook reduction (see, e.g., Garey &
Johnson, *Computers and Intractability*).  For each original variable ``x`` we
introduce two new variables ``x_pos`` and ``x_neg`` that represent the truth
value of ``x`` and its negation.  A global *false* constant ``F`` is created
using a small gadget; the clause ``(x_pos, x_neg, F)`` then forces exactly one
of ``x_pos``/``x_neg`` to be true.

For each original clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we add three fresh auxiliary
variables ``a_c, b_c, c_c`` and three 1‑in‑3 clauses:

``(L1, a_c, b_c)``, ``(L2, b_c, c_c)``, ``(L3, c_c, a_c)``

where ``L_i`` is the variable that corresponds to the literal ``ℓ_i`` (positive
or negated).  This gadget is known to be satisfiable exactly when at least one
of the literals is true: if none are true the three auxiliary variables would
have to satisfy mutually exclusive “exactly‑one” constraints, which is
impossible.

All variables are represented by positive integers as required by the target
format.  The function runs in time linear in the size of the input instance.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, OneInThreeSat


def _new_var(counter: List[int]) -> int:
    """Return a fresh variable identifier and increment the counter.

    ``counter`` is a one‑element list so that the integer can be mutated in
    place (Python integers are immutable).  The first call returns ``1``.
    """

    counter[0] += 1
    return counter[0]


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a positive 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``ThreeSat`` format.

    Returns
    -------
    dict
        An instance of ``OneInThreeSat`` that is satisfiable exactly when the
        input instance is.
    """

    # Validate the source instance to catch malformed inputs early.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Variable numbering scheme:
    #   1 .. m               -> x_pos for original variable i (i true)
    #   m+1 .. 2m            -> x_neg for original variable i (i false)
    #   next IDs             -> auxiliary variables (false constant, etc.)
    var_counter = [0]
    # Reserve the first 2*m identifiers.
    for _ in range(2 * m):
        _new_var(var_counter)

    # ----- gadget for a global false constant F -----
    # We create three auxiliary variables A, B, C and a variable F.
    A = _new_var(var_counter)
    B = _new_var(var_counter)
    C = _new_var(var_counter)
    F = _new_var(var_counter)
    false_gadget = [
        [F, A, B],
        [F, A, C],
        [F, B, C],
        [A, B, C],
    ]

    # ----- variable consistency clauses -----
    # For each original variable i we enforce exactly one of (pos, neg) true.
    consistency_clauses: List[List[int]] = []
    for i in range(1, m + 1):
        pos = i  # x_pos
        neg = m + i  # x_neg
        consistency_clauses.append([pos, neg, F])

    # ----- clause gadgets -----
    clause_gadgets: List[List[int]] = []
    for clause in clauses:
        # Map literals to the corresponding positive‑only variable.
        def lit_to_var(lit: int) -> int:
            var = abs(lit)
            if lit > 0:
                return var  # x_pos
            else:
                return m + var  # x_neg

        L1, L2, L3 = map(lit_to_var, clause)
        # Fresh auxiliary variables for this clause.
        a = _new_var(var_counter)
        b = _new_var(var_counter)
        c = _new_var(var_counter)
        clause_gadgets.extend([
            [L1, a, b],
            [L2, b, c],
            [L3, c, a],
        ])

    # Assemble final instance.
    target_instance = {
        "num_vars": var_counter[0],
        "clauses": false_gadget + consistency_clauses + clause_gadgets,
    }

    # Validate the produced target instance.
    OneInThreeSat.validate(target_instance)
    return target_instance

