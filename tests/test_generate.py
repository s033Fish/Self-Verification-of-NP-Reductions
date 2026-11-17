"""Tests for request building in workflow/generate.py (no Modal calls).

Run with: uv run pytest
"""

from __future__ import annotations

from pathlib import Path

import pytest

from benchmark.make_task import load_pairs, write_task
from workflow.agents import AGENT_BY_KEY
from workflow.generate import NO_SOLVER_CONDITIONS, Job, build_jobs, build_request
from workflow.tasks import load_tasks


@pytest.fixture(scope="module")
def task(tmp_path_factory):
    root = tmp_path_factory.mktemp("tasks")
    pair = next(p for p in load_pairs() if p.task_id == "clique-to-independent-set")
    write_task(pair, root)
    (loaded,) = load_tasks(root)
    return loaded


@pytest.mark.parametrize("condition", ["c1", "c3", "c3n"])
def test_each_condition_gets_the_right_problems_file(task, condition):
    descriptor_task, descriptor = task
    request = build_request(Job(descriptor_task, descriptor, AGENT_BY_KEY["deepseek"], condition, 0))
    sent = request["input_files"]["problems.py"].decode()
    no_solver = condition in NO_SOLVER_CONDITIONS
    assert request["task"]["solvers_provided"] is (not no_solver)
    assert ("def is_yes" in sent) is (not no_solver)
    assert "class Clique" in sent and "def validate" in sent


def test_request_carries_spec_and_model_settings(task):
    descriptor_task, descriptor = task
    agent = AGENT_BY_KEY["gptoss"]
    request = build_request(Job(descriptor_task, descriptor, agent, "c3", 1))
    assert request["run_id"] == "clique-to-independent-set__gptoss__c3__s1"
    assert request["max_tokens"] == agent.max_tokens
    assert "SOURCE = Clique" in request["task"]["spec"]


def test_best_of_k_expands_into_samples(task):
    jobs = build_jobs([task], [AGENT_BY_KEY["deepseek"]], ["c2", "c3n"], seeds=2, samples=3)
    assert len(jobs) == 2 * 3 + 2
    assert {j.run_id for j in jobs if j.condition == "c2"} >= {
        "clique-to-independent-set__deepseek__c2__s1__k2"
    }