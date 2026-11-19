"""Reduction from OneInThreeSat to ExactCover.

Given an instance of 1-in-3 SAT with m variables and a list of clauses
(each clause is a list of three distinct variable indices), we construct an
Exact Cover instance.

Construction:
- Universe elements 0..m-1 correspond to the variables.
- Universe elements m..m+|clauses|-1 correspond to the clauses.
- For each variable i (1-indexed) we create two sets:
    * False set: {i-1}
    * True set:  {i-1} ∪ {m + j | variable i appears in clause j}
  Selecting the true set covers the variable element and all clause
  elements where that variable appears, thereby satisfying those clauses.
  Selecting the false set covers only the variable element.
- An exact cover must pick exactly one of the two sets for each variable
  (to cover the variable element) and must cover each clause element exactly
  once, which forces exactly one true variable per clause.

This reduction runs in time polynomial in the size of the input.
"""

def reduce(instance):
    """Reduce a OneInThreeSat instance to an ExactCover instance.

    Parameters
    ----------
    instance : dict
        A dictionary with keys:
        - "num_vars": int, number of variables m.
        - "clauses": list of lists, each inner list contains three distinct
          variable indices (1‑based).

    Returns
    -------
    dict
        An ExactCover instance with keys:
        - "universe_size": int, m + number of clauses.
        - "sets": list of lists, each inner list is a set of universe
          elements (as integers).
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Map each variable to the list of clause indices it appears in.
    var_to_clauses = {var: [] for var in range(1, m + 1)}
    for idx, clause in enumerate(clauses):
        for var in clause:
            var_to_clauses[var].append(idx)

    sets = []
    for var in range(1, m + 1):
        var_elem = var - 1  # universe element for this variable
        # False assignment set (covers only the variable element)
        sets.append([var_elem])
        # True assignment set (covers variable element and all clause elements
        # where this variable appears)
        true_set = [var_elem] + [m + clause_idx for clause_idx in var_to_clauses[var]]
        sets.append(true_set)

    universe_size = m + num_clauses
    return {"universe_size": universe_size, "sets": sets}

# The module provides only the reduce function as required.
