"""Polynomial-time reduction from SAT to 3-SAT.

The reduction is the standard one:

* A clause that contains both ``v`` and ``-v`` is a tautology and is dropped.
* Duplicate literals inside a clause are removed.
* A clause of length 1, ``(l)``, becomes four clauses over two fresh
  variables ``x``, ``y``::

      (l v x v y) & (l v -x v y) & (l v x v -y) & (l v -x v -y)

  which is true exactly when ``l`` is true.
* A clause of length 2, ``(l1 v l2)``, becomes two clauses over one fresh
  variable ``x``::

      (l1 v l2 v x) & (l1 v l2 v -x)

  which is true exactly when ``l1 v l2`` is true.
* A clause of length 3 is kept as is.
* A clause ``(l1 v ... v lk)`` with ``k >= 4`` is split with ``k - 3``
  fresh variables ``x1, ..., x_{k-3}``::

      (l1 v l2 v x1)
      (-x1 v l3 v x2)
      ...
      (-x_{k-4} v l_{k-2} v x_{k-3})
      (-x_{k-3} v l_{k-1} v lk)

  The fresh variables can always be chosen to satisfy the new clauses
  exactly when the original clause is satisfied.
* An empty clause makes the formula unsatisfiable, so the whole output is
  replaced by the eight clauses over three variables that are unsatisfiable.

Every produced clause has exactly three literals on three different
variables, and the number of fresh variables is linear in the input size,
so the reduction runs in polynomial time.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def _unsat_gadget() -> list[list[int]]:
    """All eight clauses over variables 1, 2, 3; unsatisfiable."""
    clauses = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            for s3 in (1, -1):
                clauses.append([s1 * 1, s2 * 2, s3 * 3])
    return clauses


def reduce(instance: Instance) -> Instance:
    """Reduce a SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = num_vars + 1

    def fresh() -> int:
        nonlocal next_var
        var = next_var
        next_var += 1
        return var

    out: list[list[int]] = []

    for clause in clauses:
        # Remove duplicates and detect tautologies (both v and -v present).
        seen: set[int] = set()
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            seen.add(literal)
        if tautology:
            # Always satisfied: drop it.
            continue

        if not seen:
            # The empty clause can never be satisfied.
            return {
                "num_vars": max(num_vars, 3),
                "clauses": _unsat_gadget(),
            }

        literals = sorted(seen, key=abs)
        length = len(literals)

        if length == 1:
            (l,) = literals
            x = fresh()
            y = fresh()
            out.append([l, x, y])
            out.append([l, -x, y])
            out.append([l, x, -y])
            out.append([l, -x, -y])
        elif length == 2:
            l1, l2 = literals
            x = fresh()
            out.append([l1, l2, x])
            out.append([l1, l2, -x])
        elif length == 3:
            out.append(list(literals))
        else:
            # length >= 4: chain of fresh variables.
            xs = [fresh() for _ in range(length - 3)]
            out.append([literals[0], literals[1], xs[0]])
            for i in range(1, length - 3):
                out.append([-xs[i - 1], literals[i + 1], xs[i]])
            out.append([-xs[-1], literals[length - 2], literals[length - 1]])

    return {"num_vars": next_var - 1, "clauses": out}
