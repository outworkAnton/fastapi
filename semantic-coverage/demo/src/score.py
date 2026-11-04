from __future__ import annotations

from .models import Requirement, RequirementResult, Status

STATUS_SCORE = {Status.covered: 1.0, Status.partial: 0.5, Status.absent: 0.0}


def requirement_coverage(req: Requirement, res: RequirementResult) -> int | None:
    if not res.verified:
        return None
    weights = {ac.id: ac.weight for ac in req.acceptance_criteria}
    total = sum(weights.values())
    if total == 0:
        return None
    got = 0.0
    for ac in res.acs:
        got += weights.get(ac.ac_id, 0) * STATUS_SCORE[ac.status]
    return int(round(100 * got / total))


def requirement_confidence(req: Requirement, res: RequirementResult) -> float:
    weights = {ac.id: ac.weight for ac in req.acceptance_criteria}
    total = sum(weights.values())
    if total == 0:
        return 0.0
    acc = 0.0
    for ac in res.acs:
        conf = ac.confidence
        if ac.status != Status.absent and not ac.evidence:
            conf = min(conf, 0.3)
        acc += weights.get(ac.ac_id, 0) * conf
    return round(acc / total, 2)


def grade(coverage: int | None) -> str:
    if coverage is None:
        return "Unverified"
    if coverage >= 90:
        return "Full"
    if coverage >= 70:
        return "Good"
    if coverage >= 40:
        return "Partial"
    if coverage >= 1:
        return "Weak"
    return "None"


def aggregate(requirements: list[Requirement], results: list[RequirementResult]) -> dict:
    by_id = {r.requirement_id: r for r in results}
    rows: list[dict] = []
    for req in requirements:
        res = by_id.get(req.id)
        if res is None:
            continue
        cov = requirement_coverage(req, res)
        rows.append(
            {
                "requirement_id": req.id,
                "title": req.title,
                "coverage": cov,
                "grade": grade(cov),
                "confidence": requirement_confidence(req, res),
                "verified": res.verified,
                "ac_weights": {a.id: a.weight for a in req.acceptance_criteria},
                "ac_status": {a.ac_id: a.status.value for a in res.acs},
                "ac_confidence": {a.ac_id: a.confidence for a in res.acs},
            }
        )

    verified = [r for r in rows if r["coverage"] is not None]
    covs = [int(r["coverage"]) for r in verified]
    unweighted = round(sum(covs) / len(covs), 1) if covs else None

    total_w = 0.0
    acc = 0.0
    for r in verified:
        w = float(sum(r["ac_weights"].values()))
        total_w += w
        acc += w * int(r["coverage"])
    weighted = round(acc / total_w, 1) if total_w else None

    return {
        "requirements": rows,
        "overall_unweighted": unweighted,
        "overall_weighted": weighted,
        "unverified_requirements": [
            r["requirement_id"] for r in rows if r["coverage"] is None
        ],
    }
