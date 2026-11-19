"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is :class:`NaeThreeSat` (NAE‑3‑SAT) and the target
problem is :class:`ThreeColoring` (graph 3‑colorability). Both problem
definitions live in ``problems.py`` and expose the instance formats in
their docstrings (reproduced in the task description).

We implement a polynomial‑time many‑one reduction. The construction is
standard and proceeds in two steps:

1. **NAE‑3‑SAT → 3‑SAT** – a NAE clause ``(ℓ₁,ℓ₂,ℓ₃)`` is satisfied iff
   it contains at least one true literal *and* at least one false literal.
   This is equivalent to the conjunction of the two ordinary 3‑CNF
   clauses ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` and ``(¬ℓ₁ ∨ ¬ℓ₂ ∨ ¬ℓ₃)``. Hence each
   NAE clause is replaced by those two clauses.

2. **3‑SAT → 3‑Coloring** – we use the classic reduction from 3‑SAT to
   graph 3‑colorability (see, e.g., Garey & Johnson, *Computers and
   Intractability*). The construction creates a base triangle whose
   vertices will receive the three distinct colours. For each variable
   ``x`` we create two vertices ``x_T`` and ``x_F`` connected by an edge
   and both adjacent to the *base* vertex that represents the third
   colour. This forces ``x_T`` and ``x_F`` to take the two remaining
   colours, which we interpret as the truth values of the variable.

   For every clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we add a clause‑gadget consisting of
   three new vertices forming a triangle. The *i*‑th vertex of the
   gadget is connected to the vertex representing the *negation* of the
   corresponding literal. The triangle can be properly coloured only if
   at least one of those three connections is to a vertex coloured with
   the colour of the literal’s *negation*, which forces the clause to be
   satisfied.

The combined construction yields a graph that is 3‑colourable exactly
when the original NAE‑3‑SAT formula is satisfiable under the NAE
condition.

The ``reduce`` function below follows this plan. It does not invoke any
solver; it merely builds the graph data structure required by the target
problem. All operations are linear in the size of the input instance,
hence polynomial time.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"``
        (list of three‑element lists). Literals are represented as
        signed integers, ``+v`` for the positive literal and ``-v`` for
        the negated literal, exactly as described in the task.

    Returns
    -------
    dict
        A dictionary representing a graph in the format required by the
        target problem: ``{"n": n, "edges": [[u, v], ...]}``.
    """

    m: int = instance.get("num_vars", 0)
    nae_clauses: List[List[int]] = instance.get("clauses", [])

    # ------------------------------------------------------------------
    # Step 1 – convert NAE clauses to ordinary 3‑SAT clauses.
    # For each clause (ℓ₁,ℓ₂,ℓ₃) we create two clauses:
    #   (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) and (¬ℓ₁ ∨ ¬ℓ₂ ∨ ¬ℓ₃).
    # ------------------------------------------------------------------
    sat_clauses: List[Tuple[int, int, int]] = []
    for cl in nae_clauses:
        l1, l2, l3 = cl
        sat_clauses.append((l1, l2, l3))
        sat_clauses.append((-l1, -l2, -l3))

    # ------------------------------------------------------------------
    # Step 2 – build the graph for the 3‑SAT instance.
    # Vertex numbering:
    #   0,1,2 – the base triangle (colours 0,1,2 respectively).
    #   For each variable i (1‑based):
    #       var_true[i]  – vertex representing x_i being true.
    #       var_false[i] – vertex representing x_i being false.
    #   Additional vertices are created for each clause gadget.
    # ------------------------------------------------------------------
    edges: List[Tuple[int, int]] = []

    # base triangle
    edges.extend([(0, 1), (1, 2), (2, 0)])

    # allocate variable vertices
    var_true: List[int] = [0] * (m + 1)   # index by variable number
    var_false: List[int] = [0] * (m + 1)
    next_id = 3  # next free vertex id after the base triangle
    for v in range(1, m + 1):
        vt = next_id
        vf = next_id + 1
        next_id += 2
        var_true[v] = vt
        var_false[v] = vf
        # edge between true/false vertices – they must receive different colours
        edges.append((vt, vf))
        # both are adjacent to the base vertex 2 (the third colour), forcing them
        # to use colour 0 or 1.
        edges.append((vt, 2))
        edges.append((vf, 2))

    # helper to map a literal to the vertex representing its *negation*.
    # In the clause gadget we connect to the vertex that would be true when the
    # literal is false.
    def neg_vertex(lit: int) -> int:
        var = abs(lit)
        if lit > 0:
            # literal is x, its negation is ¬x → use the false‑vertex
            return var_false[var]
        else:
            # literal is ¬x, its negation is x → use the true‑vertex
            return var_true[var]

    # ------------------------------------------------------------------
    # Clause gadgets – one triangle per clause.
    # For clause (ℓ₁ ∨ ℓ₂ ∨ ℓ₃) we create three new vertices a,b,c forming a
    # triangle and connect a‑b‑c edges. Additionally, a is connected to the
    # vertex representing ¬ℓ₁, b to ¬ℓ₂ and c to ¬ℓ₃.
    # ------------------------------------------------------------------
    for (l1, l2, l3) in sat_clauses:
        a = next_id
        b = next_id + 1
        c = next_id + 2
        next_id += 3
        # triangle among a,b,c
        edges.extend([(a, b), (b, c), (c, a)])
        # connect to the appropriate negated literal vertices
        edges.append((a, neg_vertex(l1)))
        edges.append((b, neg_vertex(l2)))
        edges.append((c, neg_vertex(l3)))

    # Convert edge list to the required format (list of [u, v])
    edge_list: List[List[int]] = [list(e) for e in edges]

    return {"n": next_id, "edges": edge_list}

