"""Polynomial-time reduction from 3-SAT to Exact Cover.

Source instance:  {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Target instance:  {"universe_size": u, "sets": [[element, ...], ...]}

Construction
------------
For every variable i in 1..m we create three elements:

    m_i  -- "variable i is true"
    n_i  -- "variable i is false"
    s_i  -- selector element

and the sets {m_i, s_i} and {n_i, s_i}.  Since s_i can be covered only
once, exactly one of these two sets is chosen, which fixes the truth value
of variable i.

Every occurrence of a literal in a clause gets its own fresh token element.
For a positive occurrence of x_i the token must be usable exactly when x_i
is true; for a negative occurrence exactly when x_i is false.  This is
achieved by the two "group" sets

    {m_i} U pos_tokens(i)      chosen when x_i is false, and
    {n_i} U neg_tokens(i)      chosen when x_i is true.

When x_i is true the set {m_i, s_i} covers m_i, so the first group set
cannot be used and all positive tokens stay available for their clauses;
at the same time n_i must be covered, which forces the second group set to
be used, so all negative tokens become unavailable.  The situation is
symmetric when x_i is false.  The selector s_i makes it impossible to have
both groups available (that would need both {m_i,s_i} and {n_i,s_i}).

For every clause j we create an element c_j and, for each of its three
literals, the set {c_j, token}.  Thus c_j is covered by exactly one such
set, which can be used only if the corresponding literal is true.  Hence a
clause is coverable exactly when at least one of its literals is true.

A set {token} is added for every token so that tokens that are available
but not needed by their clause can still be covered.  Therefore an exact
cover exists iff the formula is satisfiable.
"""

from __future__ import annotations


def reduce(instance):
    num_vars = instance["num_vars"]
    clauses = instance["clauses"]

    sets = []
    next_element = 0

    def new_element():
        nonlocal next_element
        element = next_element
        next_element += 1
        return element

    # Elements of the variable gadgets.
    m_el = [0] * num_vars
    n_el = [0] * num_vars
    s_el = [0] * num_vars
    for i in range(num_vars):
        m_el[i] = new_element()
        n_el[i] = new_element()
        s_el[i] = new_element()

    pos_tokens = [[] for _ in range(num_vars)]
    neg_tokens = [[] for _ in range(num_vars)]

    for clause in clauses:
        clause_el = new_element()
        for literal in clause:
            var = abs(literal) - 1
            token = new_element()
            if literal > 0:
                pos_tokens[var].append(token)
            else:
                neg_tokens[var].append(token)
            # Covering the clause element together with this literal's token.
            sets.append([clause_el, token])
            # Filler: lets an unused token be covered.
            sets.append([token])

    for i in range(num_vars):
        # Exactly one of these two is chosen (they share s_i).
        sets.append([m_el[i], s_el[i]])
        sets.append([n_el[i], s_el[i]])
        # Used when x_i is false: covers m_i and all positive tokens.
        sets.append([m_el[i]] + pos_tokens[i])
        # Used when x_i is true: covers n_i and all negative tokens.
        sets.append([n_el[i]] + neg_tokens[i])

    return {"universe_size": next_element, "sets": sets}
