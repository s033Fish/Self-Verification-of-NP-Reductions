"""Reduction from 3‑SAT to Clique.

The source problem (ThreeSat) uses the instance format::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is true)
or ``-v`` (meaning variable *v* is false).  Every clause contains exactly three
distinct variables.

The target problem (Clique) expects::

    {"n": n, "edges": [[u, v], ...], "k": k}

with vertices numbered ``0 … n‑1`` and undirected edges ``[u, v]`` (no
duplicates, ``u != v``).  The answer is *yes* iff the graph contains a clique
of size at least ``k``.

Standard textbook reduction:

* For each clause ``C_i`` (``i`` from ``0`` to ``m‑1``) create three vertices –
  one for each literal in the clause.  Vertex identifiers are ``i*3 + j``
  where ``j`` is the position of the literal inside the clause.
* Connect two vertices from *different* clauses unless the corresponding
  literals are contradictory (i.e. they refer to the same variable with
  opposite signs).  This yields a graph ``G`` with ``n = 3*m`` vertices.
* Set ``k = m``.  Any clique of size ``k`` must pick exactly one vertex from
  each clause, and the non‑contradiction condition guarantees that the chosen
  literals are mutually consistent – they define a satisfying assignment.
* Conversely, a satisfying assignment selects one true literal per clause;
  the corresponding vertices form a ``k``‑clique.

Edge‑case handling:
    * If there are zero clauses the formula is trivially satisfiable.  We
      return a Clique instance with ``k = 0`` (always a yes‑instance) and an
      empty graph.
    * The reduction runs in polynomial time – ``O(m^2)`` edges at most.

The function below follows the exact formats defined in ``problems.py`` and
does not invoke any solver.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes solely for type‑checking / documentation.  The
# modules provide ``validate`` and ``is_yes`` methods, but the reduction must
# not call any exponential‑time solver.
from problems import SOURCE, TARGET


def _contradict(lit1: int, lit2: int) -> bool:
    """Return ``True`` if ``lit1`` and ``lit2`` are the same variable with
    opposite signs.

    ``lit`` is represented as a signed integer where the absolute value is the
    variable number.  Example: ``+3`` (``3``) and ``-3`` (``-3``) contradict.
    """

    return lit1 == -lit2


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to an equivalent Clique instance.

    The returned instance satisfies:
        TARGET.is_yes(returned) == SOURCE.is_yes(instance)
    and the transformation runs in polynomial time.
    """

    # Validate the source instance (will raise InvalidInstance on malformed
    # input).  This is cheap and gives clearer error messages.
    SOURCE.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    m = len(clauses)  # number of clauses

    # Edge case: empty formula – always satisfiable.
    if m == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create vertices: one per literal.  Vertex id = clause_index * 3 + pos.
    n = m * 3
    edges: List[List[int]] = []

    # For each pair of clauses, add edges between compatible literals.
    for i in range(m):
        clause_i = clauses[i]
        for j in range(i + 1, m):
            clause_j = clauses[j]
            # Compare every literal in clause_i with every literal in clause_j
            for pos_i, lit_i in enumerate(clause_i):
                id_i = i * 3 + pos_i
                for pos_j, lit_j in enumerate(clause_j):
                    if _contradict(lit_i, lit_j):
                        # contradictory literals – no edge
                        continue
                    id_j = j * 3 + pos_j
                    # Store edge with smaller id first to avoid duplicates
                    if id_i < id_j:
                        edges.append([id_i, id_j])
                    else:
                        edges.append([id_j, id_i])

    # The target instance
    target_instance: Dict[str, Any] = {
        "n": n,
        "edges": edges,
        "k": m,
    }

    # Validate the produced instance to catch programming errors early.
    TARGET.validate(target_instance)
    return target_instance

