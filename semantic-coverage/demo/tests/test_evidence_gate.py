from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.src.models import AssertRecord, Evidence, TestRecord as Rec
from demo.src.validate import gate_evidence


def _setup(tmp: str):
    repo = Path(tmp)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text(
        "def test_x():\n    assert response.status_code == 422\n", encoding="utf-8"
    )
    rec = Rec(
        id="tests/test_x.py::test_x",
        file="tests/test_x.py",
        name="test_x",
        qualname="test_x",
        line_start=1,
        line_end=2,
        asserts=[AssertRecord(line_start=2, line_end=2, source="assert response.status_code == 422")],
        has_asserts=True,
    )
    return repo, rec


def test_gate_accepts_verbatim_quote():
    with tempfile.TemporaryDirectory() as d:
        repo, rec = _setup(d)
        ev = Evidence(
            test_id=rec.id,
            file=rec.file,
            line_start=2,
            line_end=2,
            quote="assert response.status_code == 422",
        )
        ok, reason = gate_evidence(ev, rec, repo, {})
        assert ok, reason


def test_gate_rejects_invented_quote():
    with tempfile.TemporaryDirectory() as d:
        repo, rec = _setup(d)
        ev = Evidence(
            test_id=rec.id,
            file=rec.file,
            line_start=2,
            line_end=2,
            quote="assert response.status_code == 500",
        )
        ok, reason = gate_evidence(ev, rec, repo, {})
        assert not ok
        assert "not found" in reason


def test_gate_rejects_production_file():
    with tempfile.TemporaryDirectory() as d:
        repo, rec = _setup(d)
        ev = Evidence(
            test_id=rec.id,
            file="app/main.py",
            line_start=2,
            line_end=2,
            quote="assert response.status_code == 422",
        )
        ok, reason = gate_evidence(ev, rec, repo, {})
        assert not ok
        assert "not a test file" in reason
