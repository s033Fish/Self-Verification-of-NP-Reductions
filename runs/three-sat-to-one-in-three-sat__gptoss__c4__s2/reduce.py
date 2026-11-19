"""Reduction from 3-SAT (ThreeSat) to 1-in-3-SAT (OneInThreeSat).

The source problem allows literals to be positive (+v) or negative (-v).
The target problem only permits positive literals (variables identified by
integers 1..m).  A classic polynomial‑time reduction introduces three fresh
auxiliary variables per clause and replaces a clause (ℓ1 ∨ ℓ2 ∨ ℓ3) with the
following four 1‑in‑3 clauses:

    (ℓ1, a, b)
    (ℓ2, b, c)
    (ℓ3, c, a)
    (a, b, c)

The auxiliary variables a,b,c are new for each original clause.  The last
clause forces exactly one of a,b,c to be true, which in turn forces exactly
one of the three original literals to be true – i.e. the original clause is
satisfied.

To handle negated literals we introduce, for every original variable *v*, two
new variables ``pos_v`` and ``neg_v`` that represent the truth values of *v*
and ¬*v* respectively.  We enforce that exactly one of them is true by
adding the clause ``(pos_v, neg_v, aux_v)`` together with an auxiliary variable
``aux_v`` that is forced to **false**.  A variable forced false can be created
by a pair of clauses that make it impossible to be true: for a fresh variable
``false`` we add the clauses ``(false, false, x)`` and ``(false, x, y)`` where
``x`` and ``y`` are also fresh.  The only satisfying assignment for these two
clauses is ``false = 0`` (otherwise the first clause would have 2 or 3 true
variables).  This construction uses only a constant number of auxiliary
variables per original variable, keeping the reduction polynomial.

The implementation below follows this idea.  It is deliberately simple and
does not attempt any optimisation – clarity and correctness are the goals.
"""

from __future__ import annotations

from typing import List, Dict, Any

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a OneInThreeSat instance.

    Parameters
    ----------
    instance: dict with keys ``num_vars`` and ``clauses`` as described in
        ``problems.py`` for ThreeSat.

    Returns
    -------
    dict with keys ``num_vars`` and ``clauses`` suitable for OneInThreeSat.
    """

    m = instance["num_vars"]
    orig_clauses: List[List[int]] = instance["clauses"]

    # Mapping from original variable to two new variables representing the
    # positive and negative occurrence.
    pos_var: Dict[int, int] = {}
    neg_var: Dict[int, int] = {}
    # We'll also create a dedicated "false" constant variable.
    # It will be forced to false by a small gadget (see below).
    next_var = m + 1

    # Create false constant variable and its gadget.
    false_const = next_var
    next_var += 1
    # auxiliary variables for the false gadget
    false_aux1 = next_var
    next_var += 1
    false_aux2 = next_var
    next_var += 1
    # clauses that force false_const = 0
    false_gadget_clauses = [
        [false_const, false_const, false_aux1],
        [false_const, false_aux1, false_aux2],
    ]

    # Create positive/negative representation for each original variable.
    for v in range(1, m + 1):
        pos = next_var
        next_var += 1
        neg = next_var
        next_var += 1
        pos_var[v] = pos
        neg_var[v] = neg

    # For each original variable we need a clause that forces exactly one of
    # pos_v and neg_v to be true.  Using the false constant we can write a
    # single 1‑in‑3 clause: (pos_v, neg_v, false_const).  Since false_const is
    # forced to 0, the clause demands exactly one of pos_v, neg_v to be 1.
    var_choice_clauses = []
    for v in range(1, m + 1):
        var_choice_clauses.append([pos_var[v], neg_var[v], false_const])

    # Now translate each 3‑SAT clause.
    new_clauses: List[List[int]] = []
    for clause in orig_clauses:
        # clause is list of three literals, each literal is an int where sign
        # indicates polarity.
        lit_vars = []
        for lit in clause:
            var = abs(lit)
            if lit > 0:
                lit_vars.append(pos_var[var])
            else:
                lit_vars.append(neg_var[var])
        # introduce three fresh auxiliary variables a,b,c for this clause
        a = next_var
        b = next_var + 1
        c = next_var + 2
        next_var += 3
        # add the four 1‑in‑3 clauses described in the docstring
        new_clauses.append([lit_vars[0], a, b])
        new_clauses.append([lit_vars[1], b, c])
        new_clauses.append([lit_vars[2], c, a])
        new_clauses.append([a, b, c])

    all_clauses = false_gadget_clauses + var_choice_clauses + new_clauses
    return {"num_vars": next_var - 1, "clauses": all_clauses}

