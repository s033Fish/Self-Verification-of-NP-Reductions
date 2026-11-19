"""Polynomial-time reduction from 3-SAT to Subset Sum.

Encoding
--------
Let the formula have m variables and n clauses.  Work in base 10 (any base
larger than 5 works, since a clause digit accumulates at most 3 from the
variable numbers plus 2 from the slack numbers).  Use n low-order digits,
one per clause, and m higher digits, one per variable:

    digit position j        (0 <= j < n)  -> clause j
    digit position n + i    (0 <= i < m)  -> variable i+1

Numbers
-------
For each variable v (1..m) create two numbers:

    pos[v] = 10**(n + v - 1) + sum(10**j for clauses j containing +v)
    neg[v] = 10**(n + v - 1) + sum(10**j for clauses j containing -v)

For each clause j create two slack numbers:

    s1[j] = 10**j
    s2[j] = 2 * 10**j

Target
------
    target = sum(10**(n + v - 1) for v in 1..m) + 4 * sum(10**j for j < n)

Correctness
-----------
No carries can occur because every digit of every number is at most 3 (a
clause has 3 literals) and the target digits are at most 4.  Each variable
digit of the target is 1, so exactly one of pos[v], neg[v] must be picked:
this is the truth assignment of v.  At clause digit j the chosen variable
numbers contribute the number of true literals of clause j (0..3), and the
slacks contribute either 0, 1, 2 or 3.  The target digit 4 is reachable
exactly when the variable contribution is at least 1 (if it were 0 the
slacks could contribute at most 3), i.e. iff clause j is satisfied.
Hence a subset sums to the target exactly when the formula is satisfiable.

The construction uses O(m + n) numbers, each with O(m + n) digits, so it is
polynomial in the instance size.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Subset Sum instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    # Base-10 place values.
    clause_place = [10 ** j for j in range(n)]
    var_place = [10 ** (n + i) for i in range(num_vars)]

    numbers = []

    # One number per literal polarity of each variable.
    for v in range(1, num_vars + 1):
        pos = var_place[v - 1]
        neg = var_place[v - 1]
        for j, clause in enumerate(clauses):
            if v in clause:
                pos += clause_place[j]
            elif -v in clause:
                neg += clause_place[j]
        numbers.append(pos)
        numbers.append(neg)

    # Two slack numbers per clause: 1 and 2 in the clause's digit.
    for j in range(n):
        numbers.append(clause_place[j])
        numbers.append(2 * clause_place[j])

    target = sum(var_place) + 4 * sum(clause_place)
    return {"numbers": numbers, "target": target}
