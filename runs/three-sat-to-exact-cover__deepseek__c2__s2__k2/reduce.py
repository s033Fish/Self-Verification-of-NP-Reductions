"""Polynomial-time reduction from 3-SAT to Exact Cover.

Universe elements:
  * For each variable v in 1..m: two elements, one meaning "v is true" and
    one meaning "v is false".
  * For each clause c: one element that must be covered.

Sets:
  * For each variable v: {true_v, false_v}.  An exact cover must take exactly
    one of these, fixing the truth value of v.
  * For each clause c and each literal l in c: {clause_c, truth_element(l)}.
    Taking this set covers clause c and simultaneously requires the variable
    of l to have the truth value that makes l true.

An exact cover selects exactly one truth element per variable and exactly one
literal-set per clause, and the selected literal-sets are consistent with the
chosen truth values.  Hence an exact cover exists iff the formula is
satisfiable, and the construction is linear in the input size.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Element ids: variable v (1-based) -> true element 2*(v-1),
    # false element 2*(v-1)+1.  Clause c -> 2*num_vars + c.
    def true_elem(v):
        return 2 * (v - 1)

    def false_elem(v):
        return 2 * (v - 1) + 1

    sets = []
    for v in range(1, num_vars + 1):
        sets.append([true_elem(v), false_elem(v)])

    for c, clause in enumerate(clauses):
        clause_elem = 2 * num_vars + c
        for literal in clause:
            v = abs(literal)
            if literal > 0:
                sets.append([clause_elem, true_elem(v)])
            else:
                sets.append([clause_elem, false_elem(v)])

    universe_size = 2 * num_vars + len(clauses)
    return {"universe_size": universe_size, "sets": sets}
