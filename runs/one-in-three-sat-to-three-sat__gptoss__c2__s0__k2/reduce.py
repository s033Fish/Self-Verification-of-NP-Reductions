"""Reduction from 1-in-3 SAT to 3-SAT.

The source problem (OneInThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[a, b, c], ...]}

where each clause contains three *positive* variable indices.  An
assignment satisfies the formula iff **exactly one** variable in each
clause is true.

The target problem (ThreeSat) expects instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal is a signed integer – a positive integer ``v``
represents the literal *v* (variable *v* is true) and a negative integer
``-v`` represents the literal *¬v*.  Each clause must contain three
different variables.

The classic way to enforce "exactly one" with 3‑CNF is to require

* at least one true:            (a ∨ b ∨ c)
* at most one true: pairwise   (¬a ∨ ¬b), (¬a ∨ ¬c), (¬b ∨ ¬c)

The pairwise constraints are binary clauses.  To embed them into a
3‑CNF we use a simple gadget: for a binary clause (¬x ∨ ¬y) introduce a
fresh variable ``p`` and add the two 3‑clauses ``[ -x, -y,  p]`` and
``[ -x, -y, -p]``.  These two clauses are simultaneously satisfiable iff
the original binary clause is satisfied – if both ``x`` and ``y`` were
true, the first clause would demand ``p`` to be true while the second
would demand ``p`` to be false, a contradiction.

Putting everything together, for each source clause (a, b, c) we emit
seven target clauses:

1. ``[ a,  b,  c]``                       – at least one true
2. For each unordered pair (x, y) in {(a,b), (a,c), (b,c)}:
   * introduce a fresh variable ``p``
   * emit ``[ -x, -y,  p]``
   * emit ``[ -x, -y, -p]``

The construction runs in linear time and uses a constant number of
new variables per source clause, therefore it is polynomial.

The ``reduce`` function below implements this transformation.
"""

from typing import List, Dict


def reduce(instance: Dict) -> Dict:
    """Reduce a OneInThreeSat instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined
        for the source problem.

    Returns
    -------
    dict
        A ThreeSat instance preserving satisfiability.
    """

    m = instance.get("num_vars", 0)
    source_clauses: List[List[int]] = instance.get("clauses", [])

    # The target will start with the original variables.
    next_var = m + 1  # next fresh variable index
    target_clauses: List[List[int]] = []

    for clause in source_clauses:
        if len(clause) != 3:
            # Defensive: ignore malformed clauses (should not happen)
            continue
        a, b, c = clause
        # 1. At least one true
        target_clauses.append([a, b, c])

        # 2. Pairwise at-most-one constraints using the gadget described above
        pairs = [(a, b), (a, c), (b, c)]
        for x, y in pairs:
            p = next_var
            next_var += 1
            # (¬x ∨ ¬y ∨  p) and (¬x ∨ ¬y ∨ ¬p)
            target_clauses.append([-x, -y, p])
            target_clauses.append([-x, -y, -p])

    # Construct the resulting instance dictionary.
    result = {
        "num_vars": next_var - 1,  # highest variable index used
        "clauses": target_clauses,
    }
    return result

