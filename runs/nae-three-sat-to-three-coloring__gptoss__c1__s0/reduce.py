"""Reduction from NAE-3-SAT to 3-Coloring.

The source instance format (NAE-3-SAT) is:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
where each literal li is a string "+v" (variable v is true) or "-v" (variable v is false).

The target instance format (3-Coloring) is:
    {"n": n, "edges": [[u, v], ...]}
with vertices numbered 0..n-1.

The reduction works as follows (standard reduction from SAT to 3‑Coloring,
applied to the transformed formula consisting of each original clause and its
negation).  It guarantees that the constructed graph is 3‑colorable iff the
NAE‑3‑SAT formula has a not‑all‑equal satisfying assignment.
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Set


def _parse_literal(lit: str) -> Tuple[int, int]:
    """Return (sign, var) where sign is +1 for positive, -1 for negative.
    lit is a string like "+3" or "-2".
    """
    lit = lit.strip()
    if lit[0] == '+':
        return 1, int(lit[1:])
    elif lit[0] == '-':
        return -1, int(lit[1:])
    else:
        raise ValueError(f"Invalid literal format: {lit}")


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    The construction uses the classic reduction from SAT to 3‑Coloring.
    For each variable x we create two vertices `x_pos` and `x_neg` that are
    forced to take the colors representing TRUE and FALSE respectively.
    For each clause (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) we add a triangle of clause vertices and
    connect each of them to the vertex representing the corresponding literal.
    To enforce the *not‑all‑equal* condition we add a second clause gadget for
    the negated clause (¬ℓ₁ ∨ ¬ℓ₂ ∨ ¬ℓ₃).  The resulting graph is 3‑colorable iff
    the original NAE‑3‑SAT instance is satisfiable.
    """
    m: int = instance.get("num_vars", 0)
    raw_clauses: List[List[str]] = instance.get("clauses", [])

    # Special colour vertices: 0 = TRUE, 1 = FALSE, 2 = BASE
    TRUE, FALSE, BASE = 0, 1, 2
    next_id = 3  # next free vertex id after the three specials

    # Store the two vertices for each variable
    var_pos: Dict[int, int] = {}
    var_neg: Dict[int, int] = {}
    for v in range(1, m + 1):
        pos = next_id
        neg = next_id + 1
        next_id += 2
        var_pos[v] = pos
        var_neg[v] = neg

    edges: Set[Tuple[int, int]] = set()
    # The three special vertices form a triangle
    edges.add(tuple(sorted((TRUE, FALSE))))
    edges.add(tuple(sorted((FALSE, BASE))))
    edges.add(tuple(sorted((BASE, TRUE))))

    # Variable gadgets
    for v in range(1, m + 1):
        pos = var_pos[v]
        neg = var_neg[v]
        # pos and neg are adjacent
        edges.add(tuple(sorted((pos, neg))))
        # Both are adjacent to BASE, preventing them from taking the BASE colour
        edges.add(tuple(sorted((pos, BASE))))
        edges.add(tuple(sorted((neg, BASE))))

    def add_clause_gadget(lits: List[Tuple[int, int]]) -> None:
        """Add a clause gadget for the given three literals.
        `lits` is a list of three (sign, var) pairs.
        """
        nonlocal next_id
        if len(lits) != 3:
            raise ValueError("Each clause must have exactly three literals")
        # Create three new vertices for the clause triangle
        c1 = next_id
        c2 = next_id + 1
        c3 = next_id + 2
        next_id += 3
        # Connect them as a triangle
        edges.add(tuple(sorted((c1, c2))))
        edges.add(tuple(sorted((c2, c3))))
        edges.add(tuple(sorted((c3, c1))))
        # Connect each clause vertex to the vertex representing the literal
        clause_vertices = [c1, c2, c3]
        for cv, (sgn, var) in zip(clause_vertices, lits):
            lit_vertex = var_pos[var] if sgn == 1 else var_neg[var]
            edges.add(tuple(sorted((cv, lit_vertex))))

    # Process each original clause and also its negated counterpart
    for raw_clause in raw_clauses:
        # Parse literals of the original clause
        parsed = [_parse_literal(lit) for lit in raw_clause]
        # Original clause gadget (ensures at least one literal true)
        add_clause_gadget(parsed)
        # Negated clause gadget (ensures at least one literal false)
        negated = [(-sgn, var) for (sgn, var) in parsed]
        add_clause_gadget(negated)

    # Build the final instance dictionary
    edge_list = [list(e) for e in edges]
    n_vertices = next_id  # vertices are 0 .. n_vertices-1
    return {"n": n_vertices, "edges": edge_list}


# The module exports only the `reduce` function as required.

