from __future__ import annotations

from collections import Counter

from .models import RequirementsFile, Status, ValidationFile
from .score import grade


def _esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _evidence_cell(evs) -> str:
    if not evs:
        return "—"
    ev = evs[0]
    quote = ev.quote.replace("\n", " ").strip()
    if len(quote) > 80:
        quote = quote[:77] + "..."
    return f"`{ev.file}:{ev.line_start}` — `{_esc(quote)}`"


def build_report(
    reqs: RequirementsFile,
    val: ValidationFile,
    scores: dict,
    debug: dict,
    meta: dict,
) -> tuple[dict, str]:
    by_req = {r.requirement_id: r for r in val.results}
    score_by_id = {r["requirement_id"]: r for r in scores["requirements"]}

    payload: dict = {
        "run": meta,
        "scores": {
            "overall_unweighted": scores["overall_unweighted"],
            "overall_weighted": scores["overall_weighted"],
            "unverified_requirements": scores["unverified_requirements"],
        },
        "requirements": [],
    }

    for req in reqs.requirements:
        res = by_req[req.id]
        sc = score_by_id[req.id]
        cited = Counter(ev.test_id for ac in res.acs for ev in ac.evidence)
        tests = []
        for tid, count in cited.most_common():
            rec_file, _, _ = tid.partition("::")
            lines = [ev.line_start for ac in res.acs for ev in ac.evidence if ev.test_id == tid]
            tests.append(
                {
                    "test_id": tid,
                    "file": rec_file,
                    "line": min(lines) if lines else None,
                    "citations": count,
                }
            )
        payload["requirements"].append(
            {
                "requirement_id": req.id,
                "title": req.title,
                "weight": req.weight,
                "coverage": sc["coverage"],
                "grade": sc["grade"],
                "confidence": sc["confidence"],
                "verified": sc["verified"],
                "inputs": {
                    "ac_weights": sc["ac_weights"],
                    "ac_status": sc["ac_status"],
                    "ac_confidence": sc["ac_confidence"],
                    "formula": "coverage = 100 * sum(w*status_score) / sum(w)",
                },
                "tests": tests,
                "acs": [ac.model_dump(mode="json") for ac in res.acs],
                "gaps": res.gaps,
                "pool_size": len(res.pool),
            }
        )

    payload["methodology"] = {
        "rrf_k": debug.get("rrf_k"),
        "depth": debug.get("depth"),
        "per_ac": debug.get("per_ac"),
        "pool_cap": debug.get("pool_cap"),
        "embedding_backend": debug.get("embedding_backend"),
        "retrieval": debug,
    }

    return payload, render_markdown(payload, reqs, meta)


def render_markdown(payload: dict, reqs: RequirementsFile, meta: dict) -> str:
    titles = {r.id: r for r in reqs.requirements}
    lines: list[str] = []
    lines.append("# Coverage Report: Semantic Coverage Analysis")
    lines.append("")
    lines.append(f"**Run ID**: `{meta.get('run_id', 'n/a')}`  ")
    lines.append(f"**Repository**: `{meta.get('repo_url', 'n/a')}` @ `{meta.get('commit', 'n/a')}`  ")
    lines.append(f"**Validator**: `{meta.get('validator', 'n/a')}`  ")
    lines.append(f"**Embedding backend**: `{meta.get('embedding_backend', 'n/a')}`  ")
    lines.append(f"**Files in scope**: {meta.get('files', 'n/a')} / tests: {meta.get('tests', 'n/a')}  ")
    lines.append(f"**Overall coverage (unweighted)**: {payload['scores']['overall_unweighted']}%  ")
    lines.append(f"**Overall coverage (weighted by requirement weight)**: {payload['scores']['overall_weighted']}%")
    lines.append("")
    lines.append("## Summary table")
    lines.append("")
    lines.append("| Requirement ID | Title | Text | Coverage | Tests | Confidence | Evidence |")
    lines.append("|---|---|---|---|---|---|---|")

    for row in payload["requirements"]:
        req = titles[row["requirement_id"]]
        text = req.gherkin.strip().splitlines()[0] if req.gherkin.strip() else req.title
        tests = "<br>".join(f"`{t['test_id']}`" for t in row["tests"][:4]) or "—"
        cov = "unverified" if row["coverage"] is None else f"**{row['coverage']}%**"
        ev_cell = "—"
        for ac in row["acs"]:
            if ac["evidence"]:
                e = ac["evidence"][0]
                quote = e["quote"].replace("\n", " ").strip()
                if len(quote) > 80:
                    quote = quote[:77] + "..."
                ev_cell = f"`{e['file']}:{e['line_start']}` — `{_esc(quote)}`"
                break
        lines.append(
            "| {id} | {title} | {text} | {cov} | {tests} | {conf} | {ev} |".format(
                id=row["requirement_id"],
                title=_esc(row["title"]),
                text=_esc(text),
                cov=cov,
                tests=tests,
                conf=row["confidence"],
                ev=ev_cell,
            )
        )

    lines.append("")
    lines.append("## Per-requirement detail")
    lines.append("")

    for row in payload["requirements"]:
        req = titles[row["requirement_id"]]
        lines.append(f"### {row['requirement_id']}: {row['title']}")
        lines.append("")
        lines.append(f"**Coverage**: {row['coverage']}% ({row['grade']})  ")
        lines.append(f"**Confidence**: {row['confidence']}  ")
        lines.append(f"**Requirement weight**: {row['weight']}  ")
        lines.append(f"**Candidate pool**: {row['pool_size']} tests")
        lines.append("")
        lines.append("```gherkin")
        lines.append(req.gherkin.strip())
        lines.append("```")
        lines.append("")
        lines.append("**Acceptance criteria**")
        lines.append("")
        lines.append("| AC | Weight | Status | Confidence | Evidence | Reasoning |")
        lines.append("|---|---|---|---|---|---|")
        for ac in row["acs"]:
            ev = "—"
            if ac["evidence"]:
                e = ac["evidence"][0]
                ev = f"`{e['file']}:{e['line_start']}-{e['line_end']}`"
            lines.append(
                f"| {ac['ac_id']} | {row['inputs']['ac_weights'].get(ac['ac_id'])} | "
                f"{ac['status']} | {ac['confidence']} | {ev} | {_esc(ac['reasoning'])} |"
            )
        lines.append("")
        if row["acs"]:
            lines.append("**Evidence excerpts**")
            lines.append("")
            for ac in row["acs"]:
                for e in ac["evidence"]:
                    lines.append(f"- `{ac['ac_id']}` → `{e['file']}:{e['line_start']}-{e['line_end']}` ({e['test_id']})")
                    lines.append("")
                    lines.append("  ```python")
                    lines.append("  " + e["quote"].replace("\n", "\n  "))
                    lines.append("  ```")
                    lines.append("")
        if row["gaps"]:
            lines.append("**Gaps**")
            lines.append("")
            for g in row["gaps"]:
                lines.append(f"- {g}")
            lines.append("")

    lines.append("## Methodology")
    lines.append("")
    lines.append(
        "Coverage is computed per requirement over an explicit acceptance-criteria checklist:\n"
        "`coverage = 100 * sum(w_a * s_a) / sum(w_a)` where `s_a` is 1.0 for covered, "
        "0.5 for partial, 0.0 for absent. Confidence is the same weighted mean over "
        "per-AC confidences, capped at 0.3 when an AC has no accepted evidence."
    )
    lines.append("")
    lines.append(
        f"Retrieval: BM25 + embeddings fused with Reciprocal Rank Fusion (k={meta.get('rrf_k', 60)}), "
        f"depth {meta.get('depth')} per ranker, top {meta.get('per_ac')} per AC, "
        f"requirement pool capped at {meta.get('pool_cap')}."
    )
    lines.append("")
    lines.append(
        "Evidence gate: every quote is verified as a verbatim substring of the cited line "
        "range in a file matching `tests/**/test_*.py`. A failed check downgrades the AC to "
        "`absent`; nothing is taken on trust."
    )
    lines.append("")
    lines.append("## Run metadata")
    lines.append("")
    for k in (
        "run_id",
        "timestamp",
        "repo_url",
        "commit",
        "validator",
        "model",
        "embedding_backend",
        "seed",
        "files",
        "tests",
        "tests_without_asserts",
        "python",
        "packages",
        "llm_calls",
        "llm_tokens",
    ):
        if k in meta:
            lines.append(f"- **{k}**: `{meta[k]}`")
    lines.append("")
    return "\n".join(lines)
