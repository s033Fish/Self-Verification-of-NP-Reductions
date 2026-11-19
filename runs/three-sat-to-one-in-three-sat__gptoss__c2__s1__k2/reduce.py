"""Reduction from 3‑SAT to Positive 1‑in‑3‑SAT.

The source problem (ThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Every clause contains three
different variables.

The target problem (OneInThreeSat) allows only *positive* literals and asks
for an assignment such that **exactly one** variable in each clause is true.

The reduction follows the classic gadget due to Schaefer:

* For each original variable ``x`` we introduce two new variables
  ``X_pos`` and ``X_neg`` representing the truth of ``x`` and ``¬x``
  respectively.  To force them to be complementary we add three auxiliary
  variables ``a``, ``b`` and ``c`` and the following three 1‑in‑3 clauses::

        (X_pos, X_neg, a)
        (X_pos, X_neg, b)
        (a,     b,     c)

  This gadget admits a satisfying assignment iff exactly one of
  ``X_pos`` and ``X_neg`` is true – the auxiliary variable ``c`` is forced to
  be true in any satisfying assignment.

* For each original clause ``(ℓ1 ∨ ℓ2 ∨ ℓ3)`` we use the well‑known
  1‑in‑3 SAT gadget that introduces three fresh variables ``y1, y2, y3`` and
  adds four clauses::

        (ℓ1', ℓ2', y1)
        (ℓ1', ℓ3', y2)
        (ℓ2', ℓ3', y3)
        (y1,  y2,  y3)

  Here ``ℓi'`` is the positive variable representing the literal
  (``X_pos`` for a positive literal and ``X_neg`` for a negative one).
  The gadget is satisfiable exactly when at least one of the three original
  literals is true.

Putting the two gadgets together yields a polynomial‑time many‑to‑one
reduction: the constructed OneInThreeSat instance is satisfiable iff the
original 3‑SAT instance is.

The ``reduce`` function builds the target instance and returns it as a plain
dictionary matching the format required by ``OneInThreeSat``.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three integer literals).  The format follows the docstring of
        ``ThreeSat`` in ``problems.py``.

    Returns
    -------
    dict
        An instance of the target problem ``OneInThreeSat``.  The dictionary
        contains the same keys ``"num_vars"`` and ``"clauses"`` where each
        clause is a list of three *positive* variable indices.
    """

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # ------------------------------------------------------------------
    # Variable allocation strategy
    # ------------------------------------------------------------------
    # For each original variable i (1‑based) we allocate:
    #   pos_i, neg_i, a_i, b_i, c_i  (5 fresh variables)
    # After that we allocate three fresh variables per original clause for the
    # clause gadget.
    # All variables are numbered consecutively starting at 1.
    var_counter = 1
    pos = [0] * (m + 1)  # index 0 unused
    neg = [0] * (m + 1)
    aux_a = [0] * (m + 1)
    aux_b = [0] * (m + 1)
    aux_c = [0] * (m + 1)

    for i in range(1, m + 1):
        pos[i] = var_counter
        var_counter += 1
        neg[i] = var_counter
        var_counter += 1
        aux_a[i] = var_counter
        var_counter += 1
        aux_b[i] = var_counter
        var_counter += 1
        aux_c[i] = var_counter
        var_counter += 1

    target_clauses: List[List[int]] = []

    # ------------------------------------------------------------------
    # 1‑in‑3 gadget that forces exactly one of pos_i / neg_i to be true.
    # ------------------------------------------------------------------
    for i in range(1, m + 1):
        # (pos_i, neg_i, a_i)
        target_clauses.append([pos[i], neg[i], aux_a[i]])
        # (pos_i, neg_i, b_i)
        target_clauses.append([pos[i], neg[i], aux_b[i]])
        # (a_i, b_i, c_i)
        target_clauses.append([aux_a[i], aux_b[i], aux_c[i]])

    # ------------------------------------------------------------------
    # Clause gadgets for each original 3‑SAT clause.
    # ------------------------------------------------------------------
    for clause in source_clauses:
        # Map each literal to the corresponding positive variable in the
        # target instance.
        lit_vars = []
        for lit in clause:
            v = abs(lit)
            if lit > 0:
                lit_vars.append(pos[v])
            else:
                lit_vars.append(neg[v])

        # Introduce three fresh auxiliary variables y1, y2, y3.
        y1 = var_counter
        var_counter += 1
        y2 = var_counter
        var_counter += 1
        y3 = var_counter
        var_counter += 1

        # Add the four clauses of the gadget.
        a1, a2, a3 = lit_vars
        target_clauses.append([a1, a2, y1])
        target_clauses.append([a1, a3, y2])
        target_clauses.append([a2, a3, y3])
        target_clauses.append([y1, y2, y3])

    # The total number of variables is the last used counter minus one.
    num_target_vars = var_counter - 1

    return {"num_vars": num_target_vars, "clauses": target_clauses}

