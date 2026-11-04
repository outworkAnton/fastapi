from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.src.retrieve import rrf


def test_rrf_uses_ranks_only():
    fused = dict(rrf([["x", "y", "z"], ["y", "x", "z"]]))
    # x and y agree on being top-2 in both rankers; z is last twice
    assert set(fused) == {"x", "y", "z"}
    assert fused["x"] > fused["z"]
    assert fused["y"] > fused["z"]
    assert all(v > 0 for v in fused.values())


def test_rrf_rewards_agreement():
    fused = dict(rrf([["a", "b", "c"], ["a", "c", "b"]]))
    assert fused["a"] > fused["b"]
    assert fused["a"] > fused["c"]


def test_rrf_missing_item_gets_lower_score():
    fused = dict(rrf([["a", "b"], ["b"]]))
    assert fused["b"] > fused["a"]
