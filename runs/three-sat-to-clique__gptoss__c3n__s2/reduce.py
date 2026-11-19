"""Reduction from 3‑SAT to Clique.

The source problem is :class:`ThreeSat` defined in ``problems.py``. An
instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each literal is an integer ``+v`` (variable *v* is true) or ``-v``
(variable *v* is false). Every clause contains exactly three literals on
three different variables.

The target problem is :class:`Clique`. An instance is a dictionary
``{"n": n, "edges": [[u, v], ...], "k": k}`` where vertices are ``0..n‑1``.
The answer is *yes* iff the graph contains a clique of size **at least**
``k``.

Standard textbook reduction:

* For each clause create three vertices – one for each literal.
* Connect two vertices from **different** clauses iff the corresponding
  literals are *compatible*, i.e. they are not contradictory (they do not
  refer to the same variable with opposite polarity).
* Set ``k`` to the number of clauses.

If the original formula is satisfiable, pick a true literal from each
clause; the chosen vertices are pairwise compatible and therefore form a
clique of size ``k``. Conversely, a clique of size ``k`` must contain at
most one vertex from each clause (no edges inside a clause) and the
corresponding literals cannot contradict each other, yielding a satisfying
assignment.

Edge case – an empty formula (no clauses) is always satisfiable. We map
it to a trivial Clique instance with ``k = 0``; by definition any graph
answers *yes* for ``k <= 0``.

The function runs in polynomial time in the size of the 3‑SAT instance –
``O(c^2)`` where ``c`` is the number of clauses (at most ``3c`` vertices).
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, Clique


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the format of :class:`ThreeSat`.

    Returns
    -------
    dict
        An instance of :class:`Clique` such that the answer to the Clique
        instance is *yes* iff the answer to the original 3‑SAT instance is
        *yes*.
    """
    # Validate the source instance – will raise InvalidInstance on error.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    c = len(clauses)

    # Empty formula – always satisfiable. Return a trivial Clique instance.
    if c == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for each literal in each clause.
    # Vertex id = clause_index * 3 + literal_index (0,1,2).
    n = c * 3
    edges: List[List[int]] = []

    # Pre‑compute the literal for each vertex for quick lookup.
    vertex_literal: List[int] = []  # index -> literal
    for clause in clauses:
        for lit in clause:
            vertex_literal.append(lit)

    # Add edges between vertices of different clauses when literals are compatible.
    for i in range(n):
        clause_i = i // 3
        lit_i = vertex_literal[i]
        for j in range(i + 1, n):
            clause_j = j // 3
            if clause_i == clause_j:
                # No edges inside the same clause – would allow picking two
                # literals from one clause.
                continue
            lit_j = vertex_literal[j]
            # Incompatible if they refer to the same variable with opposite sign.
            if abs(lit_i) == abs(lit_j) and lit_i != lit_j:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": c}

