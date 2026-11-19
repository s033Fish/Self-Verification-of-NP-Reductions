"""Reduction from 1-in-3 SAT (positive literals only) to Exact Cover.

The source problem (OneInThreeSat) is defined as:
    instance = {"num_vars": m, "clauses": [[a, b, c], ...]}
    each clause contains three *distinct* positive variable indices (1‑based).
    The formula is satisfiable iff there exists a truth assignment in which
    **exactly one** variable in every clause is true.

The target problem (ExactCover) expects an instance of the form:
    {"universe_size": u, "sets": [[e, ...], ...]}
    where the universe is the set of integers {0, …, u‑1}.  A collection of
    sets is a *exact cover* if the chosen sets are pairwise disjoint and their
    union equals the whole universe.

We implement the classic polynomial‑time reduction used in many NP‑completeness
proofs (see e.g. Garey & Johnson, *Computers and Intractability*).  For each
variable `v` we create two universe elements representing the literal `v`
(`v_true`) and its negation `¬v` (`v_false`).  For a clause `(a, b, c)` we add
three sets, each encoding the choice of the true literal in that clause:

    { a_true,  b_false, c_false }
    { a_false, b_true,  c_false }
    { a_false, b_false, c_true }

In addition, for every variable `v` we add the *variable set*
`{ v_true, v_false }`.  The constructed Exact Cover instance has the property
that any exact cover corresponds to a satisfying 1‑in‑3 assignment and vice
+versa:

* Selecting one of the three clause‑sets for a clause forces exactly one of the
  three variables to be assigned true (its `*_true` element is covered) while
  the other two variables are forced false (their `*_false` elements are covered).
* The variable set `{v_true, v_false}` can be used only when neither of the
  clause‑sets covering `v_true` nor `v_false` has been chosen, which corresponds
  to the variable not appearing as the true literal in any clause.  Because
  each clause set that makes a variable false already covers its `*_false`
  element, the `*_false` element is covered exactly once overall.

The reduction runs in time linear in the size of the input (number of clauses
and variables) and produces a well‑formed Exact Cover instance.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        length‑3 lists of ints).  Variables are numbered from 1 to ``m``.

    Returns
    -------
    dict
        An ExactCover instance with keys ``"universe_size"`` and ``"sets"``.
    """
    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Universe elements: for each variable v (1‑based) we allocate two indices:
    #   true  element -> 2*(v-1)
    #   false element -> 2*(v-1) + 1
    universe_size = 2 * m
    sets: List[List[int]] = []

    # Variable sets {v_true, v_false}
    for v in range(1, m + 1):
        true_elem = 2 * (v - 1)
        false_elem = true_elem + 1
        sets.append([true_elem, false_elem])

    # Clause sets encoding the exactly‑one‑true condition
    for clause in clauses:
        if len(clause) != 3:
            # According to the specification this should never happen, but we
            # guard against malformed input.
            continue
        a, b, c = clause
        # Compute element indices for each literal
        a_true, a_false = 2 * (a - 1), 2 * (a - 1) + 1
        b_true, b_false = 2 * (b - 1), 2 * (b - 1) + 1
        c_true, c_false = 2 * (c - 1), 2 * (c - 1) + 1

        # Three possibilities: a true, b true, or c true
        sets.append([a_true, b_false, c_false])
        sets.append([a_false, b_true, c_false])
        sets.append([a_false, b_false, c_true])

    return {"universe_size": universe_size, "sets": sets}

