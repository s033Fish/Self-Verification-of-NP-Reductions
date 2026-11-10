"""Benchmark problem library. Each problem lives in its own module and
subclasses Problem from base.py. Register finished problems in PROBLEMS."""

from .base import InvalidInstance, Problem, check_problem
from .three_sat import ThreeSat

PROBLEMS: dict[str, type[Problem]] = {
    "three_sat": ThreeSat,
}

__all__ = ["InvalidInstance", "PROBLEMS", "Problem", "ThreeSat", "check_problem"]