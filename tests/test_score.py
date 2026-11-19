"""Tests for the scorer's oracle (c4) breakdown."""

from __future__ import annotations

import math

from workflow.score import (
    collapse_best_of_k,
    feedback_rounds,
    summarize,
    summarize_oracle,
    summarize_tester,
)


def run(run_id, verified, rounds, condition="c4"):
    log = [{"round": i + 1, "status": "wrong", "feedback": "ORACLE FEEDBACK"} for i in range(rounds)]
    log.append({"status": "correct", "feedback": None})  # a passing check carries no feedback
    return {
        "run_id": run_id, "agent": {"key": "a"}, "condition": condition,
        "agent_verified": verified, "oracle_log": log,
    }


RECORDS = [
    run("fixed", True, 2),          # feedback, then correct and verified
    run("recertified", True, 1),    # feedback, verified again, still wrong
    run("gave-up", False, 3),       # feedback, not verified, wrong
    run("never-submitted", True, 0),  # claimed verified, oracle never ran, wrong
    run("clean", True, 0),          # passed the oracle the first time
]
VERDICTS = {
    "fixed": {"status": "correct"},
    "recertified": {"status": "wrong"},
    "gave-up": {"status": "wrong"},
    "never-submitted": {"status": "wrong"},
    "clean": {"status": "correct"},
}


def test_feedback_rounds_ignore_passing_checks():
    assert feedback_rounds(RECORDS[0]) == 2
    assert feedback_rounds(RECORDS[4]) == 0


def test_oracle_breakdown():
    (row,) = summarize_oracle(RECORDS, VERDICTS)
    assert row["scored"] == 5
    assert row["feedback_runs"] == 3
    assert row["mean_rounds"] == 2
    assert math.isclose(row["fixed"], 1 / 3)
    assert row["claims_after_feedback"] == 2
    assert row["fp_after_feedback"] == 1
    assert row["fp_after_feedback_runs"] == ["recertified"]
    assert row["fp_without_feedback"] == 1


def test_breakdown_adds_up_to_the_main_fp_count():
    (main,) = summarize(RECORDS, VERDICTS)
    (oracle,) = summarize_oracle(RECORDS, VERDICTS)
    wrong_but_verified = round(main["fp_rate"] * main["verified"])
    assert wrong_but_verified == oracle["fp_after_feedback"] + oracle["fp_without_feedback"]


def test_other_conditions_have_no_oracle_rows():
    assert summarize_oracle([run("x", True, 0, condition="c3n")], {"x": {"status": "wrong"}}) == []


def c5_run(run_id, writer, tester):
    return {"run_id": run_id, "agent": {"key": "a"}, "condition": "c5",
            "writer_verified": writer, "agent_verified": tester}


def test_tester_breakdown():
    records = [
        c5_run("both-right", True, True),       # correct, both verified
        c5_run("caught", True, False),          # wrong: writer verified, tester rejected
        c5_run("both-fooled", True, True),      # wrong: both verified
        c5_run("false-alarm", True, False),     # correct: tester rejected anyway
        c5_run("tester-only", False, True),     # wrong: only the tester verified
    ]
    verdicts = {
        "both-right": {"status": "correct"}, "caught": {"status": "wrong"},
        "both-fooled": {"status": "wrong"}, "false-alarm": {"status": "correct"},
        "tester-only": {"status": "wrong"},
    }
    (row,) = summarize_tester(records, verdicts)
    assert row["writer_verified"] == 4 and row["writer_fp"] == 2
    assert row["tester_verified"] == 3 and row["tester_fp"] == 2
    assert row["caught"] == 1 and row["false_alarms"] == 1
    assert row["agree"] == 2 / 5
    (main,) = summarize(records, verdicts)
    assert main["verified"] == row["tester_verified"]  # the main table grades the tester


# --- c2: pass@k --------------------------------------------------------------------


def sample(seed, k, tokens=10):
    return {
        "run_id": f"t__a__c2__s{seed}__k{k}", "agent": {"key": "a"}, "condition": "c2",
        "seed": seed, "sample": k, "usage": [{"prompt_tokens": tokens, "completion_tokens": 1}],
    }


def test_best_of_k_is_pass_at_k():
    records = [sample(s, k) for s in range(4) for k in range(3)]
    statuses = {
        0: ["wrong", "correct", "wrong"],          # one correct sample: correct
        1: ["wrong", "wrong", "wrong"],            # all wrong: wrong
        2: ["wrong", "inconclusive", "wrong"],     # none correct, one undecided
        3: ["inconclusive", "correct", "wrong"],   # a correct sample wins
    }
    verdicts = {f"t__a__c2__s{s}__k{k}": {"status": st}
                for s, row in statuses.items() for k, st in enumerate(row)}
    merged, merged_verdicts = collapse_best_of_k(records, verdicts)
    assert sorted(r["run_id"] for r in merged) == [f"t__a__c2__s{s}" for s in range(4)]
    assert [merged_verdicts[f"t__a__c2__s{s}"]["status"] for s in range(4)] == [
        "correct", "wrong", "inconclusive", "correct"]
    (row,) = summarize(records, verdicts)
    assert row["runs"] == 4 and row["inconclusive"] == 1
    assert math.isclose(row["correct"], 2 / 3)
    assert row["prompt_tokens"] == 30  # the k samples' tokens add up


def test_other_conditions_are_untouched_by_best_of_k():
    record = {"run_id": "t__a__c3__s0", "agent": {"key": "a"}, "condition": "c3", "sample": None}
    merged, verdicts = collapse_best_of_k([record], {"t__a__c3__s0": {"status": "wrong"}})
    assert merged == [record] and verdicts == {"t__a__c3__s0": {"status": "wrong"}}