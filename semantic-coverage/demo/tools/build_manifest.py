"""Build demo/file_manifest.csv: curated, reproducible test-file selection.

Selection is intentional (domain-driven) rather than pure top-N by size:
each requirement gets a small set of files that actually exercise it, plus
a control group from unrelated domains to measure false positives.

Run:
    python demo/tools/build_manifest.py --repo .repos/fastapi --out demo/file_manifest.csv
"""

from __future__ import annotations

import argparse
import ast
import csv
from pathlib import Path

TARGETS: list[tuple[str, str]] = [
    # R1 - request body validation
    ("R1", "tests/test_request_params/test_body/test_required_str.py"),
    ("R1", "tests/test_request_params/test_body/test_optional_str.py"),
    ("R1", "tests/test_request_params/test_body/test_optional_list.py"),
    ("R1", "tests/test_request_params/test_body/test_nullable_and_defaults.py"),
    ("R1", "tests/test_request_params/test_body/test_list.py"),
    ("R1", "tests/test_multi_body_errors.py"),
    ("R1", "tests/test_body_alias_choices.py"),
    ("R1", "tests/test_union_body.py"),
    ("R1", "tests/test_union_body_discriminator.py"),
    ("R1", "tests/test_get_request_body.py"),
    # R2 - dependency injection
    ("R2", "tests/test_dependency_cache.py"),
    ("R2", "tests/test_dependency_overrides.py"),
    ("R2", "tests/test_dependency_contextmanager.py"),
    ("R2", "tests/test_dependency_yield_scope.py"),
    ("R2", "tests/test_dependency_models.py"),
    ("R2", "tests/test_dependency_duplicates.py"),
    ("R2", "tests/test_dependency_class.py"),
    ("R2", "tests/test_dependency_paramless.py"),
    ("R2", "tests/test_dependency_partial.py"),
    ("R2", "tests/test_dependency_wrapped.py"),
    # R3 - HTTP Basic
    ("R3", "tests/test_security_http_basic_optional.py"),
    ("R3", "tests/test_security_http_basic_realm.py"),
    ("R3", "tests/test_security_http_basic_realm_description.py"),
    ("R3", "tests/test_security_http_base.py"),
    ("R3", "tests/test_security_http_base_optional.py"),
    # R4 - error handling
    ("R4", "tests/test_exception_handlers.py"),
    ("R4", "tests/test_validation_error_context.py"),
    ("R4", "tests/test_starlette_exception.py"),
    ("R4", "tests/test_custom_middleware_exception.py"),
    ("R4", "tests/test_additional_responses_custom_validationerror.py"),
    ("R4", "tests/test_additional_responses_default_validationerror.py"),
    ("R4", "tests/test_pydantic_v1_error.py"),
    # R5 - response_model
    ("R5", "tests/test_response_model_data_filter.py"),
    ("R5", "tests/test_response_model_data_filter_no_inheritance.py"),
    ("R5", "tests/test_response_model_include_exclude.py"),
    ("R5", "tests/test_response_by_alias.py"),
    ("R5", "tests/test_response_model_as_return_annotation.py"),
    ("R5", "tests/test_serialize_response_model.py"),
    ("R5", "tests/test_response_model_invalid.py"),
    ("R5", "tests/test_response_model_sub_types.py"),
]

CONTROLS: list[str] = [
    "tests/test_path.py",
    "tests/test_router_include_context.py",
    "tests/test_query.py",
    "tests/test_sse.py",
    "tests/test_union_form_normalization.py",
    "tests/test_jsonable_encoder.py",
    "tests/test_params_repr.py",
    "tests/test_telemetry/test_http.py",
    "tests/test_header_cookie_alias_choices.py",
    "tests/test_tutorial/test_bigger_applications/test_main.py",
]

REASONS = {
    "R1": "request body validation domain",
    "R2": "dependency injection and caching domain",
    "R3": "HTTP security scheme domain",
    "R4": "exception handling domain",
    "R5": "response model serialization domain",
    "control": "negative control, unrelated domain",
}


def count_tests(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".repos/fastapi")
    ap.add_argument("--out", default="demo/file_manifest.csv")
    args = ap.parse_args()

    root = Path(args.repo)
    rows: list[dict[str, str | int]] = []
    missing: list[str] = []

    for domain, rel in TARGETS + [("control", c) for c in CONTROLS]:
        p = root / rel
        if not p.exists():
            missing.append(rel)
            continue
        rows.append(
            {
                "path": rel,
                "tests_count": count_tests(p),
                "domain": domain,
                "selected_reason": REASONS[domain],
                "in_scope": 1,
            }
        )

    if missing:
        print("MISSING FILES:")
        for m in missing:
            print("  ", m)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["path", "tests_count", "domain", "selected_reason", "in_scope"]
        )
        w.writeheader()
        w.writerows(rows)

    total_tests = sum(int(r["tests_count"]) for r in rows)
    by_domain: dict[str, int] = {}
    for r in rows:
        by_domain[str(r["domain"])] = by_domain.get(str(r["domain"]), 0) + 1

    print(f"wrote {out} rows={len(rows)} tests={total_tests}")
    print("by domain:", by_domain)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
