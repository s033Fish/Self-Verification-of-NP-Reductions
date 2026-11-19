"""Polynomial-time reduction from 3-SAT to Subset Sum.

Construction
------------
Let the 3-SAT instance have ``m`` variables and ``k`` clauses.  Choose the
base ``B = 10``.  Any base ``B > 5`` works: the largest possible sum in a
single digit column is 3 variable literals + 2 slack numbers = 5, so there
are no carries and every digit column behaves independently.

Digit positions of the base-B representation:

  * positions ``0 .. k-1``   -- one position per clause
  * positions ``k .. k+m-1`` -- one position per variable

Target:

  * digit 3 in every clause position
  * digit 1 in every variable position

Numbers:

  * For each variable ``i`` (1-based) two numbers::

        T_i = B**(k+i-1) + sum of B**j over clauses j containing +i
        F_i = B**(k+i-1) + sum of B**j over clauses j containing -i

    (``T_i`` is chosen when variable ``i`` is set true, ``F_i`` when false.)

  * For each clause ``j`` two slack numbers, both equal to ``B**j``.

Correctness
-----------
A variable position ``i`` receives 1 only from ``T_i`` and ``F_i`` (every
other number has 0 there).  Since the target digit is 1 and there are no
carries, any solution must pick exactly one of ``T_i``/``F_i`` for every
variable, which yields a truth assignment.

For a clause position ``j`` let ``v_j`` be the contribution of the chosen
variable numbers (one per literal of the clause, so ``v_j`` in {0,1,2,3})
and ``s_j`` the contribution of the two slacks (``s_j`` in {0,1,2}).  The
target digit is 3, so ``v_j + s_j = 3``.  If ``v_j = 0`` then ``s_j <= 2``
cannot reach 3, hence ``v_j >= 1``: at least one literal of the clause is
true.  Conversely, if ``v_j >= 1`` we can always pad to 3 (``v_j=1`` use
both slacks, ``v_j=2`` use one, ``v_j=3`` use none).

Therefore the produced Subset Sum instance is a yes instance exactly when
the 3-SAT formula is satisfiable.

The reduction builds ``2m + 2k`` numbers, each with at most ``m + k``
base-B digits, in ``O(m*k)`` time, so it runs in polynomial time.
"""


def reduce(instance):
    """Reduce a 3-SAT instance to a Subset Sum instance.

    ``instance`` is ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` and
    the result is ``{"numbers": [...], "target": t}``.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = num_vars
    k = len(clauses)

    base = 10

    # Precompute powers of the base (positions 0 .. k+m-1).
    powers = [1] * (k + m + 1)
    for p in range(1, k + m + 1):
        powers[p] = powers[p - 1] * base

    # Target: 3 in each clause position, 1 in each variable position.
    target = 0
    for j in range(k):
        target += 3 * powers[j]
    for i in range(m):
        target += powers[k + i]

    numbers = []

    # One true-number and one false-number per variable.
    for i in range(1, m + 1):
        var_digit = powers[k + i - 1]
        t_num = var_digit
        f_num = var_digit
        for j, clause in enumerate(clauses):
            for literal in clause:
                if literal == i:
                    t_num += powers[j]
                elif literal == -i:
                    f_num += powers[j]
        numbers.append(t_num)
        numbers.append(f_num)

    # Two slack numbers of value 1 per clause position.
    for j in range(k):
        numbers.append(powers[j])
        numbers.append(powers[j])

    return {"numbers": numbers, "target": target}
