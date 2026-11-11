"""Cross-checks between problems over their full enumerations.

Each identity is a known, trivially correct reduction, so these tests check
two solvers against each other. They also double as the first gold
reductions for validating the hidden verifier.

Run with: uv run pytest
"""

from __future__ import annotations

import random

from benchmark.problems import (
    Clique,
    HamiltonianCycle,
    HamiltonianPath,
    IndependentSet,
    NaeThreeSat,
    OneInThreeSat,
    Partition,
    Sat,
    SubsetSum,
    ThreeSat,
    VertexCover,
)
from benchmark.problems.graph_common import (
    adjacency,
    complement_adjacency,
    vertices,
)


def complement(instance):
    n = instance["n"]
    comp = complement_adjacency(n, adjacency(n, instance["edges"]))
    edges = [[u, v] for u in range(n) for v in vertices(comp[u]) if u < v]
    return {**instance, "edges": edges}


def test_independent_set_iff_vertex_cover_of_rest():
    # S is independent  <=>  V \ S is a vertex cover.
    for instance in IndependentSet.enumerate_instances(5):
        cover = {**instance, "k": instance["n"] - instance["k"]}
        assert IndependentSet.is_yes(instance) == VertexCover.is_yes(cover)


def test_clique_iff_independent_set_of_complement():
    for instance in Clique.enumerate_instances(5):
        assert Clique.is_yes(instance) == IndependentSet.is_yes(complement(instance))


def test_partition_iff_subset_sum_to_half():
    for instance in Partition.enumerate_instances(4):
        total = sum(instance["numbers"])
        expected = total % 2 == 0 and SubsetSum.is_yes(
            {"numbers": instance["numbers"], "target": total // 2}
        )
        assert Partition.is_yes(instance) == expected


def test_hamiltonian_cycle_implies_path():
    for instance in HamiltonianCycle.enumerate_instances(5):
        if HamiltonianCycle.is_yes(instance):
            assert HamiltonianPath.is_yes(instance)


def test_three_sat_instances_are_sat_instances_with_same_answer():
    for instance in ThreeSat.enumerate_instances(3):
        Sat.validate(instance)
        assert Sat.is_yes(instance) == ThreeSat.is_yes(instance)


def test_nae_and_one_in_three_imply_three_sat():
    # Both are stricter than "at least one literal true".
    for instance in NaeThreeSat.enumerate_instances(3):
        if NaeThreeSat.is_yes(instance):
            assert ThreeSat.is_yes(instance)
    rng = random.Random(0)
    for _ in range(300):
        instance = OneInThreeSat.random_instance(rng, rng.randint(3, 8))
        if OneInThreeSat.is_yes(instance):
            assert ThreeSat.is_yes(instance)
