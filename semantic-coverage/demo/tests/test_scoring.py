from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.src.models import AC, ACResult, Evidence, Requirement, RequirementResult, Status
from demo.src.score import aggregate, grade, requirement_confidence, requirement_coverage

EV = [
    Evidence(
        test_id="tests/test_x.py::test_x",
        file="tests/test_x.py",
        line_start=2,
        line_end=2,
        quote="assert True",
    )
]


def _req():
    return Requirement(
        id="R1",
        title="t",
        weight=3,
        acceptance_criteria=[
            AC(id="R1.AC1", text_ru="a", text_en="a", weight=3, check="c", keywords=["x"]),
            AC(id="R1.AC2", text_ru="b", text_en="b", weight=1, check="c", keywords=["y"]),
        ],
    )


def test_weighted_coverage():
    req = _req()
    res = RequirementResult(
        requirement_id="R1",
        acs=[
            ACResult(
                ac_id="R1.AC1",
                status=Status.covered,
                confidence=0.8,
                evidence=EV,
                reasoning="",
            ),
            ACResult(ac_id="R1.AC2", status=Status.absent, confidence=0.6, evidence=[], reasoning=""),
        ],
        provider="offline",
    )
    assert requirement_coverage(req, res) == 75  # (3*1.0 + 1*0.0) / 4
    assert requirement_confidence(req, res) == 0.75
    assert grade(75) == "Good"


def test_confidence_capped_without_evidence():
    req = _req()
    res = RequirementResult(
        requirement_id="R1",
        acs=[
            ACResult(ac_id="R1.AC1", status=Status.covered, confidence=0.9, evidence=[], reasoning=""),
            ACResult(ac_id="R1.AC2", status=Status.absent, confidence=0.6, evidence=[], reasoning=""),
        ],
        provider="offline",
    )
    # covered without evidence is capped at 0.3: (3*0.3 + 1*0.6) / 4 = 0.375
    assert requirement_confidence(req, res) == 0.38


def test_unverified_has_no_coverage():
    req = _req()
    res = RequirementResult(requirement_id="R1", acs=[], provider="openai", verified=False)
    assert requirement_coverage(req, res) is None
    out = aggregate([req], [res])
    assert out["overall_weighted"] is None
    assert out["unverified_requirements"] == ["R1"]


def test_grade_boundaries():
    assert grade(100) == "Full"
    assert grade(90) == "Full"
    assert grade(89) == "Good"
    assert grade(40) == "Partial"
    assert grade(1) == "Weak"
    assert grade(0) == "None"
    assert grade(None) == "Unverified"
