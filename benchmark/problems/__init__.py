"""Benchmark problem library. Each problem lives in its own module and
subclasses Problem from base.py. Register finished problems in PROBLEMS."""

from .base import InvalidInstance, Problem, check_problem
from .clique import Clique
from .dominating_set import DominatingSet
from .exact_cover import ExactCover
from .hamiltonian_cycle import HamiltonianCycle
from .hamiltonian_path import HamiltonianPath
from .independent_set import IndependentSet
from .nae_three_sat import NaeThreeSat
from .one_in_three_sat import OneInThreeSat
from .partition import Partition
from .sat import Sat
from .set_cover import SetCover
from .subset_sum import SubsetSum
from .three_coloring import ThreeColoring
from .three_sat import ThreeSat
from .vertex_cover import VertexCover

# Every finished problem, by key. Add each new problem here.
PROBLEMS: dict[str, type[Problem]] = {
    # Logic
    "sat": Sat,
    "three_sat": ThreeSat,
    "nae_three_sat": NaeThreeSat,
    "one_in_three_sat": OneInThreeSat,
    # Graphs
    "independent_set": IndependentSet,
    "vertex_cover": VertexCover,
    "clique": Clique,
    "dominating_set": DominatingSet,
    "three_coloring": ThreeColoring,
    "hamiltonian_cycle": HamiltonianCycle,
    "hamiltonian_path": HamiltonianPath,
    # Sets
    "set_cover": SetCover,
    "exact_cover": ExactCover,
    # Numbers
    "subset_sum": SubsetSum,
    "partition": Partition,
}

__all__ = [
    "PROBLEMS",
    "InvalidInstance",
    "Problem",
    "check_problem",
    *(problem.__name__ for problem in PROBLEMS.values()),
]
