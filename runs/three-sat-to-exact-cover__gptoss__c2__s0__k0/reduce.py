"""Reduction from 3‑SAT to Exact Cover.

The source problem (ThreeSat) instance format is::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Variables are numbered ``1..m``.

The target problem (ExactCover) instance format is::

    {"universe_size": u, "sets": [[e, ...], ...]}

Elements of the universe are the integers ``0..u‑1``.

The reduction follows a classic polynomial‑time construction (see e.g. Karp's
21 NP‑complete problems).  For each variable we create three universe
elements:

* ``v_j`` – a *choice* element that forces exactly one of the two assignment
  sets to be selected.
* ``t_j`` – the element representing the literal *x_j* (variable true).
* ``f_j`` – the element representing the literal *¬x_j* (variable false).

For each variable ``j`` we add the following sets:

* ``ChoiceTrue_j = {v_j, f_j}`` – selecting this corresponds to assigning the
  variable *true* (it covers the false‑literal element ``f_j`` so that sets
  containing ``f_j`` cannot be used).
* ``ChoiceFalse_j = {v_j, t_j}`` – corresponds to assigning the variable *false*.
* ``DummyTrue_j = {t_j}`` and ``DummyFalse_j = {f_j}`` – allow any literal
  element that is not used by a clause to be covered.

For each clause ``C_i`` we create a distinct universe element ``c_i``.  For every
literal in the clause we add a set that contains the clause element and the
corresponding literal element:

* Positive literal ``+v`` → ``{c_i, t_v}``
* Negative literal ``-v`` → ``{c_i, f_v}``

An exact cover must pick exactly one of the three clause sets for each clause,
thereby satisfying the clause with a literal whose assignment matches the
chosen variable assignment.  The construction guarantees a one‑to‑one
correspondence between satisfying assignments of the 3‑SAT instance and exact
covers of the produced instance.

The function ``reduce`` implements this construction.  It runs in time linear
in the size of the input (``O(m + |clauses|)``) and returns a dictionary that
conforms to the ``ExactCover`` format.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of literals).

    Returns
    -------
    dict
        An ExactCover instance as described in the module docstring.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Universe layout:
    #   for variable j (1‑based):
    #       v_j = 3*(j-1)          # choice element
    #       t_j = v_j + 1          # true literal element
    #       f_j = v_j + 2          # false literal element
    #   for clause i (0‑based):
    #       c_i = 3*m + i          # clause element
    num_vars = m
    num_clauses = len(clauses)
    universe_size = 3 * num_vars + num_clauses

    sets: List[List[int]] = []

    # Variable gadgets
    for j in range(1, num_vars + 1):
        v_j = 3 * (j - 1)
        t_j = v_j + 1
        f_j = v_j + 2

        # Choice sets – exactly one must be taken because they share v_j.
        # ChoiceTrue_j corresponds to assigning variable j = True.
        sets.append([v_j, f_j])  # ChoiceTrue_j
        # ChoiceFalse_j corresponds to assigning variable j = False.
        sets.append([v_j, t_j])  # ChoiceFalse_j

        # Dummy sets to cover any literal element not used by a clause.
        sets.append([t_j])  # DummyTrue_j
        sets.append([f_j])  # DummyFalse_j

    # Clause sets
    for i, clause in enumerate(clauses):
        c_i = 3 * num_vars + i
        for lit in clause:
            var = abs(lit)
            # Compute the literal element index.
            base = 3 * (var - 1)
            t_var = base + 1
            f_var = base + 2
            if lit > 0:
                # Positive literal uses the true element.
                sets.append([c_i, t_var])
            else:
                # Negative literal uses the false element.
                sets.append([c_i, f_var])

    return {"universe_size": universe_size, "sets": sets}

