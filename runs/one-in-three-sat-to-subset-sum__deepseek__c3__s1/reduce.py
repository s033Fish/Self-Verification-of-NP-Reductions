"""Polynomial-time reduction from 1-in-3-SAT to Subset Sum.

Idea
----
Let the formula have m variables and n clauses.  Pick a base B large enough
that no digit position ever carries (B > 3 is enough, since a clause contains
exactly 3 variables and a variable contributes to at most one digit per
clause).  Represent numbers in base B with m "variable" digits (positions
0..m-1) followed by n "clause" digits (positions m..m+n-1).

For every variable i (1-based) add two numbers:

  * true_i  = B^(i-1) + sum over clauses j containing i of B^(m+j)
  * false_i = B^(i-1)

The target is

  T = sum_i B^(i-1) + sum_j B^(m+j)

Choosing exactly one number of each pair makes every variable digit equal 1.
A chosen true_i adds 1 to the clause digit of every clause containing i, while
false_i adds nothing.  Hence clause digit j equals the number of true
variables in clause j.  Because there are no carries, the sum equals T iff
every clause digit is exactly 1, i.e. every clause has exactly one true
variable.  So the Subset Sum instance is yes iff the formula is 1-in-3
satisfiable.

The instance has 2m numbers, each of O(m+n) bits, so the reduction runs in
polynomial time and never calls a solver.
"""

from typing import Any, Dict


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    m = num_vars
    n = len(clauses)

    # Base large enough to prevent carries: the largest possible digit sum is
    # 3 (three true variables in a clause), so anything >= 4 works.
    base = max(m + n + 1, 4)

    var_weight = [base ** i for i in range(m)]
    clause_weight = [base ** (m + j) for j in range(n)]

    numbers = []
    for i in range(m):
        # "true" number: variable digit plus one digit per clause containing i
        true_number = var_weight[i]
        for j, clause in enumerate(clauses):
            if (i + 1) in clause:
                true_number += clause_weight[j]
        numbers.append(true_number)
        # "false" number: only the variable digit
        numbers.append(var_weight[i])

    target = sum(var_weight) + sum(clause_weight)
    return {"numbers": numbers, "target": target}
