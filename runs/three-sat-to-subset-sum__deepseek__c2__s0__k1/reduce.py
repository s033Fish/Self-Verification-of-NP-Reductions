"""Polynomial-time reduction from 3-SAT to Subset Sum.

For each variable v we create two numbers:
  * true_v  has digit 1 in variable position v and in every clause position
    whose clause contains +v.
  * false_v has digit 1 in variable position v and in every clause position
    whose clause contains -v.

For each clause we add two auxiliary numbers, each with digit 1 in that
clause's position.  The target has digit 1 in every variable position and
digit 3 in every clause position.

Because a clause has exactly three literals, each clause digit column can
receive at most 3 contributions from literal numbers plus 2 from auxiliary
numbers, i.e. at most 5.  Base 10 therefore causes no carries.  A subset
sums to the target exactly when it picks one of each variable pair and
satisfies every clause.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    base = 10
    # powers[p] = base ** p, for positions 0 .. m+n-1.
    powers = [1] * (m + n)
    for p in range(1, m + n):
        powers[p] = powers[p - 1] * base

    def var_pos(v):
        return v - 1

    def clause_pos(j):
        return m + j

    numbers = []

    # One pair of numbers per variable.
    for v in range(1, m + 1):
        true_num = powers[var_pos(v)]
        false_num = powers[var_pos(v)]
        for j, clause in enumerate(clauses):
            for lit in clause:
                if lit == v:
                    true_num += powers[clause_pos(j)]
                elif lit == -v:
                    false_num += powers[clause_pos(j)]
        numbers.append(true_num)
        numbers.append(false_num)

    # Two auxiliary numbers per clause.
    for j in range(n):
        numbers.append(powers[clause_pos(j)])
        numbers.append(powers[clause_pos(j)])

    # Target: one per variable digit, three per clause digit.
    target = 0
    for v in range(1, m + 1):
        target += powers[var_pos(v)]
    for j in range(n):
        target += 3 * powers[clause_pos(j)]

    return {"numbers": numbers, "target": target}
