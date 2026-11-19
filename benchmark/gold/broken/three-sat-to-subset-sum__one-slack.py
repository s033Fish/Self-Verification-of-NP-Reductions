"""BROKEN: 3-SAT -> Subset Sum with one slack number per clause.

SOURCE  3-SAT       {"num_vars": m, "clauses": [[l1, l2, l3], ...]}  yes iff satisfiable
TARGET  Subset Sum  {"numbers": [...], "target": t}  yes iff a sub-list sums to t

Construction (base-10 digits; m variable digits, then c clause digits):
  * For each variable v, two numbers, T_v (v true) and F_v (v false). Both
    have a 1 in variable digit v. T_v also has a 1 in clause digit j for
    every clause j containing +v; F_v for every clause containing -v.
  * For each clause j, two slack numbers, each with a 1 in clause digit j.
  * Target: 1 in every variable digit, 3 in every clause digit.

Why: no digit ever sums past 5 (3 literals + 2 slacks; a clause has 3
different variables), so there are no carries and each digit can be read
separately. A variable digit of 1 means exactly one of T_v, F_v: an
assignment. A clause digit gets 1 per true literal plus up to 2 from its
slacks, and reaches exactly 3 iff at least one literal is true.

Edge cases: no clauses: only variable digits, always reachable (yes).
m = 0 and no clauses: no numbers, target 0: yes.
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
        numbers += [digit(m + j)]  # BUG: a clause with one true literal reaches only 2
    target = sum(digit(i) for i in range(m)) + sum(3 * digit(m + j) for j in range(c))
    return {"numbers": numbers, "target": target}