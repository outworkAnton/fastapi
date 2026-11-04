from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .index import BM25Index, EmbeddingIndex, keyword_hits, kw_weight
from .models import AC, Requirement, TestRecord

RRF_K = 60
DEPTH = 30
PER_AC = 10
POOL_CAP = 25


def rrf(rankings: list[list[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion. Scale-free: uses only positions, not scores."""
    scores: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))


def keyword_ranking(records: list[TestRecord], ac: AC, depth: int = DEPTH) -> list[str]:
    """Explicit signal overlap: a third, deterministic ranker.

    BM25 and embeddings are both fuzzy; a literal match on the AC's declared
    keywords is a strong signal that would otherwise be diluted by RRF.
    """
    scored: list[tuple[float, str]] = []
    for rec in records:
        hay = f"{rec.search_text} {rec.body_text}".lower()
        hits = keyword_hits(hay, ac.keywords)
        if not hits:
            continue
        scored.append((sum(kw_weight(k) for k in hits), rec.id))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [tid for _, tid in scored[:depth]]


def retrieve(
    requirements: list[Requirement],
    records: list[TestRecord],
    backend: str,
    model_name: str,
    cache_dir: Path,
) -> tuple[dict[str, list[str]], dict]:
    bm25 = BM25Index(records)
    vec = EmbeddingIndex(records, backend, model_name, cache_dir)

    pools: dict[str, list[str]] = {}
    debug: dict = {
        "rrf_k": RRF_K,
        "depth": DEPTH,
        "per_ac": PER_AC,
        "pool_cap": POOL_CAP,
        "rankers": ["bm25", "vector", "keyword"],
        "embedding_backend": vec.embedder.name,
        "embedding_cache_hit": vec.cache_hit,
        "requirements": {},
    }

    for req in requirements:
        per_ac: dict[str, list[dict]] = {}
        agg: dict[str, float] = defaultdict(float)
        for ac in req.acceptance_criteria:
            query = f"{ac.text_en} {' '.join(ac.keywords)}"
            bm = bm25.search(query, DEPTH)
            ve = vec.search(query, DEPTH)
            kw = keyword_ranking(records, ac, DEPTH)
            fused = rrf([[i for i, _ in bm], [i for i, _ in ve], kw])[:PER_AC]
            per_ac[ac.id] = [
                {
                    "test_id": tid,
                    "rrf": round(score, 6),
                    "bm25_rank": next(
                        (r for r, (i, _) in enumerate(bm, start=1) if i == tid), None
                    ),
                    "vector_rank": next(
                        (r for r, (i, _) in enumerate(ve, start=1) if i == tid), None
                    ),
                    "keyword_rank": next(
                        (r for r, i in enumerate(kw, start=1) if i == tid), None
                    ),
                }
                for tid, score in fused
            ]
            for tid, score in fused:
                agg[tid] += score

        pool = [
            tid
            for tid, _ in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))[:POOL_CAP]
        ]
        pools[req.id] = pool
        debug["requirements"][req.id] = {"per_ac": per_ac, "pool": pool}

    return pools, debug
