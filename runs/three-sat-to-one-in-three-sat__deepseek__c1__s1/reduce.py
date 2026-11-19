"""Polynomial-time reduction from 3-SAT to positive 1-in-3-SAT.

Source (3-SAT): {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target (1-in-3-SAT): {"num_vars": M, "clauses": [[a, b, c], ...]}
    where every clause has exactly 3 distinct positive variables and must
    have exactly one of them true.

Construction
------------
For every source variable i (1..n) we create two target variables
    T_i = i        (intended to mean "x_i is true")
    F_i = n + i    (intended to mean "x_i is false")
and a single global variable f that is forced to be false.

1) Complement clauses: for each i, add (T_i, F_i, f).  Because f = 0 this
   forces exactly one of T_i, F_i to be true, i.e. F_i = NOT T_i.

2) False-forcing gadget (forces f = 0):
       (f, a, b), (a, b, c), (a, b, c2), (c, c2, e)
   If f = 1 then a = b = 0, hence c = 1 and c2 = 1, but then (c, c2, e)
   would have two true variables -- impossible.  So f = 0 in every
   satisfying assignment (and f = 0 is consistent: a=1,b=0,c=0,c2=0,e=1).

3) Clause gadget: a source clause (l1 v l2 v l3) requires *at least one*
   true literal, whereas a 1-in-3 clause requires *exactly one*.  For each
   source clause introduce selectors s1,s2,s3 and helpers t1,t2,t3:
       (s1, s2, s3)          -- exactly one selector is true
       (s_k, NOT l_k, t_k)   -- forbids s_k = 1 while l_k = 0
   The second clause has two true variables exactly when s_k = 1 and
   NOT l_k = 1 (i.e. l_k = 0), so it enforces s_k -> l_k.  Since exactly
   one selector is true, the gadget is satisfiable iff at least one l_k is
   true.  Here NOT l_k is the complementary target variable (F_v for a
   positive literal +v, T_v for a negative literal -v).

The result is yes iff the source is yes, and the construction uses
O(n + m) variables and clauses, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a positive 1-in-3-SAT instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    n = num_vars
    m = len(clauses)

    # Target variable numbering.
    #   T_i = i, F_i = n + i   for i = 1..n
    #   f, a, b, c, c2, e      = 2n+1 .. 2n+6
    #   clause j auxiliaries   = 2n+6 + 6j + 1 .. + 6
    f = 2 * n + 1
    a = 2 * n + 2
    b = 2 * n + 3
    c = 2 * n + 4
    c2 = 2 * n + 5
    e = 2 * n + 6

    out_clauses = []

    # 1) Force F_i = NOT T_i using the global false variable f.
    for i in range(1, n + 1):
        out_clauses.append([i, n + i, f])

    # 2) Force f = 0.
    out_clauses.append([f, a, b])
    out_clauses.append([a, b, c])
    out_clauses.append([a, b, c2])
    out_clauses.append([c, c2, e])

    # 3) One gadget per source clause.
    base = 2 * n + 6
    for j, clause in enumerate(clauses):
        s1 = base + 6 * j + 1
        s2 = base + 6 * j + 2
        s3 = base + 6 * j + 3
        t1 = base + 6 * j + 4
        t2 = base + 6 * j + 5
        t3 = base + 6 * j + 6

        out_clauses.append([s1, s2, s3])

        for s_k, t_k, lit in ((s1, t1, clause[0]),
                              (s2, t2, clause[1]),
                              (s3, t3, clause[2])):
            v = abs(lit)
            if lit > 0:
                pos = v          # T_v
                neg = n + v      # F_v = NOT T_v
            else:
                pos = n + v      # F_v
                neg = v          # T_v = NOT F_v
            # (s_k, NOT l_k, t_k) enforces s_k -> pos.
            out_clauses.append([s_k, neg, t_k])

    total_vars = 2 * n + 6 + 6 * m
    return {"num_vars": total_vars, "clauses": out_clauses}
