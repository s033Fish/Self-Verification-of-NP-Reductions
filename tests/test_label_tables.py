"""Tests for workflow/label_tables.py."""

from __future__ import annotations

import csv

import pytest

from workflow.label_tables import gaps, main

FIELDS = ["run_id", "agent", "condition", "famous", "admits", "cause", "spec_gap"]


def write(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_gaps_split_on_semicolons():
    assert gaps({"spec_gap": "poly_time; large_instances"}) == ["poly_time", "large_instances"]
    assert gaps({"spec_gap": ""}) == []


def test_tables(tmp_path, capsys):
    rows = [
        {"run_id": "a", "agent": "gptoss", "condition": "c3n", "famous": "False", "admits": "True",
         "cause": "shortcut", "spec_gap": "poly_time; large_instances"},
        {"run_id": "b", "agent": "gptoss", "condition": "c3n", "famous": "True", "admits": "False",
         "cause": "gadget", "spec_gap": "no_instances"},
        {"run_id": "c", "agent": "deepseek", "condition": "c5x", "famous": "True", "admits": "False",
         "cause": "gadget", "spec_gap": "no_instances"},
    ]
    write(tmp_path / "labels.csv", rows)
    main([str(tmp_path / "labels.csv")])
    text = (tmp_path / "label_tables.md").read_text()
    assert "| GPT-OSS | c3n | 2 | 1 | 1 |" in text      # shortcut, gadget
    assert "| DeepSeek | c5x | 1 | 0 | 1 |" in text
    assert "1 of 1." in text                           # the one shortcut admits it


def test_unlabeled_rows_are_refused(tmp_path):
    write(tmp_path / "labels.csv", [{"run_id": "a", "agent": "gptoss", "condition": "c3", "famous": "True",
                                     "admits": "", "cause": "", "spec_gap": ""}])
    with pytest.raises(SystemExit):
        main([str(tmp_path / "labels.csv")])