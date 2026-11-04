from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np

from .models import TestRecord

_STOP = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "that", "the", "this", "to", "was",
    "were", "will", "with", "response", "assert", "client", "status", "code",
}

_WORD = re.compile(r"[a-zA-Z0-9_]+")
_STEMMER = None


def _stemmer():
    global _STEMMER
    if _STEMMER is None:
        try:
            from snowballstemmer import stemmer as _make

            _STEMMER = _make("english")
        except Exception:  # pragma: no cover
            _STEMMER = False
    return _STEMMER or None


def normalize(text: str) -> str:
    return " ".join(text.split()).strip()


GENERIC_TERMS = {
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

_TERM = re.compile(r"[a-z0-9_]+")


def kw_weight(term: str) -> float:
    return 0.5 if term.lower() in GENERIC_TERMS else 1.0


def contains_term(hay: str, term: str) -> bool:
    """Substring for phrases, token-boundary match for single words.

    Prevents 'item' from matching 'items' while keeping 'status_code == 200'
    as a literal phrase.
    """
    k = term.lower()
    if _TERM.fullmatch(k):
        return re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", hay) is not None
    return k in hay


def keyword_hits(hay: str, keywords: list[str]) -> list[str]:
    return [k for k in keywords if contains_term(hay, k)]


def keyword_score(hay: str, keywords: list[str]) -> float:
    total = sum(kw_weight(k) for k in keywords)
    if not total:
        return 0.0
    got = sum(kw_weight(k) for k in keyword_hits(hay, keywords))
    return got / total


def tokenize(text: str) -> list[str]:
    stem = _stemmer()
    out: list[str] = []
    for tok in _WORD.findall(text.lower()):
        if tok in _STOP or len(tok) < 2:
            continue
        out.append(stem.stemWord(tok) if stem is not None else tok)
    return out


class BM25Index:
    def __init__(self, records: list[TestRecord]) -> None:
        from rank_bm25 import BM25Okapi

        self.ids = [r.id for r in records]
        self.corpus = [tokenize(r.search_text) for r in records]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        if self.bm25 is None:
            return []
        scores = self.bm25.get_scores(tokenize(query))
        if len(scores) == 0:
            return []
        k = min(k, len(scores))
        order = np.argsort(scores)[::-1][:k]
        return [(self.ids[int(i)], float(scores[int(i)])) for i in order]


class HashingEmbedder:
    """Deterministic hashing vectorizer (word unigrams + char n-grams).

    Used only when sentence-transformers is unavailable. It is not a
    multilingual semantic model; the English AC text is the bridge.
    """

    name = "hashing-2048"
    dim = 2048

    def _features(self, text: str) -> list[str]:
        words = _WORD.findall(text.lower())
        feats: list[str] = []
        for w in words:
            feats.append("w:" + w)
            if len(w) >= 5:
                for n in (4, 5):
                    for j in range(len(w) - n + 1):
                        feats.append(f"c{n}:" + w[j : j + n])
        return feats

    def encode(self, texts: list[str]) -> np.ndarray:
        mat = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for feat in self._features(text):
                digest = hashlib.blake2b(feat.encode("utf-8"), digest_size=8).digest()
                h = int.from_bytes(digest, "big")
                idx = h % self.dim
                sign = 1.0 if (h >> 63) & 1 else -1.0
                mat[i, idx] += sign
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return mat / norms


class STEmbedder:
    name = "sentence-transformers"

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.name = f"st:{model_name}"

    def encode(self, texts: list[str]) -> np.ndarray:
        vecs = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return np.asarray(vecs, dtype=np.float32)


def _cache_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / "emb" / f"{key}.npy"


def get_embedder(backend: str, model_name: str, cache_dir: Path):
    if backend in ("auto", "st", "sentence-transformers"):
        try:
            return STEmbedder(model_name)
        except Exception as exc:  # noqa: BLE001
            if backend != "auto":
                raise
            print(f"[index] sentence-transformers unavailable ({exc}); using hashing backend")
    return HashingEmbedder()


class EmbeddingIndex:
    def __init__(self, records: list[TestRecord], backend: str, model_name: str, cache_dir: Path) -> None:
        self.ids = [r.id for r in records]
        texts = [r.search_text for r in records]
        self.embedder = get_embedder(backend, model_name, cache_dir)
        corpus_hash = hashlib.sha256(
            (self.embedder.name + "\n" + "\n".join(texts)).encode("utf-8")
        ).hexdigest()[:16]
        path = _cache_path(cache_dir, f"corpus_{corpus_hash}")
        self.cache_hit = path.exists()
        if self.cache_hit:
            self.matrix = np.load(path)
        else:
            self.matrix = self.embedder.encode(texts)
            path.parent.mkdir(parents=True, exist_ok=True)
            np.save(path, self.matrix)

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        if not self.ids:
            return []
        vec = self.embedder.encode([query])[0]
        sims = self.matrix @ vec
        k = min(k, len(sims))
        order = np.argsort(sims)[::-1][:k]
        return [(self.ids[int(i)], float(sims[int(i)])) for i in order]
