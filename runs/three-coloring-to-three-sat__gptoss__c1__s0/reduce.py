"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form
    {"n": n, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1 and edges are undirected.

The target problem (ThreeSat) expects an instance of the form
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
where each literal is a string "+v" (variable v is true) or "-v"
 (variable v is false).  Every clause must contain exactly three
 distinct literals on distinct variables.

The reduction creates Boolean variables representing the colour of each
vertex and adds 3‑SAT clauses that enforce:
  1. Every vertex receives at least one colour.
  2. No vertex receives two different colours (at‑most‑one).
  3. Adjacent vertices do not share the same colour.

Constraints (2) and (3) are naturally expressed as 2‑literal clauses
 "(¬x ∨ ¬y)".  To fit the 3‑SAT format we replace each such clause by a
 pair of 3‑literal clauses using a fresh helper variable *z*:
      (¬x ∨ ¬y)   ≡   (¬x ∨ ¬y ∨  z) ∧ (¬x ∨ ¬y ∨ ¬z)
The two clauses together are satisfied exactly when the original
2‑clause is satisfied.

The construction runs in polynomial time and the number of variables
is O(n + |E|).  The returned instance is a correct 3‑SAT formula that is
 satisfiable iff the input graph is 3‑colourable.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to a ThreeSat instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys "n" (int) and "edges" (list of [u, v]).

    Returns
    -------
    dict
        A dictionary with keys "num_vars" and "clauses" suitable for the
        ThreeSat problem definition.
    """

    n = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Edge case: empty graph – trivially satisfiable.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Helper to compute the variable index for vertex v and colour c (1‑based).
    def var(v: int, c: int) -> int:
        # Variables are 1‑based. Colours are 1,2,3.
        return v * 3 + c

    clauses: List[List[str]] = []
    next_var = 3 * n  # last used variable index for colour variables

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clause = [f"+{var(v, 1)}", f"+{var(v, 2)}", f"+{var(v, 3)}"]
        clauses.append(clause)

    # 2. At‑most‑one colour per vertex (pairwise constraints).
    for v in range(n):
        # pairs (1,2), (1,3), (2,3)
        for c1, c2 in ((1, 2), (1, 3), (2, 3)):
            # Fresh helper variable to lift the 2‑clause to 3‑SAT.
            next_var += 1
            helper = next_var
            lit1 = f"-{var(v, c1)}"
            lit2 = f"-{var(v, c2)}"
            # (¬x ∨ ¬y ∨  z) and (¬x ∨ ¬y ∨ ¬z)
            clauses.append([lit1, lit2, f"+{helper}"])
            clauses.append([lit1, lit2, f"-{helper}"])

    # 3. Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in (1, 2, 3):
            next_var += 1
            helper = next_var
            lit1 = f"-{var(u, c)}"
            lit2 = f"-{var(v, c)}"
            clauses.append([lit1, lit2, f"+{helper}"])
            clauses.append([lit1, lit2, f"-{helper}"])

    total_vars = next_var
    return {"num_vars": total_vars, "clauses": clauses}

