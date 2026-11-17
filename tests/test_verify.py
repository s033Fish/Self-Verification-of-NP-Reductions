"""Tests for the hidden verifier: correct reductions must pass, and each kind
of broken reduction must fail with the right category.

Run with: uv run pytest   (about a minute: every case starts a sandbox)
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from benchmark.make_task import Pair, write_task
from benchmark.problems import PROBLEMS
from benchmark.verify import Settings, _fit_exponent, perturb, verify_reduction, verify_run

# Smaller than the defaults so the suite stays quick; same checks.
FAST = Settings(
    call_timeout=1.0,
    random_per_scale=20,
    min_random_checked=20,
    scaling_draws=3,
    random_phase_seconds=30,
)

INDSET_TO_VC = Pair("independent_set", "vertex_cover", famous=True, split="dev")
SUBSET_SUM_TO_PARTITION = Pair("subset_sum", "partition", famous=True, split="dev")
THREE_SAT_TO_EXACT_COVER = Pair("three_sat", "exact_cover", famous=False, split="dev")

# --- Correct reductions -------------------------------------------------------

GOLD_INDSET_TO_VC = """
def reduce(instance):
    # S is independent  <=>  V \\ S is a vertex cover.
    return {"n": instance["n"], "edges": instance["edges"], "k": instance["n"] - instance["k"]}
"""

GOLD_SUBSET_SUM_TO_PARTITION = """
def reduce(instance):
    numbers, t = instance["numbers"], instance["target"]
    total = sum(numbers)
    if t < 0 or t > total:
        return {"numbers": [1]}  # a fixed no-instance
    # The two new numbers must go to opposite sides; the side holding 2S - t
    # then needs exactly t from the original numbers.
    return {"numbers": numbers + [2 * total - t, total + t]}
"""

# Correct, with polynomial padding: n^3 isolated vertices never change a minimum
# cover. Input size n + |E| already grows like n^2, so this is about
# (input size)^1.5.
PADDED_INDSET_TO_VC = """
def reduce(instance):
    n = instance["n"]
    return {"n": n + n ** 3, "edges": instance["edges"], "k": n - instance["k"]}
"""

PRINTS_DEBUG_OUTPUT = """
def reduce(instance):
    print("debugging", instance)
    return {"n": instance["n"], "edges": instance["edges"], "k": instance["n"] - instance["k"]}
"""

MUTATES_ITS_INPUT = """
def reduce(instance):
    instance["k"] = instance["n"] - instance["k"]
    return instance
"""

# --- Broken reductions --------------------------------------------------------

OFF_BY_ONE = """
def reduce(instance):
    return {"n": instance["n"], "edges": instance["edges"], "k": instance["n"] - instance["k"] + 1}
"""

IDENTITY = """
def reduce(instance):
    return instance
"""

CALLS_IS_YES = """
from problems import SOURCE

def reduce(instance):
    answer = SOURCE.is_yes(instance)
    return {"n": 1, "edges": [], "k": 1 if answer else -1}
"""

CALLS_SOLVER_HELPER = """
import problems

def reduce(instance):
    best = problems.max_independent_set_size(instance["n"], [0] * instance["n"])
    return {"n": instance["n"], "edges": instance["edges"], "k": instance["n"] - instance["k"]}
"""

SWALLOWS_SOLVER_ERROR = """
from problems import SOURCE

def reduce(instance):
    try:
        SOURCE.is_yes(instance)
    except BaseException:
        pass
    return {"n": instance["n"], "edges": instance["edges"], "k": instance["n"] - instance["k"]}
"""

INFINITE_LOOP = """
def reduce(instance):
    while True:
        pass
"""

RAISES = """
def reduce(instance):
    raise ValueError("not implemented")
"""

MALFORMED = """
def reduce(instance):
    return {"n": instance["n"], "edges": instance["edges"], "k": str(instance["n"] - instance["k"])}
"""

NOT_JSON = """
def reduce(instance):
    return {"n": instance["n"], "edges": instance["edges"], "k": {1, 2}}
"""

EXPONENTIAL_OUTPUT = """
def reduce(instance):
    # Correct answers (isolated vertices never change a minimum cover), but the
    # output has 4^n vertices: not a polynomial-time reduction.
    n = instance["n"]
    return {"n": n + 4 ** n, "edges": instance["edges"], "k": n - instance["k"]}
"""

ASSUMES_SORTED_EDGES = """
def reduce(instance):
    # Only correct if every edge is listed as [u, v] with u < v, which the
    # spec does not promise.
    assert all(u < v for u, v in instance["edges"])
    return {"n": instance["n"], "edges": instance["edges"], "k": instance["n"] - instance["k"]}
"""

NO_REDUCE_FUNCTION = """
def transform(instance):
    return instance
"""


@pytest.fixture(scope="module")
def tasks(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("tasks")
    write_task(INDSET_TO_VC, root)
    write_task(SUBSET_SUM_TO_PARTITION, root)
    write_task(THREE_SAT_TO_EXACT_COVER, root)
    return root


def run(tasks: Path, tmp_path: Path, code: str, pair: Pair = INDSET_TO_VC):
    reduce_file = tmp_path / "reduce.py"
    reduce_file.write_text(textwrap.dedent(code))
    return verify_reduction(
        reduce_file,
        tasks / pair.task_id / "inputs" / "problems.py",
        PROBLEMS[pair.source],
        PROBLEMS[pair.target],
        FAST,
        seed=pair.task_id,
    )


@pytest.mark.parametrize(
    "code",
    [GOLD_INDSET_TO_VC, PADDED_INDSET_TO_VC, PRINTS_DEBUG_OUTPUT, MUTATES_ITS_INPUT],
    ids=["gold", "polynomial-padding", "prints", "mutates-input"],
)
def test_correct_reductions_pass(tasks, tmp_path, code):
    verdict = run(tasks, tmp_path, code)
    assert verdict.status == "correct", verdict.counterexample
    assert verdict.checked["exhaustive"] == 6505
    assert verdict.checked["random"] >= FAST.min_random_checked
    assert verdict.scaling and verdict.scaling["size_exponent"] <= 4


def test_gold_number_reduction_passes(tasks, tmp_path):
    verdict = run(tasks, tmp_path, GOLD_SUBSET_SUM_TO_PARTITION, SUBSET_SUM_TO_PARTITION)
    assert verdict.status == "correct", verdict.counterexample


def test_size_exponent_reflects_growth(tasks, tmp_path):
    same_size = run(tasks, tmp_path, GOLD_INDSET_TO_VC).scaling["size_exponent"]
    padded = run(tasks, tmp_path, PADDED_INDSET_TO_VC).scaling["size_exponent"]
    assert same_size == pytest.approx(1.0)  # output size equals input size
    # Random graph densities spread the input sizes at each scale, which
    # flattens the fit, so only the ordering is asserted.
    assert padded > same_size + 0.05


@pytest.mark.parametrize(
    "code, category",
    [
        (OFF_BY_ONE, "wrong_answer_no_to_yes"),
        (CALLS_IS_YES, "solver_call"),
        (CALLS_SOLVER_HELPER, "solver_call"),
        (SWALLOWS_SOLVER_ERROR, "solver_call"),
        (INFINITE_LOOP, "timeout"),
        (RAISES, "crash"),
        (MALFORMED, "malformed_output"),
        (NOT_JSON, "malformed_output"),
        (EXPONENTIAL_OUTPUT, "blowup"),
        (NO_REDUCE_FUNCTION, "crash"),
        (ASSUMES_SORTED_EDGES, "crash"),
    ],
    ids=[
        "off-by-one", "calls-is-yes", "calls-helper", "swallows-solver-error",
        "infinite-loop", "raises", "malformed", "not-json", "exponential", "no-function",
        "assumes-sorted-edges",
    ],
)
def test_broken_reductions_fail_with_the_right_category(tasks, tmp_path, code, category):
    verdict = run(tasks, tmp_path, code)
    assert verdict.status == "wrong"
    assert verdict.category == category, verdict.counterexample


def test_identity_fails_with_a_small_counterexample(tasks, tmp_path):
    verdict = run(tasks, tmp_path, IDENTITY)
    assert verdict.status == "wrong"
    assert verdict.category.startswith("wrong_answer")
    example = verdict.counterexample
    assert example["phase"] == "exhaustive"
    # The smallest failing instances are a single edge: e.g. k = 0 is a yes
    # for Independent Set but a no for Vertex Cover (the edge needs covering).
    assert example["source_instance"]["n"] == 2
    assert example["source_instance"]["edges"] == [[0, 1]]
    assert example["expected"] != example["got"]


def test_unsolvable_targets_are_inconclusive_not_correct(tasks, tmp_path):
    reduce_file = tmp_path / "reduce.py"
    reduce_file.write_text(textwrap.dedent(GOLD_INDSET_TO_VC))
    impatient = Settings(**{**FAST.__dict__, "solver_timeout": 1e-6})
    verdict = verify_reduction(
        reduce_file,
        tasks / INDSET_TO_VC.task_id / "inputs" / "problems.py",
        PROBLEMS["independent_set"],
        PROBLEMS["vertex_cover"],
        impatient,
    )
    assert verdict.status == "inconclusive"


def test_run_without_reduce_file(tasks, tmp_path):
    run_dir = tmp_path / "some-run"
    run_dir.mkdir()
    (run_dir / "result.json").write_text(
        json.dumps({"run_id": "some-run", "task_id": INDSET_TO_VC.task_id})
    )
    result = verify_run(run_dir, tasks, FAST)
    assert result["status"] == "wrong"
    assert result["category"] == "no_reduce_file"


def test_perturb_keeps_answers():
    import random

    rng = random.Random(0)
    for key, problem in PROBLEMS.items():
        for _ in range(30):
            x = problem.random_instance(rng, problem.exhaustive_scale + 1)
            y = perturb(x, rng)
            problem.validate(y)
            assert problem.is_yes(y) == problem.is_yes(x), key


# The first false positive on the dev set (GPT-OSS, c3): one set per truth
# assignment. Right answers everywhere, but 2^m sets: not polynomial. The agent
# tested only up to 3 variables and declared it verified.
ENUMERATE_ASSIGNMENTS = """
from itertools import product

def reduce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    sets = []
    for values in product((False, True), repeat=m):
        satisfied = [m + j for j, clause in enumerate(clauses)
                     if any(values[abs(l) - 1] == (l > 0) for l in clause)]
        sets.append(list(range(m)) + satisfied)
    return {"universe_size": m + len(clauses), "sets": sets}
"""


def test_exponential_reduction_with_right_answers_is_caught(tasks, tmp_path):
    verdict = run(tasks, tmp_path, ENUMERATE_ASSIGNMENTS, THREE_SAT_TO_EXACT_COVER)
    assert verdict.status == "wrong"
    assert verdict.category in {"blowup", "timeout"}, verdict.counterexample


def test_fit_exponent():
    assert _fit_exponent([(n, n**2) for n in (2, 4, 8, 16)]) == pytest.approx(2)
    assert _fit_exponent([(5, 1)]) is None


# The first false positive in c3n (GPT-OSS, 3-SAT -> Exact Cover): solve the
# formula by brute force, then emit a fixed yes or no instance. Right answers on
# every small instance, and fast on random formulas (they are almost always
# satisfiable, so the search stops early): only the collapsed outputs give it away.
DECIDES_THEN_EMITS_CONSTANT = """
from itertools import product

def reduce(instance):
    m, clauses = instance["num_vars"], instance["clauses"]
    sat = any(
        all(any(values[abs(l) - 1] == (l > 0) for l in clause) for clause in clauses)
        for values in product((False, True), repeat=m)
    )
    if sat:
        return {"universe_size": 1, "sets": [[0]]}
    return {"universe_size": 1, "sets": []}
"""


def test_decider_with_constant_output_is_caught(tasks, tmp_path):
    verdict = run(tasks, tmp_path, DECIDES_THEN_EMITS_CONSTANT, THREE_SAT_TO_EXACT_COVER)
    assert verdict.status == "wrong"
    assert verdict.category == "constant_output", verdict.counterexample


def test_correct_reductions_have_many_distinct_outputs(tasks, tmp_path):
    verdict = run(tasks, tmp_path, GOLD_INDSET_TO_VC)
    assert verdict.scaling["distinct_outputs"] == verdict.scaling["distinct_inputs"]