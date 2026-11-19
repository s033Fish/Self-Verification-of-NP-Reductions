"""BROKEN: 1-in-3-SAT -> Subset Sum in base 2, where 3 true variables carry.

SOURCE  1-in-3-SAT  {"num_vars": m, "clauses": [[a, b, c], ...]}  positive variables only;
                    yes iff some assignment makes EXACTLY ONE variable per clause true
TARGET  Subset Sum  {"numbers": [...], "target": t}  yes iff a sub-list sums to t

Construction: base-4 digits, one per clause. Variable v becomes the number
sum of 4^j over the clauses j that contain v. Target: a 1 in every clause
digit, sum of 4^j for j = 0..c-1.
"""


def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    numbers = [0] * m
    for j, clause in enumerate(clauses):
        for v in clause:
            numbers[v - 1] += 2 ** j  # BUG: 3 = 0b11 carries into the next clause digit
    return {"numbers": numbers, "target": sum(2 ** j for j in range(len(clauses)))}