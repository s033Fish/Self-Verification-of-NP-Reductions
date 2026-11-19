"""Reduction from 3‑SAT to Dominating Set.

The source problem (ThreeSat) encodes a Boolean formula in conjunctive normal
form where each clause has exactly three literals on distinct variables.  The
target problem (DominatingSet) asks for a set of vertices of size at most ``k``
that dominates the whole undirected graph.

We implement the classic polynomial‑time reduction described in many textbooks:

* For each variable ``x_i`` we create two vertices ``t_i`` (meaning *x_i is
  true*) and ``f_i`` (meaning *x_i is false*) and connect them with an edge.
  Selecting exactly one of the two vertices dominates both vertices of the
  pair.
* For each clause ``C_j = (ℓ_1 ∨ ℓ_2 ∨ ℓ_3)`` we create a single vertex ``c_j``
  and connect it to the vertex that represents the *satisfying* literal of the
  clause – i.e. to ``t_i`` if the literal is ``+i`` and to ``f_i`` if the literal
  is ``-i``.

If the formula is satisfiable, picking for every variable the vertex that
corresponds to the truth assignment yields a dominating set of size exactly the
number of variables ``m``.  Every clause vertex is adjacent to at least one
selected variable vertex, and each variable vertex dominates its partner.

Conversely, any dominating set of size at most ``m`` must contain at least one
vertex from each variable pair (otherwise one of the two would be undominated).
Thus it contains exactly ``m`` vertices, one per variable.  If a clause is not
satisfied by the implied assignment, none of its three neighbours is selected,
so the clause vertex would be undominated – a contradiction.  Hence the
dominating set of size ``m`` exists *iff* the formula is satisfiable.

The reduction runs in time linear in the size of the formula and produces a
graph with ``2·m + |clauses|`` vertices and ``m + 3·|clauses|`` edges.  The
parameter ``k`` of the Dominating Set instance is set to ``m``.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a DominatingSet instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑element lists of ints).  The format follows the docstring of the
        ``ThreeSat`` class in ``problems.py``.

    Returns
    -------
    dict
        A Dominating Set instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex numbering:
    #   true literal for variable i (0‑based) -> 2*i
    #   false literal for variable i                -> 2*i + 1
    # Clause vertices start after the 2*m variable vertices.
    edges: List[List[int]] = []

    # Variable gadgets: an edge between the true and false vertex of each var.
    for i in range(m):
        edges.append([2 * i, 2 * i + 1])

    clause_offset = 2 * m
    for idx, clause in enumerate(clauses):
        clause_vertex = clause_offset + idx
        # Connect the clause vertex to the vertex that would make the literal
        # true.
        for lit in clause:
            var = abs(lit) - 1  # variables are 1‑based in the input.
            if lit > 0:
                # Positive literal -> true vertex.
                var_vertex = 2 * var
            else:
                # Negative literal -> false vertex.
                var_vertex = 2 * var + 1
            edges.append([clause_vertex, var_vertex])

    n = 2 * m + len(clauses)
    k = m  # size bound as argued in the documentation above.

    return {"n": n, "edges": edges, "k": k}

