"""Reduction from SAT to Independent Set.

The source problem is SAT in CNF as described in ``problems.py``:

    {
        "num_vars": m,
        "clauses": [[literal, ...], ...]
    }

A *literal* is an integer where the sign encodes polarity: ``+v`` means
variable ``v`` is true, ``-v`` means variable ``v`` is false.  ``v`` is a
positive integer in the range ``1..m``.

The target problem is Independent Set with instance format:

    {
        "n": n,
        "edges": [[u, v], ...],
        "k": k
    }

The reduction is the classic one used in complexity theory:

* For each clause we create a *clique* – a set of vertices where every
  pair is connected.  Each vertex corresponds to one literal occurrence
  in the clause.
* Vertices belonging to different clauses are connected **iff** the
  corresponding literals are contradictory, i.e. they refer to the same
  variable with opposite polarity.
* We ask for an independent set of size ``k`` where ``k`` equals the
  number of clauses.  Selecting one vertex from each clause that are not
  adjacent exactly corresponds to picking one literal per clause that
  does not conflict, which yields a satisfying assignment.

Edge‑case handling matches the specification of the source problem:

* An empty list of clauses is always satisfiable – we output a graph with
  ``k = 0`` (always yes).
* A formula containing an empty clause is unsatisfiable – we output a
  graph where ``k > n`` (always no).

The implementation runs in polynomial time in the size of the SAT
instance.  It builds the vertex list, then adds edges inside each clause
and contradictory edges across clauses, taking care to store each edge
once with ``u < v``.
"""

from typing import Dict, List, Tuple, Set


def _parse_literal(lit: int) -> Tuple[int, bool]:
    """Return ``(var, is_positive)`` for a literal.

    ``lit`` is an integer where the sign encodes polarity.  The absolute
    value is the variable index (1‑based).  ``is_positive`` is ``True``
    for a positive literal ``+v`` and ``False`` for a negative literal
    ``-v``.
    """
    var = abs(lit)
    return var, lit > 0


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance: dict
        SAT instance following the format described in the problem
        statement.

    Returns
    -------
    dict
        Independent Set instance.  The answer to the returned instance
        is *yes* iff the original SAT instance is satisfiable.
    """
    clauses: List[List[int]] = instance.get("clauses", [])

    # Edge case: formula contains an empty clause → unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            # Return a trivially false instance: k > n.
            return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses → always satisfiable.
    if len(clauses) == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Create a vertex for each literal occurrence.
    # vertex_id maps (clause_index, literal_index) -> global vertex number.
    vertex_id: List[List[int]] = []  # list per clause of vertex ids
    literals: List[List[int]] = []   # parallel list storing the literal value
    current_id = 0
    for ci, clause in enumerate(clauses):
        ids_row: List[int] = []
        lits_row: List[int] = []
        for lit in clause:
            ids_row.append(current_id)
            lits_row.append(lit)
            current_id += 1
        vertex_id.append(ids_row)
        literals.append(lits_row)

    n_vertices = current_id
    edges_set: Set[Tuple[int, int]] = set()

    # 1. Add edges inside each clause to form a clique.
    for ids_row in vertex_id:
        sz = len(ids_row)
        for i in range(sz):
            u = ids_row[i]
            for j in range(i + 1, sz):
                v = ids_row[j]
                if u < v:
                    edges_set.add((u, v))
                else:
                    edges_set.add((v, u))

    # 2. Add contradictory edges across different clauses.
    # For each pair of clauses (c1, c2) with c1 < c2, compare every literal.
    clause_count = len(clauses)
    for c1 in range(clause_count):
        for c2 in range(c1 + 1, clause_count):
            for idx1, lit1 in enumerate(literals[c1]):
                var1, pos1 = _parse_literal(lit1)
                for idx2, lit2 in enumerate(literals[c2]):
                    var2, pos2 = _parse_literal(lit2)
                    if var1 == var2 and pos1 != pos2:
                        u = vertex_id[c1][idx1]
                        v = vertex_id[c2][idx2]
                        if u < v:
                            edges_set.add((u, v))
                        else:
                            edges_set.add((v, u))

    # Convert edge set to required list format.
    edges_list = [[u, v] for (u, v) in sorted(edges_set)]

    return {"n": n_vertices, "edges": edges_list, "k": len(clauses)}

# The module exports only the ``reduce`` function as required by the
# evaluation harness.
