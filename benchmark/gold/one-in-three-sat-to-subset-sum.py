"""Gold reduction: 1-in-3-SAT -> Subset Sum.             [test, less common]

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
            numbers[v - 1] += 4 ** j
    return {"numbers": numbers, "target": sum(4 ** j for j in range(len(clauses)))}