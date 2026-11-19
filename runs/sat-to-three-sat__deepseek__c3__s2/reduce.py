"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

The reduction is the standard one:

* A clause that is a tautology (contains both v and -v) is dropped.
* Repeated literals in a clause are removed.
* A clause with 0 literals makes the whole formula unsatisfiable.
* A clause with 3 literals is kept as is.
* A clause with 1 literal l is replaced by the four clauses
      (l v p v q), (l v p v -q), (l v -p v q), (l v -p v -q)
  over two fresh variables p, q; this forces l to be true.
* A clause with 2 literals l1, l2 is replaced by the two clauses
      (l1 v l2 v p), (l1 v l2 v -p)
  over one fresh variable p; this forces l1 v l2.
* A clause with k >= 4 literals l1..lk is replaced by the chain
      (l1 v l2 v z1), (-z1 v l3 v z2), ..., (-z_{k-3} v l_{k-1} v lk)
  using k-3 fresh variables z1..z_{k-3}.

Every step preserves satisfiability, and the output is a valid 3-SAT
instance (exactly 3 literals on 3 distinct variables per clause).
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def _unsatisfiable_instance(num_vars: int) -> Instance:
    """An unsatisfiable 3-SAT instance on variables 1..max(3, num_vars).

    All eight clauses over variables 1, 2, 3 cannot be simultaneously
    satisfied, so this is always a no-instance.
    """
    n = max(3, num_vars)
    clauses = [
        [s1 * 1, s2 * 2, s3 * 3]
        for s1 in (1, -1)
        for s2 in (1, -1)
        for s3 in (1, -1)
    ]
    return {"num_vars": n, "clauses": clauses}


def reduce(instance: Instance) -> Instance:
    """Reduce a SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # An empty clause can never be satisfied.
    if any(len(clause) == 0 for clause in clauses):
        return _unsatisfiable_instance(num_vars)

    next_var = num_vars + 1

    def fresh() -> int:
        nonlocal next_var
        var = next_var
        next_var += 1
        return var

    out_clauses: list[list[int]] = []

    for clause in clauses:
        literals = set(clause)

        # A tautological clause is always true and can be discarded.
        if any(-lit in literals for lit in literals):
            continue

        # Deterministic order; all literals now have distinct variables.
        lits = sorted(literals, key=abs)
        k = len(lits)

        if k == 0:
            # Only possible for the empty clause, handled above.
            return _unsatisfiable_instance(num_vars)
        elif k == 1:
            l = lits[0]
            p, q = fresh(), fresh()
            out_clauses.append([l, p, q])
            out_clauses.append([l, p, -q])
            out_clauses.append([l, -p, q])
            out_clauses.append([l, -p, -q])
        elif k == 2:
            l1, l2 = lits
            p = fresh()
            out_clauses.append([l1, l2, p])
            out_clauses.append([l1, l2, -p])
        elif k == 3:
            out_clauses.append([lits[0], lits[1], lits[2]])
        else:
            # k >= 4: split with k-3 fresh chain variables.
            z = [fresh() for _ in range(k - 3)]
            out_clauses.append([lits[0], lits[1], z[0]])
            for i in range(1, k - 3):
                out_clauses.append([-z[i - 1], lits[i + 1], z[i]])
            out_clauses.append([-z[k - 4], lits[k - 2], lits[k - 1]])

    if out_clauses:
        # A 3-SAT instance with clauses needs at least 3 variables.
        target_vars = max(3, next_var - 1)
    else:
        # No clauses: satisfiable for any num_vars, including 0.
        target_vars = num_vars

    return {"num_vars": target_vars, "clauses": out_clauses}
