"""The interface every benchmark problem implements, and shared conventions.

A problem is a class whose methods are classmethods.

Two different "sizes" appear below:

* scale  A small problem-specific knob that says how big an instance to
         make: the number of vertices for a graph problem, the number of
         variables for a SAT problem. random_instance and
         enumerate_instances take it.
* size   The encoding length of a given instance (e.g. n + |E|), returned
         by size(). The hidden verifier compares size(reduce(x)) with
         size(x) to flag non-polynomial blowup.

Conventions shared by all problems (the docstrings repeat what each needs):
- Instances are plain JSON-serialisable dicts: ints, lists and dicts only.
- Integers are real ints.
- Graphs are {"n": n, "edges": [[u, v], ...]}: vertices 0..n-1, undirected,
  no self-loops and no duplicate edges ([u, v] and [v, u] are the same edge).
  Edge order does not matter.
- CNF formulas use DIMACS-style literals: variables 1..m, a literal is +v or
  -v, a clause is a list of literals. The empty formula is satisfiable; a
  formula containing an empty clause is not.
- Budgets are named k, and every docstring says whether the condition is
  "at most k", "at least k" or "exactly k".

This module uses only the standard library, so make_task.py can copy it into
a task's problems.py unchanged.
"""

from __future__ import annotations

import json
import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from itertools import combinations
from typing import Any, ClassVar

Instance = dict[str, Any]

_REQUIRED_METHODS = (
    "validate",
    "is_yes",
    "size",
    "random_instance",
    "enumerate_instances",
)


class InvalidInstance(ValueError):
    """An instance that does not follow its problem's format."""

class Problem(ABC):
    """Base class for benchmark problems. Subclasses set `name`,
    `exhaustive_scale` and a docstring, and implement every method below."""

    name: ClassVar[str]
    # Largest scale at which enumerate_instances plus is_yes stays fast enough
    # for the verifier to check every instance (seconds, not minutes).
    exhaustive_scale: ClassVar[int]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Fail at import time, not mid-experiment, if a problem is incomplete."""
        super().__init_subclass__(**kwargs)
        missing = [
            method for method in _REQUIRED_METHODS
            if getattr(cls, method).__func__ is getattr(Problem, method).__func__
        ]
        if missing:
            raise TypeError(f"{cls.__name__} must implement {', '.join(missing)}")
        if not isinstance(getattr(cls, "name", None), str):
            raise TypeError(f"{cls.__name__} must set name")
        if not isinstance(getattr(cls, "exhaustive_scale", None), int):
            raise TypeError(f"{cls.__name__} must set exhaustive_scale")
        if not (cls.__doc__ or "").strip():
            raise TypeError(
                f"{cls.__name__} needs a docstring: it is the spec the agent reads"
            )

    def __new__(cls, *args: Any, **kwargs: Any):
        raise TypeError("problems are used as classes; do not instantiate them")

    @classmethod
    @abstractmethod
    def validate(cls, instance: Any) -> None:
        """Raise InvalidInstance unless `instance` follows the format exactly."""

    @classmethod
    @abstractmethod
    def is_yes(cls, instance: Instance) -> bool:
        """Brute-force answer. Exponential time: small instances only.
        May assume validate(instance) has passed."""

    @classmethod
    @abstractmethod
    def size(cls, instance: Instance) -> int:
        """Encoding length of the instance (see module docstring)."""

    @classmethod
    @abstractmethod
    def random_instance(cls, rng: random.Random, scale: int) -> Instance:
        """A valid instance at this scale, drawn with `rng` so runs repeat.
        Should produce both yes and no instances across draws."""

    @classmethod
    @abstractmethod
    def enumerate_instances(cls, scale: int) -> Iterator[Instance]:
        """Every valid instance with scale at most `scale`, each exactly once."""


# --- Shared validation helpers ---------------------------------------------


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidInstance(message)


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_keys(instance: Any, keys: set[str]) -> None:
    require(isinstance(instance, dict), "instance must be a dict")
    require(
        set(instance) == keys,
        f"instance keys must be exactly {sorted(keys)}, got {sorted(instance)}",
    )


def require_int(value: Any, field: str, minimum: int | None = None) -> None:
    require(is_int(value), f"{field} must be an int")
    if minimum is not None:
        require(value >= minimum, f"{field} must be >= {minimum}")


def validate_graph(instance: Instance) -> None:
    """Check the "n" and "edges" fields of a graph instance."""
    n = instance.get("n")
    require_int(n, "n", minimum=0)
    edges = instance.get("edges")
    require(isinstance(edges, list), "edges must be a list")
    seen: set[frozenset[int]] = set()
    for edge in edges:
        require(
            isinstance(edge, list) and len(edge) == 2,
            f"each edge must be a list [u, v], got {edge!r}",
        )
        u, v = edge
        require(is_int(u) and is_int(v), f"edge endpoints must be ints, got {edge!r}")
        require(0 <= u < n and 0 <= v < n, f"edge {edge!r} has a vertex outside 0..{n - 1}")
        require(u != v, f"self-loop {edge!r} is not allowed")
        key = frozenset((u, v))
        require(key not in seen, f"duplicate edge {edge!r}")
        seen.add(key)


def validate_cnf(clauses: Any, num_vars: Any) -> None:
    """Check a DIMACS-style clause list over variables 1..num_vars."""
    require_int(num_vars, "num_vars", minimum=0)
    require(isinstance(clauses, list), "clauses must be a list")
    for clause in clauses:
        require(isinstance(clause, list), f"each clause must be a list, got {clause!r}")
        for literal in clause:
            require(is_int(literal), f"literals must be ints, got {literal!r}")
            require(
                literal != 0 and abs(literal) <= num_vars,
                f"literal {literal} is outside ±1..±{num_vars}",
            )


# --- Shared generation helpers ---------------------------------------------


def all_graphs(n: int) -> Iterator[list[list[int]]]:
    """Every labelled simple graph on n vertices, as an edge list.
    There are 2^(n(n-1)/2) of them: 1,024 at n = 5, 32,768 at n = 6."""
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(pair) for index, pair in enumerate(pairs) if mask >> index & 1]


def random_graph(rng: random.Random, n: int, p: float | None = None) -> list[list[int]]:
    """Edge list with each edge present with probability p (random if None)."""
    p = rng.random() if p is None else p
    return [[u, v] for u, v in combinations(range(n), 2) if rng.random() < p]


def canonical(instance: Instance) -> str:
    """A stable string for an instance, for de-duplication and logging."""
    return json.dumps(instance, sort_keys=True, separators=(",", ":"))


# --- Conformance check -------------------------------------------------------

def check_problem(
    problem: type[Problem],
    scale: int | None = None,
    random_draws: int = 200,
    seed: int = 0,
) -> dict[str, int]:
    """Check that a problem honours the interface. Raises AssertionError.

    Every enumerated instance must validate, be distinct and get a bool
    answer; random instances must validate; sizes must be non-negative ints;
    and both yes and no answers must occur. Returns counts for the Data
    section of the report.
    """
    scale = problem.exhaustive_scale if scale is None else scale
    seen: set[str] = set()
    yes = no = 0
    for instance in problem.enumerate_instances(scale):
        problem.validate(instance)
        key = canonical(instance)
        assert key not in seen, f"{problem.name}: duplicate enumerated instance {key}"
        seen.add(key)
        answer = problem.is_yes(instance)
        assert isinstance(answer, bool), f"{problem.name}: is_yes must return a bool"
        size = problem.size(instance)
        assert is_int(size) and size >= 0, f"{problem.name}: bad size {size!r}"
        yes += answer
        no += not answer
    assert seen, f"{problem.name}: enumerate_instances({scale}) yielded nothing"
    assert yes and no, f"{problem.name}: enumeration has only one answer (yes={yes}, no={no})"

    rng = random.Random(seed)
    for _ in range(random_draws):
        instance = problem.random_instance(rng, scale)
        problem.validate(instance)
        assert isinstance(problem.is_yes(instance), bool)
    return {"enumerated": len(seen), "yes": yes, "no": no}
