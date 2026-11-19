"""Reduction from Exact Cover to Subset Sum.

The source problem (ExactCover) is defined by an instance dictionary:

    {"universe_size": u, "sets": [[element, ...], ...]}

The goal is to decide whether a sub‑collection of the given sets forms an
exact cover of the universe {0,…,u‑1}: the chosen sets must be pairwise
disjoint and their union must be the whole universe.

The target problem (SubsetSum) expects an instance of the form:

    {"numbers": [a1, a2, ...], "target": t}

We encode each set as a number in a mixed‑radix (actually a single large base)
representation.  Let ``m`` be the number of sets and choose ``base = m + 1``.
Because ``base`` is larger than the maximum possible multiplicity of any
universe element (an element can appear in at most ``m`` sets), the sum of any
selection of numbers will never cause a carry when expressed in this base.

For a set ``S`` we create the number:

    num(S) = Σ_{i ∈ S} base**i

The target value is the number whose base‑``base`` representation has a digit
``1`` in every position ``0 … u‑1``:

    target = Σ_{i=0}^{u-1} base**i

Selecting a collection of sets corresponds to adding their numbers.  Because
there are no carries, the digit in position ``i`` of the sum equals the count
of selected sets that contain element ``i``.  Hence the sum equals ``target``
iff each element appears exactly once – i.e. the selected sets form an exact
cover.  Over‑coverage (digit > 1) cannot be compensated by carries, so such a
selection never reaches the target.  Under‑coverage (digit 0) also prevents
equality.  Therefore the reduction is correct.

Edge cases:
* ``u = 0`` → ``target = 0``.  Subset‑Sum with target 0 is always a YES
  instance, matching the Exact‑Cover definition.
* Empty sets contribute ``0`` to the numbers list; they are harmless because
  they do not affect the sum.

The reduction runs in polynomial time: we compute ``base`` and then raise it
to powers up to ``u‑1`` (at most linear in the input size) and construct the
list of numbers with a simple loop.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce an ExactCover instance to a SubsetSum instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"universe_size"`` (int) and ``"sets"`` (list
        of list of ints) as described in the problem statement.

    Returns
    -------
    dict
        A SubsetSum instance with keys ``"numbers"`` and ``"target"``.
    """
    u: int = instance.get("universe_size", 0)
    sets: List[List[int]] = instance.get("sets", [])

    m = len(sets)
    # Choose a base larger than the maximum possible multiplicity of any
    # element to avoid carries during addition.
    base = m + 1 if m >= 0 else 1  # m is non‑negative; fallback to 1 for safety

    # Pre‑compute powers of the base: pow_base[i] = base**i for i in 0..u-1.
    # For u == 0 the list is empty, yielding target = 0.
    pow_base: List[int] = []
    cur = 1
    for _ in range(u):
        pow_base.append(cur)
        cur *= base

    numbers: List[int] = []
    for s in sets:
        val = 0
        for elem in s:
            if 0 <= elem < u:
                val += pow_base[elem]
        numbers.append(val)

    target = sum(pow_base)
    return {"numbers": numbers, "target": target}

