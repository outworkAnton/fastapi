from __future__ import annotations

import ast
import csv
import json
from pathlib import Path

from .models import AssertRecord, TestRecord

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _signals(node: ast.AST) -> list[str]:
    out: list[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            f = sub.func
            # client.get("/path")
            if (
                isinstance(f, ast.Attribute)
                and f.attr in HTTP_METHODS
                and isinstance(f.value, ast.Name)
                and f.value.id == "client"
                and sub.args
                and isinstance(sub.args[0], ast.Constant)
                and isinstance(sub.args[0].value, str)
            ):
                out.append(f"{f.attr.upper()} {sub.args[0].value}")
            # pytest.raises(...)
            if isinstance(f, ast.Attribute) and f.attr == "raises":
                out.append("pytest.raises")
            if isinstance(f, ast.Name) and f.id == "raises":
                out.append("pytest.raises")
            # response.json()
            if isinstance(f, ast.Attribute) and f.attr == "json":
                out.append("response.json()")
        elif isinstance(sub, ast.Compare):
            # response.status_code == 200
            left = sub.left
            if isinstance(left, ast.Attribute) and left.attr == "status_code":
                for comp in sub.comparators:
                    if isinstance(comp, ast.Constant) and isinstance(comp.value, int):
                        out.append(f"status_code == {comp.value}")
    # stable, deduplicated
    seen: set[str] = set()
    uniq: list[str] = []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def _asserts(fn: ast.AST, src: str) -> list[AssertRecord]:
    recs: list[AssertRecord] = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            segment = ast.get_source_segment(src, node) or ""
            recs.append(
                AssertRecord(
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    source=segment.rstrip(),
                    kind="assert",
                )
            )
        elif isinstance(node, ast.With):
            for item in node.items:
                call = item.context_expr
                if (
                    isinstance(call, ast.Call)
                    and (
                        (isinstance(call.func, ast.Attribute) and call.func.attr == "raises")
                        or (isinstance(call.func, ast.Name) and call.func.id == "raises")
                    )
                ):
                    segment = ast.get_source_segment(src, node) or ""
                    recs.append(
                        AssertRecord(
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            source=segment.rstrip(),
                            kind="raises",
                        )
                    )
    recs.sort(key=lambda r: r.line_start)
    return recs


def _walk_functions(
    node: ast.AST, prefix: str = ""
) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    found: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []
    for child in getattr(node, "body", []):
        if isinstance(child, ast.ClassDef):
            found.extend(_walk_functions(child, f"{prefix}{child.name}."))
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found.append((f"{prefix}{child.name}", child))
            found.extend(_walk_functions(child, f"{prefix}{child.name}."))
    return found


def parse_file(path: Path, rel: str, domain: str | None) -> list[TestRecord]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out: list[TestRecord] = []
    for qualname, fn in _walk_functions(tree):
        name = qualname.rsplit(".", 1)[-1]
        if not name.startswith("test_"):
            continue
        docstring = ast.get_docstring(fn) or ""
        asserts = _asserts(fn, src)
        signals = _signals(fn)
        words = " ".join(name.replace("test_", "").split("_"))
        body_text = (ast.get_source_segment(src, fn) or "")[:4000]
        search_text = " ".join(
            [
                words,
                docstring,
                " ".join(a.source[:500] for a in asserts[:10]),
                " ".join(signals),
            ]
        ).strip()
        out.append(
            TestRecord(
                id=f"{rel}::{qualname}",
                file=rel,
                name=name,
                qualname=qualname,
                line_start=fn.lineno,
                line_end=getattr(fn, "end_lineno", fn.lineno),
                docstring=docstring,
                asserts=asserts,
                signals=signals,
                search_text=search_text,
                body_text=body_text,
                has_asserts=bool(asserts),
                domain=domain,
            )
        )
    return out


def ingest(manifest_csv: Path, repo_dir: Path, out_jsonl: Path) -> dict[str, int]:
    records: list[TestRecord] = []
    with manifest_csv.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rel = row["path"]
            domain = row["domain"]
            path = repo_dir / rel
            if not path.exists():
                raise FileNotFoundError(path)
            records.extend(parse_file(path, rel, domain))

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r.model_dump(), ensure_ascii=False) + "\n")

    return {
        "files": len({r.file for r in records}),
        "tests": len(records),
        "tests_without_asserts": sum(1 for r in records if not r.has_asserts),
        "tests_with_raises_only": sum(
            1 for r in records if r.asserts and all(a.kind == "raises" for a in r.asserts)
        ),
    }


def load_records(path: Path) -> list[TestRecord]:
    out: list[TestRecord] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(TestRecord.model_validate(json.loads(line)))
    return out
