# Coverage Report: Semantic Coverage Analysis

**Run ID**: `run_20261105T142506Z`  
**Repository**: `https://github.com/fastapi/fastapi.git` @ `5e376c47094a98d2b808e9995412c36f33041e57`  
**Validator**: `openai`  
**Embedding backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`  
**Files in scope**: 50 / tests: 649  
**Overall coverage (unweighted)**: 97.6%  
**Overall coverage (weighted by AC weight)**: 97.8%

## Summary table

| Requirement ID | Title | Text | Coverage | Tests | Confidence | Evidence |
|---|---|---|---|---|---|---|
| R1 | Валидация тела запроса по Pydantic-модели | Feature: Request body validation | **100%** | `tests/test_multi_body_errors.py::test_put_correct_body`<br>`tests/test_body_alias_choices.py::test_embedded_body_requires_an_object`<br>`tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error`<br>`tests/test_request_params/test_body/test_required_str.py::test_required_str_schema` | 0.95 | `tests/test_multi_body_errors.py:25` — `assert response.status_code == 200, response.text     assert response.json() ...` |
| R2 | Dependency Injection: кэширование и teardown | Feature: Dependency injection caching | **100%** | `tests/test_dependency_overrides.py::test_override_with_sub_decorator_depends_k_bar`<br>`tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function`<br>`tests/test_dependency_cache.py::test_sub_counter`<br>`tests/test_dependency_cache.py::test_sub_counter_no_cache` | 1.0 | `tests/test_dependency_cache.py:64` — `assert response.json() == {"counter": 1, "subcounter": 1}` |
| R3 | HTTP Basic аутентификация | Feature: HTTP Basic authentication | **100%** | `tests/test_security_http_basic_optional.py::test_security_http_basic`<br>`tests/test_security_http_basic_optional.py::test_security_http_basic_no_credentials`<br>`tests/test_security_http_basic_optional.py::test_security_http_basic_invalid_credentials`<br>`tests/test_security_http_basic_optional.py::test_openapi_schema` | 1.0 | `tests/test_security_http_basic_optional.py:23` — `assert response.status_code == 200, response.text     assert response.json() ...` |
| R4 | Обработка ошибок и кастомные exception handlers | Feature: Exception handling | **88%** | `tests/test_exception_handlers.py::test_override_http_exception`<br>`tests/test_exception_handlers.py::test_override_request_validation_exception`<br>`tests/test_exception_handlers.py::test_override_server_error_exception_response` | 0.91 | `tests/test_exception_handlers.py:58` — `assert response.status_code == 200     assert response.json() == {"exception"...` |
| R5 | Сериализация ответа по response_model | Feature: Response model filtering | **100%** | `tests/test_response_model_data_filter_no_inheritance.py::test_filter_top_level_model`<br>`tests/test_response_model_data_filter_no_inheritance.py::test_filter_second_level_model`<br>`tests/test_response_model_include_exclude.py::test_nested_include_simple`<br>`tests/test_response_model_include_exclude.py::test_nested_exclude_simple` | 1.0 | `tests/test_response_model_data_filter_no_inheritance.py:61` — `assert response.json() == {"email": "johndoe@example.com"}` |

## Per-requirement detail

### R1: Валидация тела запроса по Pydantic-модели

**Coverage**: 100% (Full)  
**Confidence**: 0.95  
**Requirement weight**: 3  
**Candidate pool**: 25 tests

```gherkin
Feature: Request body validation
  Scenario: Valid body
    Given app with POST /items and Pydantic model Item
    When client sends a valid JSON body
    Then response is 200 and echoes the payload
  Scenario: Missing required field
    Given app with a model that requires field "p"
    When client sends {} or null
    Then response is 422 and detail reports a missing field with loc
  Scenario: Value constraint violation
    Given app with a model field constrained by gt=0
    When client sends a value below the constraint
    Then response is 422 with error type greater_than and loc
```

**Acceptance criteria**

| AC | Weight | Status | Confidence | Evidence | Reasoning |
|---|---|---|---|---|---|
| R1.AC1 | 2 | covered | 0.95 | `tests/test_multi_body_errors.py:25-37` | Test test_put_correct_body sends a valid request body and asserts status_code 200 and response.json() equals snapshot containing the submitted item, directly covering the AC. |
| R1.AC2 | 3 | covered | 0.95 | `tests/test_body_alias_choices.py:134-142` | Test test_embedded_body_requires_an_object asserts status_code 422 and detail errors with type missing and loc in body, matching the AC. |
| R1.AC3 | 3 | covered | 0.95 | `tests/test_multi_body_errors.py:40-53` | Test test_jsonable_encoder_requiring_error asserts status_code 422 and detail contains type greater_than with loc in body, matching the AC. |
| R1.AC4 | 1 | covered | 0.95 | `tests/test_request_params/test_body/test_required_str.py:35-46` | Test test_required_str_schema asserts that the OpenAPI schema for the body model includes required list containing field p, matching the AC. |

**Evidence excerpts**

- `R1.AC1` → `tests/test_multi_body_errors.py:25-37` (tests/test_multi_body_errors.py::test_put_correct_body)

  ```python
      assert response.status_code == 200, response.text
      assert response.json() == snapshot(
          {
              "item": [
                  {
                      "name": "Foo",
                      "age": "5",
                  }
              ]
          }
      )
  ```

- `R1.AC2` → `tests/test_body_alias_choices.py:134-142` (tests/test_body_alias_choices.py::test_embedded_body_requires_an_object)

  ```python
      assert response.status_code == 422
      assert [(error["type"], error["loc"]) for error in response.json()["detail"]] == [
          ("missing", ["body", "items"]),
          ("missing", ["body", "first"]),
      ]
  ```

- `R1.AC3` → `tests/test_multi_body_errors.py:40-53` (tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error)

  ```python
      assert response.status_code == 422, response.text
      assert response.json() == {
          "detail": [
              {
                  "type": "greater_than",
                  "loc": ["body", 0, "age"],
                  "msg": "Input should be greater than 0",
                  "input": -1.0,
                  "ctx": {"gt": 0},
              }
          ]
      }
  ```

- `R1.AC4` → `tests/test_request_params/test_body/test_required_str.py:35-46` (tests/test_request_params/test_body/test_required_str.py::test_required_str_schema)

  ```python
      assert app.openapi()["components"]["schemas"][body_model_name] == {
          "properties": {
              "p": {"title": "P", "type": "string"},
          },
          "required": ["p"],
          "title": body_model_name,
          "type": "object",
      }
  ```

### R2: Dependency Injection: кэширование и teardown

**Coverage**: 100% (Full)  
**Confidence**: 1.0  
**Requirement weight**: 2  
**Candidate pool**: 25 tests

```gherkin
Feature: Dependency injection caching
  Scenario: Cached dependency
    Given a dependency that increments a counter
    When a route depends on it twice on the same request
    Then the dependency is called once
  Scenario: Cache disabled
    Given a dependency used with use_cache=False
    When the route is called once
    Then the dependency is called twice
  Scenario: Override
    Given app.dependency_overrides for a dependency
    When the route is called
    Then the override result is used
```

**Acceptance criteria**

| AC | Weight | Status | Confidence | Evidence | Reasoning |
|---|---|---|---|---|---|
| R2.AC1 | 2 | covered | 1.0 | `tests/test_dependency_cache.py:64-71` | Test test_sub_counter asserts response.json() == {"counter": 1, "subcounter": 1} on a single request, matching the required counter and subcounter both equal 1. |
| R2.AC2 | 3 | covered | 1.0 | `tests/test_dependency_cache.py:74-81` | Test test_sub_counter_no_cache asserts response.json() == {"counter": 2, "subcounter": 1}, showing counter differs from subcounter due to use_cache False. |
| R2.AC3 | 2 | covered | 1.0 | `tests/test_dependency_overrides.py:296-301` | Test test_override_with_sub_decorator_depends_k_bar returns status code 200 and overridden dependency result {"in": "decorator-depends"}, proving dependency_overrides replaces the implementation. |
| R2.AC4 | 2 | covered | 1.0 | `tests/test_dependency_yield_scope.py:222-232` | Test test_app_level_dep_scope_function asserts status 503 and detail "Exception after yield", indicating that the code after the yield (teardown) was executed and raised an exception. |

**Evidence excerpts**

- `R2.AC1` → `tests/test_dependency_cache.py:64-71` (tests/test_dependency_cache.py::test_sub_counter)

  ```python
  assert response.json() == {"counter": 1, "subcounter": 1}
  ```

- `R2.AC2` → `tests/test_dependency_cache.py:74-81` (tests/test_dependency_cache.py::test_sub_counter_no_cache)

  ```python
  assert response.json() == {"counter": 2, "subcounter": 1}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:296-301` (tests/test_dependency_overrides.py::test_override_with_sub_decorator_depends_k_bar)

  ```python
  assert response.status_code == 200
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:296-301` (tests/test_dependency_overrides.py::test_override_with_sub_decorator_depends_k_bar)

  ```python
  assert response.json() == {"in": "decorator-depends"}
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:222-232` (tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function)

  ```python
  assert response.status_code == 503
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:222-232` (tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function)

  ```python
  assert response.json() == {"detail": "Exception after yield"}
  ```

### R3: HTTP Basic аутентификация

**Coverage**: 100% (Full)  
**Confidence**: 1.0  
**Requirement weight**: 3  
**Candidate pool**: 25 tests

```gherkin
Feature: HTTP Basic authentication
  Scenario: Valid credentials
    Given an endpoint protected by HTTPBasic
    When client sends valid Basic credentials
    Then response is 200 and contains the username
  Scenario: Invalid header
    Given an endpoint protected by HTTPBasic
    When client sends a malformed Authorization header
    Then response is 401 with WWW-Authenticate Basic
  Scenario: Optional auth
    Given HTTPBasic(auto_error=False)
    When client sends no credentials
    Then response is 200 with a fallback message
```

**Acceptance criteria**

| AC | Weight | Status | Confidence | Evidence | Reasoning |
|---|---|---|---|---|---|
| R3.AC1 | 3 | covered | 1.0 | `tests/test_security_http_basic_optional.py:23-26` | Test asserts status_code == 200 and response JSON username equals john. |
| R3.AC2 | 2 | covered | 1.0 | `tests/test_security_http_basic_optional.py:29-32` | Test without credentials asserts status_code == 200 and fallback message 'Create an account first'. |
| R3.AC3 | 3 | covered | 1.0 | `tests/test_security_http_basic_optional.py:35-41` | Test with invalid credentials asserts status_code == 401, WWW-Authenticate header equals Basic, and detail Not authenticated. |
| R3.AC4 | 1 | covered | 1.0 | `tests/test_security_http_basic_optional.py:53-79` | OpenAPI schema test asserts components.securitySchemes.HTTPBasic has type http and scheme basic. |

**Evidence excerpts**

- `R3.AC1` → `tests/test_security_http_basic_optional.py:23-26` (tests/test_security_http_basic_optional.py::test_security_http_basic)

  ```python
      assert response.status_code == 200, response.text
      assert response.json() == {"username": "john", "password": "secret"}
  ```

- `R3.AC2` → `tests/test_security_http_basic_optional.py:29-32` (tests/test_security_http_basic_optional.py::test_security_http_basic_no_credentials)

  ```python
      assert response.status_code == 200, response.text
      assert response.json() == {"msg": "Create an account first"}
  ```

- `R3.AC3` → `tests/test_security_http_basic_optional.py:35-41` (tests/test_security_http_basic_optional.py::test_security_http_basic_invalid_credentials)

  ```python
      assert response.status_code == 401, response.text
      assert response.headers["WWW-Authenticate"] == "Basic"
      assert response.json() == {"detail": "Not authenticated"}
  ```

- `R3.AC4` → `tests/test_security_http_basic_optional.py:53-79` (tests/test_security_http_basic_optional.py::test_openapi_schema)

  ```python
              "components": {
                  "securitySchemes": {"HTTPBasic": {"type": "http", "scheme": "basic"}}
              }
  ```

### R4: Обработка ошибок и кастомные exception handlers

**Coverage**: 88% (Good)  
**Confidence**: 0.91  
**Requirement weight**: 2  
**Candidate pool**: 25 tests

```gherkin
Feature: Exception handling
  Scenario: HTTPException handler override
    Given app registered a handler for HTTPException
    When route raises HTTPException
    Then the custom handler response is returned
  Scenario: Validation error handler
    Given app registered a handler for RequestValidationError
    When request fails validation
    Then the custom handler response is returned
  Scenario: Unhandled server error
    Given raise_server_exceptions is False
    When route raises RuntimeError
    Then response is 500 with the custom body
```

**Acceptance criteria**

| AC | Weight | Status | Confidence | Evidence | Reasoning |
|---|---|---|---|---|---|
| R4.AC1 | 2 | covered | 1.0 | `tests/test_exception_handlers.py:58-61` | The test directly asserts the required status code 200 and response body {"exception": "http-exception"}, exactly matching the AC check. |
| R4.AC2 | 2 | covered | 1.0 | `tests/test_exception_handlers.py:64-67` | The test directly asserts the required status code 200 and response body {"exception": "request-validation"}, exactly matching the AC check. |
| R4.AC3 | 3 | covered | 1.0 | `tests/test_exception_handlers.py:75-79` | The test asserts status code 500 and response body {"exception": "server-error"}, matching the AC check. The paired 'raises' test (test_override_server_error_exception_raises) uses raise_server_exceptions=True, so this response test corresponds to raise_server_exceptions=False. |
| R4.AC4 | 1 | absent | 0.3 | — | The test explicitly checks that the last traceback frame's line number equals the line where the original exception was raised in the dependency. \| evidence_unverified: tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield: quote not found verbatim in the cited lines |

**Evidence excerpts**

- `R4.AC1` → `tests/test_exception_handlers.py:58-61` (tests/test_exception_handlers.py::test_override_http_exception)

  ```python
      assert response.status_code == 200
      assert response.json() == {"exception": "http-exception"}
  ```

- `R4.AC2` → `tests/test_exception_handlers.py:64-67` (tests/test_exception_handlers.py::test_override_request_validation_exception)

  ```python
      assert response.status_code == 200
      assert response.json() == {"exception": "request-validation"}
  ```

- `R4.AC3` → `tests/test_exception_handlers.py:75-79` (tests/test_exception_handlers.py::test_override_server_error_exception_response)

  ```python
      assert response.status_code == 500
      assert response.json() == {"exception": "server-error"}
  ```

### R5: Сериализация ответа по response_model

**Coverage**: 100% (Full)  
**Confidence**: 1.0  
**Requirement weight**: 2  
**Candidate pool**: 25 tests

```gherkin
Feature: Response model filtering
  Scenario: Top level filtering
    Given route declared response_model=UserBase
    When handler returns a richer object
    Then extra fields are removed from the response
  Scenario: Nested filtering
    Given nested response model
    When handler returns objects with extra nested fields
    Then nested extra fields are removed
  Scenario: Include and exclude
    Given response_model_include or exclude
    When handler returns the model
    Then only the selected fields are present
```

**Acceptance criteria**

| AC | Weight | Status | Confidence | Evidence | Reasoning |
|---|---|---|---|---|---|
| R5.AC1 | 3 | covered | 1.0 | `tests/test_response_model_data_filter_no_inheritance.py:61-65` | Test asserts top-level response JSON exactly equals {"email": "johndoe@example.com"}, proving fields like password are stripped. |
| R5.AC2 | 3 | covered | 1.0 | `tests/test_response_model_data_filter_no_inheritance.py:68-73` | Test asserts nested owner object contains only email, demonstrating stripping of extra nested fields. |
| R5.AC3 | 2 | covered | 1.0 | `tests/test_response_model_include_exclude.py:116-124` | Include and exclude tests assert filtered response JSON with only included fields present and excluded fields absent, directly covering response_model_include/exclude. |
| R5.AC4 | 1 | covered | 1.0 | `tests/test_response_model_invalid.py:10-16` | Test explicitly uses pytest.raises(FastAPIError) with response_model=NonPydanticModel, showing invalid response_model raises an error. |

**Evidence excerpts**

- `R5.AC1` → `tests/test_response_model_data_filter_no_inheritance.py:61-65` (tests/test_response_model_data_filter_no_inheritance.py::test_filter_top_level_model)

  ```python
      assert response.json() == {"email": "johndoe@example.com"}
  ```

- `R5.AC2` → `tests/test_response_model_data_filter_no_inheritance.py:68-73` (tests/test_response_model_data_filter_no_inheritance.py::test_filter_second_level_model)

  ```python
      assert response.json() == {
          "name": "Nibbler",
          "owner": {"email": "johndoe@example.com"},
      }
  ```

- `R5.AC3` → `tests/test_response_model_include_exclude.py:116-124` (tests/test_response_model_include_exclude.py::test_nested_include_simple)

  ```python
      assert response.status_code == 200, response.text
      assert response.json() == {
          "baz": "simple_include model2 baz",
          "ref": {"foo": "simple_include model foo"},
      }
  ```

- `R5.AC3` → `tests/test_response_model_include_exclude.py:138-144` (tests/test_response_model_include_exclude.py::test_nested_exclude_simple)

  ```python
      assert response.status_code == 200, response.text
      assert response.json() == {
          "baz": "simple_exclude model2 baz",
          "ref": {"foo": "simple_exclude model foo"},
      }
  ```

- `R5.AC4` → `tests/test_response_model_invalid.py:10-16` (tests/test_response_model_invalid.py::test_invalid_response_model_raises)

  ```python
      with pytest.raises(FastAPIError):
          app = FastAPI()
  
          @app.get("/", response_model=NonPydanticModel)
          def read_root():
              pass
  ```

## Methodology

Coverage is computed per requirement over an explicit acceptance-criteria checklist:
`coverage = 100 * sum(w_a * s_a) / sum(w_a)` where `s_a` is 1.0 for covered, 0.5 for partial, 0.0 for absent. Confidence is the same weighted mean over per-AC confidences, capped at 0.3 when an AC has no accepted evidence.

Retrieval: BM25 + embeddings fused with Reciprocal Rank Fusion (k=60), depth 30 per ranker, top 10 per AC, requirement pool capped at 25.

Evidence gate: every quote is verified as a verbatim substring of the cited line range in a file matching `tests/**/test_*.py`. A failed check downgrades the AC to `absent`; nothing is taken on trust.

## Run metadata

- **run_id**: `run_20261105T142506Z`
- **timestamp**: `2026-11-05T14:25:07.374852+00:00`
- **repo_url**: `https://github.com/fastapi/fastapi.git`
- **commit**: `5e376c47094a98d2b808e9995412c36f33041e57`
- **validator**: `openai`
- **model**: `deepseek-v4-pro`
- **embedding_backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`
- **seed**: `42`
- **files**: `50`
- **tests**: `649`
- **tests_without_asserts**: `0`
- **python**: `3.12.10`
- **packages**: `{'openai': '3.43.0', 'numpy': '2.5.4', 'rank-bm25': '0.2.2', 'pydantic': '2.14.2', 'PyYAML': '6.0.3', 'sentence-transformers': '6.2.0'}`
- **llm_calls**: `5`
