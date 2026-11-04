from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import ROOT, Settings, get_settings
from .ingest import ingest, load_records
from .models import RequirementsFile, TestRecord, ValidationFile
from .report import build_report
from .retrieve import retrieve
from .score import aggregate
from .validate import validate_offline, validate_openai
from .verify import read_csv_rows, render, verify

RUNS = ROOT / "artifacts"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_reqs(path: Path) -> RequirementsFile:
    return RequirementsFile.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def _pkg_versions() -> dict[str, str]:
    from importlib.metadata import PackageNotFoundError, version

    out: dict[str, str] = {}
    for name in ("openai", "numpy", "rank-bm25", "pydantic", "PyYAML", "sentence-transformers"):
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = "absent"
    return out


def _commit(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _remote(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "remote", "get-url", "origin"], text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _resolve_run(arg: str | None, create_new: bool = False) -> Path:
    if arg:
        p = Path(arg)
        if not p.is_absolute():
            p = ROOT / p
        p.mkdir(parents=True, exist_ok=True)
        return p
    RUNS.mkdir(parents=True, exist_ok=True)
    if not create_new:
        existing = sorted([p for p in RUNS.iterdir() if p.is_dir() and p.name.startswith("run_")])
        if existing:
            return existing[-1]
    p = RUNS / f"run_{_utc()}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _write_meta(run: Path, patch: dict) -> dict:
    path = run / "run_meta.json"
    meta = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    meta.update(patch)
    meta.setdefault("run_id", run.name)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def _need(run: Path, name: str) -> Path:
    p = run / name
    if not p.exists():
        raise SystemExit(f"error: {p} not found; run the previous pipeline step first")
    return p


# --------------------------------------------------------------------- commands


def cmd_ingest(args: argparse.Namespace, s: Settings) -> Path:
    run = _resolve_run(args.run, create_new=True)
    stats = ingest(ROOT / args.manifest, s.repo_dir, run / "tests.jsonl")
    _write_meta(
        run,
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo_url": _remote(s.repo_dir),
            "repo_dir": str(s.repo_dir.relative_to(ROOT)) if s.repo_dir.is_relative_to(ROOT) else str(s.repo_dir),
            "commit": _commit(s.repo_dir),
            "validator": args.provider,
            "model": s.llm_model if args.provider == "openai" else None,
            "embedding_model": s.embedding_model,
            "embedding_backend": "pending",
            "seed": s.seed,
            "files": stats["files"],
            "tests": stats["tests"],
            "tests_without_asserts": stats["tests_without_asserts"],
            "tests_with_raises_only": stats["tests_with_raises_only"],
            "python": platform.python_version(),
            "packages": _pkg_versions(),
        },
    )
    print(f"run: {run}")
    print(f"files={stats['files']} tests={stats['tests']} without_asserts={stats['tests_without_asserts']}")
    return run


def cmd_retrieve(args: argparse.Namespace, s: Settings) -> Path:
    run = _resolve_run(args.run)
    reqs = _load_reqs(ROOT / args.requirements)
    records = load_records(_need(run, "tests.jsonl"))
    pools, debug = retrieve(
        reqs.requirements, records, s.embedding_backend, s.embedding_model, s.cache_dir
    )
    (run / "pools.json").write_text(json.dumps(pools, indent=2), encoding="utf-8")
    (run / "retrieval_debug.json").write_text(json.dumps(debug, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_meta(
        run,
        {
            "embedding_backend": debug["embedding_backend"],
            "rrf_k": debug["rrf_k"],
            "depth": debug["depth"],
            "per_ac": debug["per_ac"],
            "pool_cap": debug["pool_cap"],
            "embedding_cache_hit": debug["embedding_cache_hit"],
        },
    )
    print(f"pools: " + ", ".join(f"{k}={len(v)}" for k, v in pools.items()))
    print(f"embedding backend: {debug['embedding_backend']}")
    return run


def cmd_validate(args: argparse.Namespace, s: Settings) -> Path:
    run = _resolve_run(args.run)
    reqs = _load_reqs(ROOT / args.requirements)
    records = load_records(_need(run, "tests.jsonl"))
    by_id = {r.id: r for r in records}
    pools = json.loads(_need(run, "pools.json").read_text(encoding="utf-8"))

    if args.provider == "offline":
        val = validate_offline(reqs.requirements, pools, by_id, s.repo_dir)
        calls = 0
    else:
        val = validate_openai(reqs.requirements, pools, by_id, s.repo_dir, s, run)
        calls = len(reqs.requirements)

    (run / "validated.json").write_text(
        val.model_dump_json(indent=2), encoding="utf-8"
    )
    _write_meta(run, {"validator": val.provider, "model": val.model, "llm_calls": calls})
    for res in val.results:
        print(f"{res.requirement_id}: " + ", ".join(f"{a.ac_id}={a.status.value}" for a in res.acs))
    return run


def cmd_report(args: argparse.Namespace, s: Settings) -> Path:
    run = _resolve_run(args.run)
    reqs = _load_reqs(ROOT / args.requirements)
    val = ValidationFile.model_validate(json.loads(_need(run, "validated.json").read_text(encoding="utf-8")))
    scores = aggregate(reqs.requirements, val.results)
    debug = json.loads(_need(run, "retrieval_debug.json").read_text(encoding="utf-8"))
    meta = json.loads(_need(run, "run_meta.json").read_text(encoding="utf-8"))

    payload, md = build_report(reqs, val, scores, debug, meta)
    (run / "report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (run / "report.md").write_text(md, encoding="utf-8")

    header = (
        f"<!-- generated from {run.name}/report.md; do not edit by hand -->\n"
        f"<!-- run: {run.name} | commit: {meta.get('commit')} | validator: {meta.get('validator')} -->\n\n"
    )
    (ROOT / "coverage_report.md").write_text(header + md, encoding="utf-8")
    print(f"coverage: unweighted={scores['overall_unweighted']} weighted={scores['overall_weighted']}")
    for row in scores["requirements"]:
        print(f"  {row['requirement_id']}: {row['coverage']}% ({row['grade']}), conf={row['confidence']}")
    return run


def cmd_metrics(args: argparse.Namespace, s: Settings) -> Path:
    run = _resolve_run(args.run)
    gold = ROOT / args.gold
    pools = json.loads(_need(run, "pools.json").read_text(encoding="utf-8"))
    debug = json.loads(_need(run, "retrieval_debug.json").read_text(encoding="utf-8"))
    reqs = _load_reqs(ROOT / args.requirements)

    rows: list[dict] = []
    if gold.exists():
        rows = read_csv_rows(gold)

    # top-5 per requirement from the RRF aggregate in debug
    top5: dict[str, list[str]] = {}
    for rid, data in debug["requirements"].items():
        agg: dict[str, float] = {}
        for item in data["per_ac"].values():
            for entry in item:
                agg[entry["test_id"]] = agg.get(entry["test_id"], 0.0) + entry["rrf"]
        top5[rid] = [tid for tid, _ in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]

    labeled = {(r["requirement_id"], r["test_id"]): int(r["relevant"]) for r in rows}

    p5: list[float] = []
    for rid in top5:
        hits = 0
        for tid in top5[rid]:
            hits += labeled.get((rid, tid), 0)
        p5.append(hits / len(top5[rid]) if top5[rid] else 0.0)
    precision_at_5 = round(sum(p5) / len(p5), 4) if p5 else None

    recall_scores: list[float] = []
    for req in reqs.requirements:
        relevant = {tid for (rid, tid), rel in labeled.items() if rid == req.id and rel == 1}
        if not relevant:
            continue
        pool = set(pools.get(req.id, []))
        recall_scores.append(len(relevant & pool) / len(relevant))
    recall_at_pool = round(sum(recall_scores) / len(recall_scores), 4) if recall_scores else None

    # stability: offline retrieval is deterministic; re-run 3 times and compare pools
    records = load_records(_need(run, "tests.jsonl"))
    runs: list[dict[str, list[str]]] = []
    for _ in range(3):
        p, _d = retrieve(reqs.requirements, records, s.embedding_backend, s.embedding_model, s.cache_dir)
        runs.append(p)
    jaccards: list[float] = []
    for rid in pools:
        sets = [set(r[rid]) for r in runs]
        union = set().union(*sets)
        inter = set.intersection(*sets) if sets else set()
        jaccards.append(len(inter) / len(union) if union else 1.0)
    stability = round(sum(jaccards) / len(jaccards), 4) if jaccards else None

    metrics = {
        "run_id": run.name,
        "gold_pairs": len(rows),
        "positive_pairs": sum(1 for r in rows if r.get("relevant") == "1"),
        "precision_at_5": precision_at_5,
        "recall_at_pool": recall_at_pool,
        "pool_cap": debug.get("pool_cap"),
        "stability_jaccard_3_runs": stability,
        "top5": top5,
        "targets": {"precision_at_5": 0.8, "recall_at_pool": 0.8, "stability": 0.9},
    }
    (run / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: metrics[k] for k in ("gold_pairs", "precision_at_5", "recall_at_pool", "stability_jaccard_3_runs")}, indent=2))
    return run


def cmd_verify(args: argparse.Namespace, s: Settings) -> int:
    run = _resolve_run(args.run)
    results, ok = verify(
        run,
        ROOT / args.requirements,
        ROOT / args.manifest,
        ROOT / args.gold,
        s.repo_dir,
    )
    print(render(results))
    if getattr(args, "json", False):
        (run / "verify.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("\nRESULT:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def cmd_selfcheck(args: argparse.Namespace, s: Settings) -> int:
    print(f"base_url={s.llm_base_url}")
    print(f"model={s.llm_model}")
    print(f"api_key={'set' if s.llm_api_key else 'EMPTY'}")
    print(f"embedding_model={s.embedding_model} backend={s.embedding_backend}")
    print(f"repo={s.repo_dir} commit={_commit(s.repo_dir)}")
    if not s.llm_api_key:
        print("LLM: not configured (offline validator only)")
        return 0
    try:
        from openai import OpenAI

        c = OpenAI(base_url=s.llm_base_url, api_key=s.llm_api_key)
        ids = [m.id for m in c.models.list()]
        print(f"models: {ids[:8]}")
        print("model_present:", s.llm_model in ids)
        return 0 if s.llm_model in ids else 2
    except Exception as exc:  # noqa: BLE001
        print(f"LLM probe failed: {type(exc).__name__}: {exc}")
        return 3


def cmd_all(args: argparse.Namespace, s: Settings) -> int:
    run = cmd_ingest(args, s)
    args.run = str(run)
    cmd_retrieve(args, s)
    cmd_validate(args, s)
    cmd_report(args, s)
    gold = ROOT / args.gold
    if gold.exists():
        cmd_metrics(args, s)
    return cmd_verify(args, s)


def main(argv: list[str] | None = None) -> int:
    s = get_settings()
    ap = argparse.ArgumentParser(prog="demo.cli", description="Semantic coverage pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--run", default=None, help="run directory (default: latest or new)")
        p.add_argument("--requirements", default="demo/requirements.yaml")
        p.add_argument("--manifest", default="demo/file_manifest.csv")
        p.add_argument("--gold", default="demo/gold_set.csv")
        p.add_argument("--provider", choices=["offline", "openai"], default=s.validator)

    p = sub.add_parser("ingest")
    common(p)
    p.set_defaults(fn=cmd_ingest)

    p = sub.add_parser("retrieve")
    common(p)
    p.set_defaults(fn=cmd_retrieve)

    p = sub.add_parser("validate")
    common(p)
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("report")
    common(p)
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("metrics")
    common(p)
    p.set_defaults(fn=cmd_metrics)

    p = sub.add_parser("verify")
    common(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("selfcheck")
    p.set_defaults(fn=cmd_selfcheck)

    p = sub.add_parser("all")
    common(p)
    p.set_defaults(fn=cmd_all)

    args = ap.parse_args(argv)
    rc = args.fn(args, s)
    return rc if isinstance(rc, int) else 0


if __name__ == "__main__":
    sys.exit(main())
