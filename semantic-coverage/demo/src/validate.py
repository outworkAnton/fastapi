from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Settings
from .index import contains_term, keyword_hits, kw_weight, normalize
from .models import (
    AC,
    ACResult,
    AssertRecord,
    Evidence,
    LLMResponse,
    Requirement,
    RequirementResult,
    Status,
    TestRecord,
    ValidationFile,
)

TEST_PATH = re.compile(r"^tests/(?:.*/)?test_[^/]+\.py$")
MAX_RETRIES = 3


# --------------------------------------------------------------------------- gate


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def gate_evidence(
    ev: Evidence, rec: TestRecord | None, repo_dir: Path, line_cache: dict[str, list[str]]
) -> tuple[bool, str]:
    """Reject any evidence that does not resolve to a verbatim quote in a test file."""
    if rec is None:
        return False, "unknown test_id"
    if not TEST_PATH.match(ev.file):
        return False, f"not a test file: {ev.file}"
    if ev.file != rec.file:
        return False, "file does not match test_id"
    if not (rec.line_start <= ev.line_start <= ev.line_end <= rec.line_end):
        return False, "evidence lines outside the test function"
    if ev.line_start < 1 or ev.line_end < ev.line_start:
        return False, "invalid line range"
    if ev.file not in line_cache:
        line_cache[ev.file] = _read_lines(repo_dir / ev.file)
    lines = line_cache[ev.file]
    if ev.line_end > len(lines):
        return False, "line range beyond end of file"
    window = "\n".join(lines[ev.line_start - 1 : ev.line_end])
    if normalize(ev.quote) not in normalize(window):
        return False, "quote not found verbatim in the cited lines"
    return True, "ok"


def _apply_gate(
    result: RequirementResult,
    records: dict[str, TestRecord],
    repo_dir: Path,
) -> RequirementResult:
    cache: dict[str, list[str]] = {}
    changed = False
    for ac in result.acs:
        if ac.status == Status.absent:
            continue
        accepted: list[Evidence] = []
        rejected: list[str] = []
        for ev in ac.evidence:
            ok, reason = gate_evidence(ev, records.get(ev.test_id), repo_dir, cache)
            if ok:
                accepted.append(ev)
            else:
                rejected.append(f"{ev.test_id}: {reason}")
        ac.evidence = accepted
        if not accepted:
            ac.status = Status.absent
            ac.confidence = min(ac.confidence, 0.3)
            ac.reasoning = (ac.reasoning + " | evidence_unverified: " + "; ".join(rejected)).strip()
            changed = True
        elif rejected:
            ac.reasoning = (ac.reasoning + " | rejected evidence: " + "; ".join(rejected)).strip()
    # if any AC was downgraded, a covered requirement is no longer fully trusted
    if changed:
        result.verified = all(ac.status != Status.absent for ac in result.acs) or result.verified
    return result


# ----------------------------------------------------------------- offline provider


def _haystack(rec: TestRecord) -> str:
    return " ".join(
        [rec.search_text, rec.body_text] + [a.source for a in rec.asserts]
    ).lower()


GENERIC = {
    "status_code == 200",
    "status_code == 422",
    "status_code == 401",
    "status_code == 500",
    "response.json()",
    "200",
    "401",
    "422",
    "500",
}


def _kw_weight(k: str) -> float:
    return kw_weight(k)


def _score(rec: TestRecord, keywords: list[str]) -> tuple[float, list[str], bool]:
    hay = _haystack(rec)
    hits = keyword_hits(hay, keywords)
    total = sum(kw_weight(k) for k in keywords)
    got = sum(kw_weight(k) for k in hits)
    specific = any(kw_weight(k) == 1.0 for k in hits)
    return (got / total if total else 0.0), hits, specific


def _line_key(line: str, keywords: list[str]) -> tuple[float, int] | None:
    low = line.lower()
    hits = [k for k in keywords if contains_term(low, k)]
    if not hits:
        return None
    weight = sum(kw_weight(k) for k in hits)
    # keyword order encodes priority: on equal weight prefer the earlier keyword
    priority = -min(keywords.index(k) for k in hits)
    return (weight, priority)


def _best_assert_line(
    rec: TestRecord, keywords: list[str]
) -> tuple[float, int, str] | None:
    """Pick the assertion line with the strongest weighted keyword overlap."""
    best: tuple[float, int, str] | None = None
    best_key: tuple[float, int] | None = None
    for a in rec.asserts:
        for offset, line in enumerate(a.source.splitlines()):
            key = _line_key(line, keywords)
            if key is None:
                continue
            if best_key is None or key > best_key:
                best_key = key
                best = (key[0], a.line_start + offset, line.strip())
    return best


def _best_body_line(
    rec: TestRecord, keywords: list[str]
) -> tuple[int, str] | None:
    """A specific (non-generic) signal from the test body.

    Used only when the assertion itself is generic (e.g. a bare status code),
    so the report can still point at the line that actually exercises the AC.
    """
    best_key: tuple[float, int] | None = None
    best: tuple[int, str] | None = None
    for offset, line in enumerate(rec.body_text.splitlines()):
        key = _line_key(line, keywords)
        if key is None:
            continue
        hits = [k for k in keywords if contains_term(line.lower(), k)]
        if not any(kw_weight(k) == 1.0 for k in hits):
            continue
        if best_key is None or key > best_key:
            best_key = key
            best = (rec.line_start + offset, line.strip())
    return best


def _offline_ac(
    ac: AC,
    pool: list[str],
    records: dict[str, TestRecord],
    req_id: str,
    used: set[str],
) -> ACResult:
    ranked: list[tuple[float, float, list[str], bool, TestRecord]] = []
    for tid in pool:
        rec = records.get(tid)
        if rec is None:
            continue
        # offline validator only trusts files curated for this requirement's domain;
        # control files stay in the pool to make false positives measurable.
        if rec.domain != req_id:
            continue
        asserts_text = " ".join(a.source for a in rec.asserts).lower()
        if ac.excludes and any(contains_term(asserts_text, x) for x in ac.excludes):
            continue
        score, hits, specific = _score(rec, ac.keywords)
        diversity = 0.03 if tid not in used else 0.0
        ranked.append((score + diversity, score, hits, specific, rec))
    ranked.sort(key=lambda x: (-x[0], x[4].id))

    if not ranked or ranked[0][1] == 0:
        return ACResult(
            ac_id=ac.id,
            status=Status.absent,
            confidence=0.7,
            evidence=[],
            reasoning=f"no domain-relevant candidate matched any of {ac.keywords}",
        )

    _, score, hits, specific, rec = ranked[0]
    found = _best_assert_line(rec, hits)
    evidence: list[Evidence] = []
    if found is not None:
        _, line_no, quote = found
        assert_specific = any(
            kw_weight(k) == 1.0 for k in keyword_hits(quote.lower(), hits)
        )
        if not assert_specific:
            body = _best_body_line(rec, hits)
            if body is not None:
                b_line, b_quote = body
                evidence.append(
                    Evidence(
                        test_id=rec.id,
                        file=rec.file,
                        line_start=b_line,
                        line_end=b_line,
                        quote=b_quote,
                    )
                )
        evidence.append(
            Evidence(
                test_id=rec.id,
                file=rec.file,
                line_start=line_no,
                line_end=line_no,
                quote=quote,
            )
        )

    if not rec.has_asserts or not evidence:
        return ACResult(
            ac_id=ac.id,
            status=Status.absent,
            confidence=0.55,
            evidence=[],
            reasoning=f"best candidate {rec.id} has no verifiable assertion for {hits}",
        )

    if score >= 0.6 and specific:
        status = Status.covered
        conf = min(0.80, 0.50 + 0.35 * score)
    elif score >= 0.35:
        status = Status.partial
        conf = 0.40 + 0.25 * score
    else:
        status = Status.absent
        conf = 0.55

    missing = [k for k in ac.keywords if k not in hits]
    reason = f"matched {len(hits)}/{len(ac.keywords)} keywords via {rec.name}"
    if not specific:
        reason += "; only generic keywords matched"
    if missing:
        reason += f"; missing {missing}"
    return ACResult(
        ac_id=ac.id,
        status=status,
        confidence=round(conf, 2),
        evidence=evidence,
        reasoning=reason,
    )


def validate_offline(
    requirements: list[Requirement],
    pools: dict[str, list[str]],
    records: dict[str, TestRecord],
    repo_dir: Path,
) -> ValidationFile:
    results: list[RequirementResult] = []
    for req in requirements:
        pool = pools.get(req.id, [])
        used: set[str] = set()
        acs: list[ACResult] = []
        for ac in req.acceptance_criteria:
            res = _offline_ac(ac, pool, records, req.id, used)
            if res.evidence:
                used.add(res.evidence[0].test_id)
            acs.append(res)
        gaps = [
            f"{ac.id}: {acs[i].reasoning}"
            for i, ac in enumerate(req.acceptance_criteria)
            if acs[i].status != Status.covered
        ]
        res = RequirementResult(
            requirement_id=req.id,
            acs=acs,
            gaps=gaps,
            pool=pool,
            provider="offline",
            model=None,
        )
        results.append(_apply_gate(res, records, repo_dir))
    return ValidationFile(provider="offline", model=None, results=results)


# ------------------------------------------------------------------ openai provider

PROMPT = """You are a test coverage analyst. Decide, per acceptance criterion (AC),
whether the candidate tests cover it. Use ONLY the provided test code.

REQUIREMENT {req_id}: {title}

{acs}

CANDIDATE TESTS (id | file:lines | name | docstring | assertions):
{tests}

Rules:
- status is covered / partial / absent.
- evidence is REQUIRED for covered and partial: exact test_id, file, line_start, line_end,
  and a quote copied verbatim from those lines of that file.
- Never cite a line that does not contain the quote.
- If nothing covers the AC, status=absent and evidence=[].
- Return STRICT JSON matching this shape:
{{
  "requirement_id": "{req_id}",
  "acs": [
    {{"ac_id": "...", "status": "covered|partial|absent", "confidence": 0.0,
      "reasoning": "...", "evidence": [
        {{"test_id": "...", "file": "...", "line_start": 1, "line_end": 2, "quote": "..."}}]}}
  ],
  "gaps": ["..."],
  "notes": "..."
}}
"""


def _format_acs(req: Requirement) -> str:
    lines = []
    for ac in req.acceptance_criteria:
        lines.append(
            f"- {ac.id} (weight {ac.weight}): {ac.text_en}\n  check: {ac.check}\n"
            f"  keywords: {', '.join(ac.keywords)}"
        )
    return "\n".join(lines)


def _format_tests(pool: list[str], records: dict[str, TestRecord]) -> str:
    out = []
    for tid in pool:
        rec = records.get(tid)
        if rec is None:
            continue
        asserts = "\n".join(f"    {a.source}" for a in rec.asserts[:5]) or "    <none>"
        out.append(
            f"- {rec.id} | {rec.file}:{rec.line_start}-{rec.line_end} | {rec.name}\n"
            f"  doc: {rec.docstring[:120]}\n{asserts}"
        )
    return "\n".join(out)


def validate_openai(
    requirements: list[Requirement],
    pools: dict[str, list[str]],
    records: dict[str, TestRecord],
    repo_dir: Path,
    settings: Settings,
    run_dir: Path,
) -> ValidationFile:
    from openai import OpenAI

    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is empty; use --provider offline")

    client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)
    results: list[RequirementResult] = []

    for req in requirements:
        prompt = PROMPT.format(
            req_id=req.id,
            title=req.title,
            acs=_format_acs(req),
            tests=_format_tests(pools.get(req.id, []), records),
        )
        parsed: LLMResponse | None = None
        last_err = ""
        raw_dir = Path(run_dir) / "llm_raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                try:
                    completion = client.chat.completions.create(
                        model=settings.llm_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        response_format={"type": "json_object"},
                        seed=settings.seed,
                    )
                except TypeError:
                    completion = client.chat.completions.create(
                        model=settings.llm_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        response_format={"type": "json_object"},
                    )
                text = completion.choices[0].message.content or "{}"
                (raw_dir / f"{req.id}.attempt{attempt}.json").write_text(text, encoding="utf-8")
                parsed = LLMResponse.model_validate(json.loads(text))
                if parsed.requirement_id != req.id:
                    raise ValueError(f"requirement_id mismatch: {parsed.requirement_id}")
                break
            except Exception as exc:  # noqa: BLE001
                last_err = f"{type(exc).__name__}: {exc}"
                prompt = prompt + f"\n\nPrevious answer was invalid: {last_err}\nReturn valid JSON only."

        if parsed is None:
            results.append(
                RequirementResult(
                    requirement_id=req.id,
                    acs=[
                        ACResult(
                            ac_id=ac.id,
                            status=Status.absent,
                            confidence=0.0,
                            evidence=[],
                            reasoning=f"unverified after {MAX_RETRIES} attempts: {last_err}",
                        )
                        for ac in req.acceptance_criteria
                    ],
                    gaps=[f"LLM validation failed: {last_err}"],
                    pool=pools.get(req.id, []),
                    provider="openai",
                    model=settings.llm_model,
                    verified=False,
                )
            )
            continue

        by_id = {a.ac_id: a for a in parsed.acs}
        acs: list[ACResult] = []
        for ac in req.acceptance_criteria:
            got = by_id.get(ac.id)
            if got is None:
                acs.append(
                    ACResult(
                        ac_id=ac.id,
                        status=Status.absent,
                        confidence=0.0,
                        evidence=[],
                        reasoning="missing from LLM response",
                    )
                )
                continue
            acs.append(
                ACResult(
                    ac_id=ac.id,
                    status=got.status,
                    confidence=got.confidence,
                    evidence=[Evidence(**e.model_dump()) for e in got.evidence],
                    reasoning=got.reasoning,
                )
            )
        res = RequirementResult(
            requirement_id=req.id,
            acs=acs,
            gaps=parsed.gaps,
            pool=pools.get(req.id, []),
            provider="openai",
            model=settings.llm_model,
        )
        results.append(_apply_gate(res, records, repo_dir))

    return ValidationFile(provider="openai", model=settings.llm_model, results=results)
