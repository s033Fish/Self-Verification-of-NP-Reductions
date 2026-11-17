"""Polynomial-time reduction from 3-SAT (SOURCE) to Exact Cover (TARGET).

Given a 3-SAT instance with variables 1..m and clauses c_1..c_n, build an
Exact Cover instance as follows.

Universe elements
-----------------
* ``s_v`` for every variable v in 1..m          (element v-1)
* ``o_{j,k}`` for every literal occurrence k in clause j
* ``c_j`` for every clause j

Sets
----
* For each variable v, two "choice" sets:
    A_v = {s_v} u { o_{j,k} : literal -v occurs at position k of clause j }
    B_v = {s_v} u { o_{j,k} : literal +v occurs at position k of clause j }
  Choosing A_v means "x_v is false" (the false literal -v is satisfied);
  choosing B_v means "x_v is true".  Exactly one of A_v, B_v must be chosen
  because both contain s_v and the sets of the cover are disjoint while s_v
  must be covered.
* For each clause j and each of its literal occurrences k:
    {c_j, o_{j,k}}   and   {o_{j,k}}.
  The singleton {o_{j,k}} is the "this literal is not the witness" option;
  the pair {c_j, o_{j,k}} is the "this literal is the witness for clause j"
  option.

Correctness
-----------
Suppose the formula is satisfiable by an assignment.  Choose B_v if x_v is
true and A_v otherwise.  Each occurrence o_{j,k} whose literal is true is
already covered by its variable's choice set; cover it with the singleton
{o_{j,k}}.  Every clause has a true literal, so for one such occurrence k*
leave o_{j,k*} uncovered by the variable set (it is a false literal, so the
chosen variable set does not contain it) and cover it with {c_j, o_{j,k*}},
which also covers c_j.  This is a valid exact cover.

Conversely, take an exact cover.  For each variable exactly one of A_v, B_v
is chosen, defining an assignment.  Each clause element c_j must be covered
by some pair {c_j, o_{j,k}}; that pair also covers o_{j,k}, so the chosen
variable set for var(literal k) does not contain o_{j,k}.  If the literal is
+v then B_v is the only set containing o_{j,k}, so B_v was not chosen, hence
x_v is false -- the literal -v is false, contradiction; thus a positive
witness literal is true.  Symmetrically a negative witness literal is true.
So every clause has a true literal and the assignment satisfies the formula.

The construction uses O(m + sum_j |clause_j|) elements and sets, hence runs
in polynomial time.  It never calls the brute-force solvers.
"""

from __future__ import annotations

from typing import Any

Instance = dict[str, Any]


def reduce(instance: Instance) -> Instance:
    """Reduce a 3-SAT instance to an Exact Cover instance."""
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Universe element ids.  Variables occupy 0..num_vars-1.
    next_element = num_vars

    # A[v] / B[v] are the "x_v false" / "x_v true" choice sets.
    # A[v] collects occurrences of the negative literal -v, B[v] those of +v.
    set_false: list[list[int]] = [[] for _ in range(num_vars + 1)]
    set_true: list[list[int]] = [[] for _ in range(num_vars + 1)]
    for v in range(1, num_vars + 1):
        set_false[v] = [v - 1]
        set_true[v] = [v - 1]

    sets: list[list[int]] = []
    for clause in clauses:
        clause_element = next_element
        next_element += 1
        for literal in clause:
            occurrence_element = next_element
            next_element += 1
            variable = abs(literal)
            if literal > 0:
                set_true[variable].append(occurrence_element)
            else:
                set_false[variable].append(occurrence_element)
            # "witness" option for this clause and "not the witness" option.
            sets.append([clause_element, occurrence_element])
            sets.append([occurrence_element])

    for v in range(1, num_vars + 1):
        sets.append(set_false[v])
        sets.append(set_true[v])

    return {"universe_size": next_element, "sets": sets}
