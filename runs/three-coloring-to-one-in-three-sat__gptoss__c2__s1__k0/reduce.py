"""Reduction from 3-Coloring to 1-in-3-SAT.

Source instance format (ThreeColoring):
    {"n": int, "edges": [[u, v], ...]}
    Vertices are 0..n-1.

Target instance format (OneInThreeSat):
    {"num_vars": int, "clauses": [[a, b, c], ...]}
    Variables are 1..num_vars, each clause contains three distinct
    positive integers.

The reduction creates, for each vertex v, three Boolean variables
    v_R, v_G, v_B (encoded as consecutive integer IDs).  A clause
    (v_R, v_G, v_B) forces exactly one of the three colours to be true.
For each edge (u, v) we introduce three fresh auxiliary variables
    e_{uv,R}, e_{uv,G}, e_{uv,B}.  For each colour c we add a clause
    (u_c, v_c, e_{uv,c}) which guarantees that u and v cannot both
    take colour c.  Finally we add the clause (e_{uv,R}, e_{uv,G},
    e_{uv,B}) which forces exactly one of the auxiliary variables to
    be true; this is satisfied precisely when u and v have different
    colours.

The construction is polynomial in the size of the graph.
"""

def reduce(instance):
    n = instance.get("n", 0)
    edges = instance.get("edges", [])
    # Variable numbering:
    # For vertex i (0-indexed), colours 0,1,2 get IDs 3*i + 1, 3*i + 2, 3*i + 3
    clauses = []
    # Vertex colour clauses
    for i in range(n):
        v_vars = [3*i + 1, 3*i + 2, 3*i + 3]
        clauses.append(v_vars)
    # Edge gadgets
    next_var = 3*n + 1  # first auxiliary variable id
    for (u, v) in edges:
        # auxiliary vars for this edge, one per colour
        e_vars = []
        for colour in range(3):
            u_var = 3*u + colour + 1
            v_var = 3*v + colour + 1
            e_var = next_var
            next_var += 1
            e_vars.append(e_var)
            # clause (u_colour, v_colour, e_var)
            clauses.append([u_var, v_var, e_var])
        # clause forcing exactly one of the e_vars to be true
        clauses.append(e_vars)
    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

# The module provides only the reduce function; it can be imported by the
# evaluation harness.
