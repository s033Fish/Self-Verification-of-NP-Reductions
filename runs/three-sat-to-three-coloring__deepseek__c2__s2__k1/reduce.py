"""Polynomial-time reduction from 3-SAT (ThreeSat) to 3-Coloring (ThreeColoring).

Colours are represented by three base vertices forming a triangle:
    T = 0, F = 1, B = 2
with edges (0,1), (1,2), (0,2).  These three vertices are pairwise adjacent,
so they always receive three distinct colours; B is a fixed reference colour
and T/F are the truth colours.

Variable gadget for variable v:
    two vertices pos[v], neg[v] with edges
        pos[v] -- neg[v],  pos[v] -- B,  neg[v] -- B
    Both are adjacent to B, so neither can be B, and they are adjacent to each
    other, so they take the two remaining colours: exactly one is T and the
    other F.  pos[v] = T means v is true.

Not-all-equal (NAE) gadget for inputs (a, b, c):
    three new vertices x, y, z forming a triangle, with edges x--a, y--b, z--c.
    x, y, z need three distinct colours, and each x/y/z must avoid the colour
    of its input.  A system of distinct representatives exists iff the three
    input colours are not all equal (if they are all equal, only two colours
    remain for the triangle).  Hence this gadget is 3-colourable iff a, b, c
    are not all equal.

Clause gadget for clause (l1, l2, l3):
    introduce a fresh variable s (nodes ps, ns via the variable gadget) and add
        NAE(l1, l2, ps)   and   NAE(ns, l3, F)
    where F is the fixed false base vertex (colour 1).  This is satisfiable for
    some s iff l1 or l2 or l3 is true:
      * if l3 is true (colour 0), NAE(ns, 0, 1) holds for every s, and s can be
        chosen so that NAE(l1, l2, ps) holds;
      * if l3 is false (colour 1), NAE(ns, 1, 1) forces ns = 0 (s false), and
        then NAE(l1, l2, ps=1) holds exactly when l1 or l2 is true;
      * if all three literals are false, the second gadget is unsatisfiable.
    Conversely, a colouring of the graph yields truth values for the literal
    nodes, and the two NAE gadgets force at least one literal of the clause to
    be true.

The construction uses O(num_vars + num_clauses) vertices and edges, so it runs
in polynomial time.  No solver is called.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Base palette triangle: T=0, F=1, B=2.
    T, F, B = 0, 1, 2
    edges = [[T, F], [F, B], [T, B]]
    n = 3  # vertices 0, 1, 2 already used

    pos = {}
    neg = {}

    def new_variable():
        """Add a variable gadget and return its (positive, negative) nodes."""
        nonlocal n
        p = n
        q = n + 1
        n += 2
        edges.append([p, q])
        edges.append([p, B])
        edges.append([q, B])
        return p, q

    for v in range(1, num_vars + 1):
        pos[v], neg[v] = new_variable()

    def literal_node(lit):
        if lit > 0:
            return pos[lit]
        return neg[-lit]

    def add_nae(a, b, c):
        """Triangle gadget, 3-colourable iff a, b, c are not all equal."""
        nonlocal n
        x = n
        y = n + 1
        z = n + 2
        n += 3
        edges.append([x, y])
        edges.append([y, z])
        edges.append([x, z])
        edges.append([x, a])
        edges.append([y, b])
        edges.append([z, c])

    for clause in clauses:
        l1, l2, l3 = clause
        ps, ns = new_variable()
        add_nae(literal_node(l1), literal_node(l2), ps)
        add_nae(ns, literal_node(l3), F)

    return {"n": n, "edges": edges}
