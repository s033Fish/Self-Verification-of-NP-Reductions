"""Reduction from SAT (CNF) to Clique.

The source problem is defined in :class:`problems.Sat` and expects an
instance of the form `{"num_vars": m, "clauses": [[literal, ...], ...]}`.
Each literal is an integer `+v` (variable *v* true) or `-v` (variable *v*
false).  The target problem is :class:`problems.Clique` with instance format
`{"n": n, "edges": [[u, v], ...], "k": k}`.

The classic polynomial‑time reduction works as follows:

* For each clause *C_i* and each literal *ℓ* in that clause we create a vertex
  identified by the pair ``(i, ℓ)``.
* Two vertices are connected by an (undirected) edge iff they belong to
  *different* clauses **and** the corresponding literals are not complementary
  (i.e. ``ℓ₁ != -ℓ₂``).
* We set ``k`` equal to the number of clauses.

If the CNF formula is satisfiable, we can pick one true literal from each
clause; the chosen vertices form a ``k``‑clique because they are pairwise
non‑conflicting.  Conversely, any ``k``‑clique selects exactly one vertex from
each clause and yields a consistent assignment that satisfies all clauses.

Edge‑case handling:
* **No clauses** – an empty formula is always satisfiable.  For the Clique
  instance we use ``k = 0`` (the problem definition states that ``k <= 0`` is
  always a yes instance).  The graph may be empty.
* **Empty clause** – such a clause can never be satisfied, so the formula is
  unsatisfiable.  We return a Clique instance where ``k > n`` (here ``n = 0``
  and ``k = 1``), which is always a no instance.

The implementation follows the description above and runs in polynomial
time with respect to the size of the SAT instance.
"""

from __future__ import annotations

from typing import List, Tuple

# Import the problem classes only for validation (optional).  The reduction
# itself does not rely on any methods of the classes.
from problems import SOURCE, TARGET


def _unsat_clique_instance() -> dict:
    """Return a Clique instance that is always a NO instance.

    Using ``n = 0`` and ``k = 1`` guarantees ``k > n`` which, by the problem
    definition, is an unsatisfiable instance.
    """
    return {"n": 0, "edges": [], "k": 1}


def _trivial_yes_clique_instance() -> dict:
    """Return a Clique instance that is always a YES instance.

    Setting ``k = 0`` satisfies the edge‑case rule that any ``k <= 0`` is a
    yes instance, regardless of the graph.
    """
    return {"n": 0, "edges": [], "k": 0}


def reduce(instance: dict) -> dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the SAT specification described in the
        docstring of :class:`problems.Sat`.

    Returns
    -------
    dict
        A dictionary adhering to the Clique specification.  The returned
        instance is a yes‑instance iff the input SAT instance is a yes‑instance.
    """
    # Validate the SAT instance – this will raise InvalidInstance if malformed.
    SOURCE.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    # Edge case 1: any empty clause makes the formula unsatisfiable.
    for clause in clauses:
        if len(clause) == 0:
            return _unsat_clique_instance()

    # Edge case 2: formula with zero clauses is trivially satisfiable.
    if len(clauses) == 0:
        return _trivial_yes_clique_instance()

    # Build vertices: one for each literal in each clause.
    vertices: List[Tuple[int, int]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    # Pre‑compute edges according to the reduction rules.
    edges: List[List[int]] = []
    for i in range(n):
        ci, lit_i = vertices[i]
        for j in range(i + 1, n):
            cj, lit_j = vertices[j]
            # Vertices must come from different clauses.
            if ci == cj:
                continue
            # Do not connect complementary literals.
            if lit_i == -lit_j:
                continue
            edges.append([i, j])

    # The required clique size is the number of clauses.
    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}

