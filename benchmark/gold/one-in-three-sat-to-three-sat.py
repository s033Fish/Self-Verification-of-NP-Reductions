"""Gold reduction: 1-in-3-SAT -> 3-SAT.              [difficulty: 5 of 6]

SOURCE  1-in-3-SAT  {"num_vars": m, "clauses": [[a, b, c], ...]}
        positive variables only; yes iff some assignment makes EXACTLY ONE
        variable in every clause true.
TARGET  3-SAT       {"num_vars": m', "clauses": [[l1, l2, l3], ...]}
        EXACTLY 3 literals per clause, on 3 DIFFERENT variables.

Construction
  "Exactly one of a, b, c" = "at least one" AND "no two together":
       (a or b or c)
       and (not a or not b) and (not a or not c) and (not b or not c)
  1. "At least one" is already a 3-literal clause: [a, b, c].
  2. "Not both a and b" has only 2 literals, and 3-SAT needs exactly 3. Pad
     it with a fresh variable z in both polarities:
       [-a, -b, z] and [-a, -b, -z]
     Together these are equivalent to (not a or not b), whatever z is.
  3. One fresh variable is enough for the whole formula: z = m + 1, so
     num_vars = m + 1. (Why can't you pad with a, b or c instead?)
  Each source clause becomes 1 + 3 * 2 = 7 clauses.

Edge cases
  * No clauses: the source is yes; the output should be satisfiable too.
  * The padding variable must differ from a and b, or the clause repeats a
    variable and the target's validate() rejects it.

Broken versions to try
  * Pad with a repeated literal, e.g. [-a, -b, -b] (rejected as malformed).
  * Only add "at least one" (the "no two together" part is lost).
  * Keep num_vars = m while using z = m + 1 (variable out of range).

Check it:
  uv run python -m benchmark.verify --reduce benchmark/gold/one-in-three-sat-to-three-sat.py --task one-in-three-sat-to-three-sat
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = list(instance["clauses"])

    for [a, b, c] in instance["clauses"]:
        clauses.append([-a, -b, num_vars+1])
        clauses.append([-a, -b, -(num_vars+1)])

        clauses.append([-a, -c, num_vars+1])
        clauses.append([-a, -c, -(num_vars+1)])

        clauses.append([-c, -b, num_vars+1])
        clauses.append([-c, -b, -(num_vars+1)])

    return {"num_vars": num_vars + 1, "clauses": clauses}