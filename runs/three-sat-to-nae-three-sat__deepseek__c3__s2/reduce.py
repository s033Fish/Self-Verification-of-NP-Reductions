"""Polynomial-time reduction from 3-SAT to NAE-3-SAT.

Construction
------------
Let the 3-SAT instance have variables 1..m and clauses C_1..C_n.

Introduce one global "anchor" variable s = m+1 and, for each clause C_i,
one auxiliary variable t_i = m+1+i.

For a clause C_i = (l1 v l2 v l3) emit two NAE-3 clauses:

    NAE(l1, l2, t_i)        and        NAE(l3, s, ~t_i)

Correctness
-----------
Key identity: for any literals a,b,c,d,

    NAE4(a,b,c,d)  <=>  exists t:  NAE3(a,b,t) and NAE3(c,d,~t).

(If a!=b take t=c; if a=b take t=~a. Conversely if a=b=c=d then the
first NAE3 forces t!=a while the second forces t=a.)

Hence the emitted pair for clause i is satisfiable (over t_i) exactly when
NAE4(l1,l2,l3,s) holds.  NAE constraints are invariant under complementing
every variable, so a satisfying assignment exists with s=false iff one
exists at all.  With s=false, NAE4(l1,l2,l3,false) means "not all of
l1,l2,l3,false are equal", i.e. at least one of l1,l2,l3 is true -- exactly
the original 3-SAT clause.  Therefore the NAE-3-SAT instance is satisfiable
iff the 3-SAT instance is.

The construction uses m + 1 + n variables and 2n clauses, so it runs in
polynomial time and never calls a solver.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to an equisatisfiable NAE-3-SAT instance."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    n = len(clauses)

    s = m + 1  # global anchor variable
    out_clauses = []
    for i, clause in enumerate(clauses):
        l1, l2, l3 = clause
        t = m + 2 + i  # fresh auxiliary variable for this clause
        out_clauses.append([l1, l2, t])
        out_clauses.append([l3, s, -t])

    return {"num_vars": m + 1 + n, "clauses": out_clauses}
