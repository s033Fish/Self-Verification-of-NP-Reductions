"""Polynomial-time reduction from 3-SAT to 3-Coloring.

Graph construction
------------------
Colours are named T (true), F (false) and B (blue).

* Base triangle on nodes ANCHOR=0, FALSE=1, TRUE=2.  In every proper
  3-colouring these three nodes receive the three distinct colours; we
  call colour(0)=B, colour(1)=F, colour(2)=T.

* Variable gadget for variable i: two nodes pos[i], neg[i] joined by an
  edge and both joined to ANCHOR.  Since ANCHOR has colour B, both nodes
  lie in {T,F} and the edge makes them different.  So pos[i]=T means the
  variable is true and neg[i]=T means it is false.

* NAE gadget on three inputs u,v,w (each coloured T or F): a triangle
  a,b,c with edges a-u, b-v, c-w.  It is colourable iff u,v,w are not
  all equal.  (All equal -> a,b,c avoid one colour, leaving only two
  colours for a triangle, impossible.  Otherwise an explicit colouring
  exists.)

* Clause gadget for (l1 v l2 v l3): a fresh auxiliary variable y (nodes
  y, ny forced to T/F and opposite) plus two NAE gadgets
      NAE(l1, l2, y)   and   NAE(l3, ny, FALSE).
  One checks that some choice of y makes both NAE constraints hold iff
  l1 v l2 v l3 is true:
    - l3 = T : second NAE is automatic; choose y to satisfy the first.
    - l3 = F : second NAE forces y = F; then the first holds iff
               not(l1 = l2 = F), i.e. l1 v l2.
    - l1 = l2 = l3 = F : second forces y = F and the first fails.

Auxiliary nodes are local to each clause, so the whole graph is
3-colourable exactly when the formula is satisfiable.
"""


def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]

    ANCHOR, FALSE, TRUE = 0, 1, 2
    edges = []

    def add(u, v):
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append((u, v))

    # Base triangle.
    add(ANCHOR, FALSE)
    add(FALSE, TRUE)
    add(ANCHOR, TRUE)

    n = 3

    # Variable gadgets.
    pos = {}
    neg = {}
    for i in range(1, m + 1):
        pos[i] = n
        neg[i] = n + 1
        n += 2
        add(pos[i], neg[i])
        add(pos[i], ANCHOR)
        add(neg[i], ANCHOR)

    def lit_node(lit):
        v = abs(lit)
        return pos[v] if lit > 0 else neg[v]

    # Clause gadgets.
    for clause in clauses:
        l1, l2, l3 = clause

        # Auxiliary variable y and its negation ny.
        y = n
        ny = n + 1
        n += 2
        add(y, ny)
        add(y, ANCHOR)
        add(ny, ANCHOR)

        # NAE(l1, l2, y)
        a1, a2, a3 = n, n + 1, n + 2
        n += 3
        add(a1, a2)
        add(a2, a3)
        add(a1, a3)
        add(a1, lit_node(l1))
        add(a2, lit_node(l2))
        add(a3, y)

        # NAE(l3, ny, FALSE)
        b1, b2, b3 = n, n + 1, n + 2
        n += 3
        add(b1, b2)
        add(b2, b3)
        add(b1, b3)
        add(b1, lit_node(l3))
        add(b2, ny)
        add(b3, FALSE)

    # Deduplicate and emit lists.
    seen = set()
    out_edges = []
    for e in edges:
        if e not in seen:
            seen.add(e)
            out_edges.append([e[0], e[1]])

    return {"n": n, "edges": out_edges}
