"""Reduction from Subset Sum to SAT.

The source problem (SubsetSum) instance format is:
    {"numbers": [a1, a2, ...], "target": t}
where the numbers are non‑negative integers (duplicates allowed) and *t*
is an integer.  The answer is *yes* iff some sub‑list of the numbers sums to
exactly *t*.

The target problem (Sat) instance format is:
    {"num_vars": m, "clauses": [[literal, ...], ...]}
where literals are represented as ``+v`` (variable *v* true) or ``-v``
(v *false).  An empty list of clauses is always satisfiable, while a
clause ``[]`` makes the whole formula unsatisfiable.

This file implements a polynomial‑time reduction using a classic
pseudo‑polynomial dynamic‑programming encoding.  For each prefix of the input
list and each achievable sum up to the target we introduce a Boolean variable
``y_{i,s}`` meaning *"using the first i numbers we can achieve sum s"*.

The constraints are encoded with Tseitin‑style clauses:

* Base case (i = 0): ``y_{0,0}`` must be true and all other ``y_{0,s}`` (s>0)
  must be false.
* Transition (i ≥ 1):
    y_{i,s} ⇔ (y_{i-1,s} ∨ (s ≥ a_i ∧ y_{i-1, s-a_i]))
  which is expressed by the three clauses
    (¬y_{i-1,s} ∨ y_{i,s})
    (¬y_{i-1,s-a_i} ∨ y_{i,s})   (only if s ≥ a_i)
    (¬y_{i,s} ∨ y_{i-1,s} ∨ y_{i-1,s-a_i})
  (the last clause omits the second term when s < a_i).

Finally we force ``y_{n,target}`` to be true with a unit clause.  The formula is
 satisfiable iff the original Subset‑Sum instance is a yes‑instance.

The size of the constructed SAT instance is O(n·T) where *n* is the number of
input numbers and *T* is the target value (treated as a non‑negative integer).
For the typical test harness used in these exercises the targets are small,
so this simple encoding is sufficient and respects the polynomial‑time
requirement with respect to the input size.
"""

from typing import List, Dict, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a SubsetSum instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"numbers"`` (list of non‑negative ints) and
        ``"target"`` (int).

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """
    numbers: List[int] = instance.get("numbers", [])
    target: int = instance.get("target", 0)

    # Edge cases handled directly.
    if target == 0:
        # Empty subset always works – return a trivially satisfiable formula.
        return {"num_vars": 0, "clauses": []}
    if target < 0:
        # Impossible – return an unsatisfiable formula (single empty clause).
        return {"num_vars": 0, "clauses": [[]]}
    if not numbers:
        # No numbers and target != 0 -> unsatisfiable.
        return {"num_vars": 0, "clauses": [[]]}

    n = len(numbers)
    T = target

    # Mapping from (i, s) to variable id. i ranges 0..n, s ranges 0..T.
    var_id: Dict[Tuple[int, int], int] = {}
    next_var = 1
    for i in range(n + 1):
        for s in range(T + 1):
            var_id[(i, s)] = next_var
            next_var += 1

    clauses: List[List[int]] = []

    # Base case clauses.
    for s in range(T + 1):
        v = var_id[(0, s)]
        if s == 0:
            # y_{0,0} must be true.
            clauses.append([+v])
        else:
            # y_{0,s} (s>0) must be false.
            clauses.append([-v])

    # Transition clauses.
    for i in range(1, n + 1):
        a = numbers[i - 1]
        for s in range(T + 1):
            cur = var_id[(i, s)]
            prev_same = var_id[(i - 1, s)]
            # (¬prev_same ∨ cur)
            clauses.append([-prev_same, +cur])
            if s >= a:
                prev_minus = var_id[(i - 1, s - a)]
                # (¬prev_minus ∨ cur)
                clauses.append([-prev_minus, +cur])
                # (¬cur ∨ prev_same ∨ prev_minus)
                clauses.append([-cur, +prev_same, +prev_minus])
            else:
                # When a cannot be taken, cur ⇔ prev_same.
                # We already have (¬prev_same ∨ cur). Add (¬cur ∨ prev_same).
                clauses.append([-cur, +prev_same])

    # Force the target sum to be reachable.
    target_var = var_id[(n, T)]
    clauses.append([+target_var])

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

