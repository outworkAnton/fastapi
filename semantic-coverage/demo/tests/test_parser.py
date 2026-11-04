from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.src.ingest import parse_file


def test_parse_file_extracts_tests_and_assert_lines():
    src = """
def test_ok():
    response = client.get("/x")
    assert response.status_code == 200
    assert response.json() == {"a": 1}

def test_raises():
    with pytest.raises(ValueError):
        raise ValueError()

def helper():
    pass
"""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "test_sample.py"
        p.write_text(src, encoding="utf-8")
        recs = parse_file(p, "tests/test_sample.py", "R1")

    assert [r.name for r in recs] == ["test_ok", "test_raises"]
    ok = recs[0]
    assert ok.file == "tests/test_sample.py"
    assert ok.has_asserts
    assert len(ok.asserts) == 2
    assert ok.asserts[0].line_start == 4
    assert "status_code == 200" in ok.signals
    assert "GET /x" in ok.signals
    assert ok.asserts[0].source.startswith("assert")
    raises = recs[1]
    assert raises.asserts[0].kind == "raises"
    assert "pytest.raises" in raises.signals
