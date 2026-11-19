"""Polynomial-time reduction from 3-SAT to Exact Cover.

Source instance (3-SAT):
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Target instance (Exact Cover):
    {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
Element layout:
    * v_i        = i - 1                       for i = 1..num_vars
    * c_j        = num_vars + j                for j = 0..len(clauses)-1
    * p_{j,k}    = num_vars + len(clauses) + 3*j + k

Sets:
    * T_i = {v_i} union { p_{j,k} : clause j, position k holds literal -i }
    * F_i = {v_i} union { p_{j,k} : clause j, position k holds literal +i }

      T_i and F_i share v_i, so at most one can be picked; v_i must be
      covered, so exactly one is picked.  This encodes the truth value of
      variable i.  A p_{j,k} belongs to the set for the *opposite* value of
      literal l_{j,k}; hence p_{j,k} is covered by a variable set exactly
      when l_{j,k} is false.

    * A_{j,k} = {c_j, p_{j,k}}
    * B_{j,k} = {p_{j,k}}

      c_j can only be covered by one of the A_{j,k}; that A_{j,k} is
      choosable only when p_{j,k} is not already covered by a variable set,
      i.e. only when l_{j,k} is true.  So clause j is satisfiable iff c_j
      can be covered.  For the other true literals of the clause, their
      p_{j,k} are covered by the singleton B_{j,k}; for false literals the
      variable set covers p_{j,k}.  Everything is covered exactly once.

Therefore the exact-cover instance has a solution iff the 3-SAT instance
is satisfiable.  The construction is linear in the input size.
"""


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]
    m = len(clauses)

    # Element indices.
    #   v_i      -> i - 1                        (0 .. num_vars-1)
    #   c_j      -> num_vars + j                 (num_vars .. num_vars+m-1)
    #   p_{j,k}  -> num_vars + m + 3*j + k       (num_vars+m .. num_vars+4m-1)
    universe_size = num_vars + 4 * m

    # Variable gadgets: T_i and F_i both contain v_i.
    true_sets = [[i] for i in range(num_vars)]   # T_i
    false_sets = [[i] for i in range(num_vars)]  # F_i

    sets = []

    for j, clause in enumerate(clauses):
        c_elem = num_vars + j
        for k, literal in enumerate(clause):
            p_elem = num_vars + m + 3 * j + k

            # Clause gadget sets.
            sets.append([c_elem, p_elem])  # A_{j,k}
            sets.append([p_elem])          # B_{j,k}

            var_index = abs(literal) - 1
            if literal > 0:
                # Positive literal +var: p is covered when var is FALSE.
                false_sets[var_index].append(p_elem)
            else:
                # Negative literal -var: p is covered when var is TRUE.
                true_sets[var_index].append(p_elem)

    # Add the variable gadget sets.
    for i in range(num_vars):
        sets.append(true_sets[i])
        sets.append(false_sets[i])

    return {"universe_size": universe_size, "sets": sets}
