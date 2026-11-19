"""Reduction from One-In-Three SAT (positive literals) to 3-SAT.

The source problem (OneInThreeSat) instance format:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where a,b,c are distinct positive integers (variables 1..m).
The target problem (ThreeSat) instance format:
    {"num_vars": m', "clauses": [[l1, l2, l3], ...]}
where each literal li is a signed integer: +v for variable v, -v for its negation.
Each clause must contain exactly three literals on three distinct variables.

The reduction enforces that each original clause has exactly one true variable.
For a clause (a, b, c) we create:
  1. (a ∨ b ∨ c)                – at least one true.
  2. For each pair (x, y) in {(a,b), (a,c), (b,c)} we add two clauses
       (¬x ∨ ¬y ∨ p) and (¬x ∨ ¬y ∨ ¬p)
     where p is a fresh auxiliary variable unique to that pair.
     The pair of clauses is equivalent to (¬x ∨ ¬y) (i.e., at most one of x,y true).
Together they enforce exactly‑one true among a,b,c.

For each original clause we introduce three fresh variables, so the total
number of variables is m + 3·|clauses|.
"""

def reduce(instance):
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "num_vars" (int) and "clauses" (list of
        three‑element lists of positive ints).

    Returns
    -------
    dict
        A ThreeSat instance dictionary with keys "num_vars" and "clauses".
    """
    m = instance.get("num_vars", 0)
    src_clauses = instance.get("clauses", [])
    n = len(src_clauses)

    # Each source clause introduces three fresh auxiliary variables.
    new_m = m + 3 * n
    clauses = []

    for i, triple in enumerate(src_clauses):
        if len(triple) != 3:
            # Defensive: skip malformed clause (should not happen).
            continue
        a, b, c = triple
        # Clause enforcing at least one true.
        clauses.append([a, b, c])
        # Pairs for at‑most‑one constraints.
        pairs = [(a, b), (a, c), (b, c)]
        for j, (x, y) in enumerate(pairs):
            # Auxiliary variable index (1‑based).
            p = m + 3 * i + j + 1
            # Two clauses that together are equivalent to (¬x ∨ ¬y).
            clauses.append([-x, -y, p])
            clauses.append([-x, -y, -p])

    return {"num_vars": new_m, "clauses": clauses}

if __name__ == "__main__":
    # Simple self‑test (not exhaustive).
    example = {"num_vars": 3, "clauses": [[1, 2, 3]]}
    print(reduce(example))
