"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Given a 3-SAT instance with variables 1..m and clauses (l1 v l2 v l3), we
introduce one global variable z and one fresh variable y per clause, and
replace each clause by the two NAE-3 clauses

    NAE(l1, l2, y)      and      NAE(-y, l3, z).

Correctness:
  * If the 3-SAT formula is satisfied, set z = false.  For each clause:
      - if l3 is true, the second NAE clause is automatically satisfied
        (it contains both a true and a false literal); pick y = true when
        l1 and l2 are both false, otherwise y may be arbitrary;
      - if l3 is false then l1 or l2 is true, so set y = false: the second
        clause is (true, false, false) and the first is not all equal.
    Hence all NAE clauses are satisfied.
  * Conversely, any NAE-satisfying assignment can be globally flipped
    (NAE satisfaction is invariant under negating every literal), so assume
    z = false.  If some original clause had l1 = l2 = l3 = false, the second
    NAE clause would force y = false, making the first clause (false, false,
    false), a contradiction.  Thus every original clause has a true literal.

The construction uses m + 1 + k variables and 2k clauses for k input
clauses, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an equisatisfiable NAE-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # No clauses: already yes for both problems.
    if not clauses:
        return {"num_vars": num_vars, "clauses": []}

    z = num_vars + 1          # global variable
    next_var = num_vars + 2   # first fresh per-clause variable
    out_clauses = []

    for l1, l2, l3 in clauses:
        y = next_var
        next_var += 1
        out_clauses.append([l1, l2, y])
        out_clauses.append([-y, l3, z])

    return {"num_vars": next_var - 1, "clauses": out_clauses}
