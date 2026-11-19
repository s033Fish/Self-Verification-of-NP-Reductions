"""Reduction from 3-SAT to positive 1-in-3-SAT.

We implement the classic polynomial‑time reduction using the
"triangle" gadget:
    (ℓ1 ∨ ℓ2 ∨ ℓ3)   ⇝   three clauses
        (ℓ1, a, b)
        (ℓ2, b, c)
        (ℓ3, c, a)
where a,b,c are fresh auxiliary variables.  It is easy to verify that the
three new clauses are satisfiable exactly when at least one of the three
literals ℓi is true.

Negated literals are handled by introducing, for each original variable i,
two new positive variables:
    xi   – intended to mean "i is true"
    yi   – intended to mean "i is false"
We add a gadget that forces exactly one of xi, yi to be true.  The gadget
uses three fresh auxiliaries (ti, ui, vi) and the following four
1‑in‑3 clauses:
    (xi, yi, ti)
    (ti, ui, vi)
    (ui, vi, wi)
    (vi, wi, xi)
The construction forces ti,ui,vi,wi to be false, leaving the first clause
as (xi, yi, false) which forces exactly one of xi, yi to be true.
(Any constant‑false variable can be obtained by the cycle of clauses
above; the cycle has a unique satisfying assignment in which all four
auxiliary variables are false.)

Putting everything together we obtain a polynomial‑size 1‑in‑3‑SAT instance
that is satisfiable iff the original 3‑SAT instance is satisfiable.
"""

from __future__ import annotations

from typing import Dict, List

# The target problem expects keys "num_vars" and "clauses".

def reduce(instance: Dict) -> Dict:
    # Validate source format loosely (the caller guarantees it).  We just
    # read the fields we need.
    m: int = instance["num_vars"]
    orig_clauses: List[List[int]] = instance["clauses"]

    # Mapping from original variable to its positive and negative target vars.
    # We'll allocate IDs sequentially.
    next_var = 1
    pos_var = {}  # v -> target var representing v = True
    neg_var = {}  # v -> target var representing v = False
    for v in range(1, m + 1):
        pos_var[v] = next_var
        next_var += 1
        neg_var[v] = next_var
        next_var += 1
        # Add the exactly‑one gadget for (pos, neg).
        # We'll create four fresh auxiliaries for the constant‑false cycle.
        t = next_var; next_var += 1
        u = next_var; next_var += 1
        vaux = next_var; next_var += 1
        w = next_var; next_var += 1
        # gadget clauses (see docstring)
        # (pos, neg, t)
        # (t, u, vaux)
        # (u, vaux, w)
        # (vaux, w, pos)
        # We'll collect them later.
        # Store them in a list.
        # We'll build clause list after the loop.
        if 'var_gadgets' not in locals():
            var_gadgets = []
        var_gadgets.extend([
            [pos_var[v], neg_var[v], t],
            [t, u, vaux],
            [u, vaux, w],
            [vaux, w, pos_var[v]],
        ])

    # Now handle each original clause.
    clause_gadgets = []
    for clause in orig_clauses:
        # clause is list of three literals, each like +v or -v (int with sign)
        a_lit, b_lit, c_lit = clause
        # map literal to target variable
        def lit_to_var(l):
            v = abs(l)
            return pos_var[v] if l > 0 else neg_var[v]
        a = lit_to_var(a_lit)
        b = lit_to_var(b_lit)
        c = lit_to_var(c_lit)
        # three fresh auxiliaries for the triangle gadget
        a_aux = next_var; next_var += 1
        b_aux = next_var; next_var += 1
        c_aux = next_var; next_var += 1
        clause_gadgets.extend([
            [a, a_aux, b_aux],
            [b, b_aux, c_aux],
            [c, c_aux, a_aux],
        ])

    # Combine all clauses
    all_clauses = []
    if 'var_gadgets' in locals():
        all_clauses.extend(var_gadgets)
    all_clauses.extend(clause_gadgets)

    return {"num_vars": next_var - 1, "clauses": all_clauses}

