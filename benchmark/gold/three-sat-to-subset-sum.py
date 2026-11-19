"""Gold reduction: 3-SAT -> Subset Sum.                  [test, famous]

SOURCE  3-SAT       {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  Subset Sum  {"numbers": [...], "target": t}  yes iff a sub-list sums to t

Construction (base-10 digits; m variable digits, then c clause digits):
  * For each variable v, two numbers, T_v (v true) and F_v (v false). Both
    have a 1 in variable digit v. T_v also has a 1 in clause digit j for
    every clause j containing +v; F_v for every clause containing -v.
  * For each clause j, two slack numbers, each with a 1 in clause digit j.
  * Target: 1 in every variable digit, 3 in every clause digit.
"""


def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    c = len(clauses)

    def digit(position):  # variable digits 0..m-1, clause digits m..m+c-1
        return 10 ** position

    numbers = []
    for v in range(1, m + 1):
        true_number = false_number = digit(v - 1)
        for j, clause in enumerate(clauses):
            if v in clause:
                true_number += digit(m + j)
            if -v in clause:
                false_number += digit(m + j)
        numbers += [true_number, false_number]
    for j in range(c):
        numbers += [digit(m + j), digit(m + j)]
    target = sum(digit(i) for i in range(m)) + sum(3 * digit(m + j) for j in range(c))
    return {"numbers": numbers, "target": target}