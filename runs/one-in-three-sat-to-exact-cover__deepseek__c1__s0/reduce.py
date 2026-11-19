def reduce(instance):
    """Polynomial-time reduction from positive 1-in-3-SAT to Exact Cover.

    Construction
    ------------
    For every occurrence of a variable in a clause, create a distinct port
    element.  For each variable v, create the set P_v containing all of its
    port elements.  Choosing P_v means v is false and covers all of v's ports.

    For each clause j with three literals, create two private elements
    q_{j,0}, q_{j,1} and, for each literal position k, the set
        { port(j,k), q_{j,0}, q_{j,1} }.

    If v is true, P_v is not chosen, so every clause containing v must cover
    v's port using its clause set.  A clause set also covers that clause's two
    private elements, and all clause sets of one clause share those elements,
    so exactly one clause set per clause can be chosen.  Hence a clause can be
    covered iff exactly one of its three variables is true.  The chosen P_v
    sets define a consistent assignment: v is false exactly when P_v is
    chosen.
    """
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    # Assign integer element ids.
    next_id = 0
    port_id = {}
    q_id = {}
    for j, clause in enumerate(clauses):
        for k in range(3):
            port_id[(j, k)] = next_id
            next_id += 1
        q_id[(j, 0)] = next_id
        next_id += 1
        q_id[(j, 1)] = next_id
        next_id += 1

    universe_size = next_id

    # Collect the ports belonging to each variable.
    var_ports = {v: [] for v in range(1, num_vars + 1)}
    for j, clause in enumerate(clauses):
        for k, v in enumerate(clause):
            var_ports[v].append(port_id[(j, k)])

    sets = []

    # Variable gadget: choosing this set makes the variable false.
    for v in range(1, num_vars + 1):
        if var_ports[v]:
            sets.append(var_ports[v])

    # Clause gadgets.
    for j, clause in enumerate(clauses):
        q0 = q_id[(j, 0)]
        q1 = q_id[(j, 1)]
        for k in range(3):
            sets.append([port_id[(j, k)], q0, q1])

    return {"universe_size": universe_size, "sets": sets}
