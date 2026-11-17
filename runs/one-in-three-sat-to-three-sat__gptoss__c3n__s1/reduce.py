"""Reduction from 1-in-3-SAT (positive) to 3-SAT.

The source problem (OneInThreeSat) requires that each clause of three
positive variables has **exactly one** true literal.  The target problem
ThreeSat requires each clause (of three literals) to have **at least one**
true literal.

For a clause (a, b, c) we enforce the condition using the following
3‑SAT clauses:

* At least one true:               ( a ∨  b ∨  c )
* At most one true – pairwise constraints.  For each pair we introduce a
  fresh dummy variable d and encode the 2‑literal clause (¬x ∨ ¬y) as two
  3‑literal clauses:

      ( ¬x ∨ ¬y ∨  d )
      ( ¬x ∨ ¬y ∨ ¬d )

  The two clauses are simultaneously satisfiable iff (¬x ∨ ¬y) holds –
  because if both x and y are true the first clause forces d = true and the
  second forces d = false, a contradiction.

We create three fresh dummy variables per original clause, one for each
pair (a,b), (a,c) and (b,c).  The total number of variables in the
reduced instance is:

    m' = m + 3 * |clauses|

where ``m`` is the number of variables in the source instance.

The reduction runs in polynomial time and preserves satisfiability:
an assignment satisfies the original formula iff it can be extended with
appropriate values for the dummy variables to satisfy all generated 3‑SAT
clauses.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, ThreeSat


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary conforming to the ``OneInThreeSat`` format:
        ``{"num_vars": m, "clauses": [[a, b, c], ...]}``.

    Returns
    -------
    dict
        A dictionary conforming to the ``ThreeSat`` format that is
        satisfiable exactly when the input instance is.
    """
    # Validate the source instance – this will raise InvalidInstance if the
    # format is wrong.
    OneInThreeSat.validate(instance)

    m: int = instance["num_vars"]
    source_clauses: List[List[int]] = instance["clauses"]

    # No clauses – the formula is trivially satisfiable.  We can return an
    # empty 3‑SAT instance with the same number of variables.
    if not source_clauses:
        return {"num_vars": m, "clauses": []}

    new_clauses: List[List[int]] = []
    # We will allocate fresh dummy variables starting after the original
    # variables.  For each source clause we need three dummies.
    dummy_counter = m  # next fresh variable index (1‑based)

    for clause in source_clauses:
        a, b, c = clause  # each clause is guaranteed to have three distinct vars

        # 1. At least one true
        new_clauses.append([a, b, c])

        # Helper to add the pairwise at‑most‑one constraints using a fresh
        # dummy variable.
        def add_pairwise(x: int, y: int) -> None:
            nonlocal dummy_counter
            dummy_counter += 1
            d = dummy_counter
            # (¬x ∨ ¬y ∨  d)
            new_clauses.append([-x, -y, d])
            # (¬x ∨ ¬y ∨ ¬d)
            new_clauses.append([-x, -y, -d])

        # 2. Pairwise constraints
        add_pairwise(a, b)
        add_pairwise(a, c)
        add_pairwise(b, c)

    reduced_instance = {"num_vars": dummy_counter, "clauses": new_clauses}
    # Validate the produced instance to catch programming errors early.
    ThreeSat.validate(reduced_instance)
    return reduced_instance

