from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import yaml

from .models import RequirementsFile, Status, TestRecord, ValidationFile
from .validate import TEST_PATH, gate_evidence

REQUIRED_META = ("run_id", "commit", "validator", "embedding_backend", "seed", "files", "tests")


def read_csv_rows(path: Path) -> list[dict]:
    """Read CSV ignoring '#' comment lines and blank lines."""
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return list(csv.DictReader(lines))


def _check(results: list[dict], name: str, ok: bool, detail: str = "") -> None:
    results.append({"check": name, "ok": bool(ok), "detail": detail})


def verify(
    run_dir: Path,
    requirements_file: Path,
    manifest_csv: Path,
    gold_csv: Path,
    repo_dir: Path,
) -> tuple[list[dict], bool]:
    results: list[dict] = []

    def need(name: str) -> Path:
        p = run_dir / name
        if not p.exists():
            raise FileNotFoundError(p)
        return p

    tests = [TestRecord.model_validate(json.loads(l)) for l in need("tests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    records = {t.id: t for t in tests}
    val = ValidationFile.model_validate(json.loads(need("validated.json").read_text(encoding="utf-8")))
    payload = json.loads(need("report.json").read_text(encoding="utf-8"))
    meta = json.loads(need("run_meta.json").read_text(encoding="utf-8"))
    md = need("report.md").read_text(encoding="utf-8")
    reqs = RequirementsFile.model_validate(yaml.safe_load(requirements_file.read_text(encoding="utf-8")))

    # 1. evidence gate over all evidence
    bad = []
    cache: dict[str, list[str]] = {}
    total_ev = 0
    for res in val.results:
        for ac in res.acs:
            for ev in ac.evidence:
                total_ev += 1
                ok, reason = gate_evidence(ev, records.get(ev.test_id), repo_dir, cache)
                if not ok:
                    bad.append(f"{ac.ac_id}/{ev.test_id}: {reason}")
    _check(results, "evidence quotes resolve verbatim", not bad, "; ".join(bad[:5]))

    # 2. every cited test id exists and points to a test file
    unknown = [
        ev.test_id
        for res in val.results
        for ac in res.acs
        for ev in ac.evidence
        if ev.test_id not in records or not TEST_PATH.match(ev.file)
    ]
    _check(results, "evidence points to real test functions only", not unknown, "; ".join(unknown[:5]))

    # 3. coverage inputs present and statuses valid
    problems = []
    valid_status = {s.value for s in Status}
    for row in payload["requirements"]:
        inputs = row.get("inputs") or {}
        if not inputs.get("ac_weights") or not inputs.get("ac_status"):
            problems.append(f"{row['requirement_id']}: missing inputs")
            continue
        for ac_id, st in inputs["ac_status"].items():
            if st not in valid_status:
                problems.append(f"{row['requirement_id']}/{ac_id}: bad status {st}")
    _check(results, "coverage derived from AC weights and statuses", not problems, "; ".join(problems[:5]))

    # 4. five requirements, >=3 AC each
    counts = {r.id: len(r.acceptance_criteria) for r in reqs.requirements}
    _check(
        results,
        "5 requirements with >=3 AC each",
        len(reqs.requirements) == 5 and all(v >= 3 for v in counts.values()),
        str(counts),
    )

    # 5. manifest <=50 and files exist
    with manifest_csv.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("in_scope") == "1"]
    missing = [r["path"] for r in rows if not (repo_dir / r["path"]).exists()]
    _check(results, "manifest <=50 in-scope files, all present", len(rows) <= 50 and not missing, f"rows={len(rows)} missing={missing[:3]}")

    # 6. gold set >=20 pairs with both labels
    gold_ok = False
    gold_detail = "missing"
    if gold_csv.exists():
        grows = read_csv_rows(gold_csv)
        labels = {r.get("relevant") for r in grows}
        gold_ok = len(grows) >= 20 and {"0", "1"} <= labels
        gold_detail = f"pairs={len(grows)} labels={sorted(x for x in labels if x is not None)}"
    _check(results, "gold set >=20 pairs with both labels", gold_ok, gold_detail)

    # 7. run metadata completeness
    absent = [k for k in REQUIRED_META if k not in meta or meta[k] in (None, "")]
    _check(results, "run_meta has required fields", not absent, ",".join(absent))

    # 8. report numbers match report.json
    mismatched = []
    for row in payload["requirements"]:
        if row["coverage"] is None:
            continue
        token = f"**{row['coverage']}%**"
        if token not in md:
            mismatched.append(f"{row['requirement_id']}:{row['coverage']}")
    _check(results, "report numbers traceable to report.json", not mismatched, ",".join(mismatched))

    # 9. no production files in matched tests
    prod = [t["test_id"] for row in payload["requirements"] for t in row["tests"] if not TEST_PATH.match(t["file"])]
    _check(results, "no production files in matched tests", not prod, "; ".join(prod[:5]))

    _check(results, "evidence items collected", total_ev > 0, f"total={total_ev}")

    return results, all(r["ok"] for r in results)


def render(results: list[dict]) -> str:
    lines = []
    for r in results:
        mark = "PASS" if r["ok"] else "FAIL"
        line = f"[{mark}] {r['check']}"
        if r["detail"] and not r["ok"]:
            line += f" — {r['detail']}"
        lines.append(line)
    return "\n".join(lines)
