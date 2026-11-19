"""Polynomial-time reduction from SAT to 3-SAT.

Source instance:  {"num_vars": m, "clauses": [[literal, ...], ...]}
Target instance:  {"num_vars": m', "clauses": [[l1, l2, l3], ...]}

The reduction preserves satisfiability exactly:

* A source clause that is a tautology (contains both v and -v) is dropped.
* Repeated literals in a clause are removed.
* A clause of length 3 on 3 distinct variables is kept unchanged.
* A clause of length 1, [l], becomes four 3-clauses over l and two fresh
  variables a, b:  (l|a|b) & (l|a|-b) & (l|-a|b) & (l|-a|-b), which is
  equivalent to l.
* A clause of length 2, [l1, l2], becomes (l1|l2|a) & (l1|l2|-a) with one
  fresh variable a, which is equivalent to l1|l2.
* A clause of length k >= 4, [l1, ..., lk], becomes the standard chain
  (l1|l2|z1) & (-z1|l3|z2) & ... & (-z_{k-3}|l_{k-1}|lk) with fresh
  variables z1, ..., z_{k-3}, which is equivalent to the original clause.
* An empty clause is replaced by all eight 3-clauses over three fresh
  variables, which is unsatisfiable.

All fresh variables are numbered after the original ones, so the returned
instance is a valid 3-SAT instance.  The construction is linear in the size
of the input (each source literal contributes O(1) target clauses).
"""


def reduce(instance):
    """Reduce a SAT instance to an equisatisfiable 3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    next_var = num_vars + 1

    def fresh():
        nonlocal next_var
        var = next_var
        next_var += 1
        return var

    result = []

    for clause in clauses:
        # Canonicalize: remove duplicate literals; a clause containing both
        # v and -v is a tautology and can be dropped entirely.
        seen = set()
        literals = []
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            if literal not in seen:
                seen.add(literal)
                literals.append(literal)
        if tautology:
            continue

        length = len(literals)

        if length == 0:
            # Empty clause: encode an explicit contradiction over 3 fresh
            # variables using all eight possible clauses.
            a, b, c = fresh(), fresh(), fresh()
            for sa in (a, -a):
                for sb in (b, -b):
                    for sc in (c, -c):
                        result.append([sa, sb, sc])
        elif length == 1:
            literal = literals[0]
            a, b = fresh(), fresh()
            result.append([literal, a, b])
            result.append([literal, a, -b])
            result.append([literal, -a, b])
            result.append([literal, -a, -b])
        elif length == 2:
            first, second = literals
            a = fresh()
            result.append([first, second, a])
            result.append([first, second, -a])
        elif length == 3:
            result.append(list(literals))
        else:
            # Standard chain encoding of a long clause.
            zs = [fresh() for _ in range(length - 3)]
            result.append([literals[0], literals[1], zs[0]])
            for i in range(1, length - 3):
                result.append([-zs[i - 1], literals[i + 1], zs[i]])
            result.append([-zs[-1], literals[length - 2], literals[length - 1]])

    return {"num_vars": next_var - 1, "clauses": result}
