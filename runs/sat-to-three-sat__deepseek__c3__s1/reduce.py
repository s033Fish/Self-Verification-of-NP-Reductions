"""Polynomial-time reduction from SAT (arbitrary CNF) to 3-SAT.

The reduction keeps the original variables 1..m and introduces fresh
auxiliary variables (numbered m+1, m+2, ...) to turn every source clause
into a conjunction of 3-literal clauses over 3 distinct variables.

For a source clause C (a list of literals):

  * Drop C if it is a tautology (contains both v and -v): it is always true.
  * Remove repeated literals.  After this, distinct literals have distinct
    underlying variables (a repeated variable would have to be a tautology).
  * Let L be the resulting list of literals, n = len(L).

    n == 0 : C is the empty clause and is unsatisfiable.  Emit all 8
             clauses over three fresh variables a, b, c (every sign
             combination), which is unsatisfiable.
    n == 1 : (l)  <=>  (l v a v b) & (l v ~a v b) & (l v a v ~b) & (l v ~a v ~b)
    n == 2 : (l1 v l2) <=> (l1 v l2 v a) & (l1 v l2 v ~a)
    n == 3 : already a 3-clause, keep it.
    n >= 4: standard chain with fresh variables a_1..a_{n-3}:
              (l1 v l2 v a1)
              (~a1 v l3 v a2)
              ...
              (~a_{n-4} v l_{n-2} v a_{n-3})
              (~a_{n-3} v l_{n-1} v ln)

Every emitted clause has 3 literals on 3 distinct variables, so the result
is a valid 3-SAT instance.  The construction is satisfiability-preserving
and runs in time polynomial in the size of the input.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a SAT instance to a 3-SAT instance (same yes/no answer)."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    out: list[list[int]] = []
    next_var = num_vars + 1

    def fresh() -> int:
        nonlocal next_var
        var = next_var
        next_var += 1
        return var

    for clause in clauses:
        # Remove duplicates and detect tautologies in one pass.
        seen: set[int] = set()
        literals: list[int] = []
        tautology = False
        for literal in clause:
            if -literal in seen:
                tautology = True
                break
            if literal not in seen:
                seen.add(literal)
                literals.append(literal)
        if tautology:
            # Always satisfied: contributes nothing.
            continue

        n = len(literals)
        if n == 0:
            # Empty clause: emit an unsatisfiable 3-CNF over fresh vars.
            a, b, c = fresh(), fresh(), fresh()
            for sa in (a, -a):
                for sb in (b, -b):
                    for sc in (c, -c):
                        out.append([sa, sb, sc])
        elif n == 1:
            (l,) = literals
            a, b = fresh(), fresh()
            out.append([l, a, b])
            out.append([l, -a, b])
            out.append([l, a, -b])
            out.append([l, -a, -b])
        elif n == 2:
            l1, l2 = literals
            a = fresh()
            out.append([l1, l2, a])
            out.append([l1, l2, -a])
        elif n == 3:
            out.append(literals)
        else:
            aux = [fresh() for _ in range(n - 3)]
            out.append([literals[0], literals[1], aux[0]])
            for i in range(1, n - 3):
                out.append([-aux[i - 1], literals[i + 1], aux[i]])
            out.append([-aux[-1], literals[n - 2], literals[n - 1]])

    if not out:
        # No clauses: satisfiable for any number of variables.
        return {"num_vars": num_vars, "clauses": []}

    return {"num_vars": max(next_var - 1, 3), "clauses": out}
