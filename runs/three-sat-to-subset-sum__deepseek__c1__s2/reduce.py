"""Polynomial-time reduction from 3-SAT to Subset Sum.

Encoding
--------
Let n = num_vars and k = len(clauses).  We build decimal numbers whose
digits are indexed by "columns":

    * variable v (1..n)   -> column v - 1
    * clause   j (0..k-1) -> column n + j

For every variable v we add two numbers (the "true" and "false" choice):

    true_v  = 10**(v-1) + sum(10**(n+j) for clauses j containing  +v)
    false_v = 10**(v-1) + sum(10**(n+j) for clauses j containing  -v)

For every clause j we add two slack numbers, each equal to 10**(n+j).

The target has digit 1 in every variable column and digit 3 in every
clause column.

Correctness
-----------
Variable column v receives either 0, 1 or 2 from the two variable numbers
of v (all other numbers have 0 there).  The target digit is 1, so any
solution must pick exactly one of true_v / false_v: this is exactly a
truth assignment.

Clause column j receives a_j in {0,1,2,3} from the three literal
occurrences (one per variable in the clause) plus b_j in {0,1,2} from the
two slack numbers of clause j.  The target digit is 3, so a_j + b_j = 3.
This is possible iff a_j >= 1, i.e. iff the clause has at least one true
literal (a_j = 0 leaves at most b_j = 2 < 3; a_j = 1 needs both slacks;
a_j = 2 needs one slack; a_j = 3 needs none).  Hence a subset summing to
the target exists iff the formula is satisfiable.

No column ever exceeds 5 < 10, so there are no carries between columns and
the digit argument is exact.  The construction uses 2n + 2k numbers, each
with O(n + k) digits, so it runs in polynomial time.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = num_vars
    k = len(clauses)

    def var_col(v):
        return 10 ** (v - 1)

    def clause_col(j):
        return 10 ** (n + j)

    target = 0
    for v in range(1, n + 1):
        target += var_col(v)
    for j in range(k):
        target += 3 * clause_col(j)

    numbers = []

    # One number per (variable, truth value).
    for v in range(1, n + 1):
        base = var_col(v)
        true_num = base
        false_num = base
        for j, clause in enumerate(clauses):
            if v in clause:
                true_num += clause_col(j)
            if -v in clause:
                false_num += clause_col(j)
        numbers.append(true_num)
        numbers.append(false_num)

    # Two slack numbers per clause, each contributing 1 to that column.
    for j in range(k):
        numbers.append(clause_col(j))
        numbers.append(clause_col(j))

    return {"numbers": numbers, "target": target}
