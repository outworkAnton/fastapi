# Coverage Report: Semantic Coverage Analysis

**Run ID**: `run_20261103T193532Z`  
**Repository**: `https://github.com/fastapi/fastapi.git` @ `5cb6272ed7e3e07eaf6978e1e65b94aca76fa8e0`  
**Validator**: `offline`  
**Embedding backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`  
**Files in scope**: 50 / tests: 649  
**Overall coverage (unweighted)**: 97.8%  
**Overall coverage (weighted by requirement weight)**: 97.8%

## Summary table

| Requirement ID | Title | Text | Coverage | Tests | Confidence | Evidence |
|---|---|---|---|---|---|---|
| R1 | Валидация тела запроса по Pydantic-модели | Feature: Request body validation | **100%** | `tests/test_router_include_context.py::test_effective_body_fields_from_app_router_include_and_route_match_openapi`<br>`tests/test_body_alias_choices.py::test_embedded_body_requires_an_object`<br>`tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error`<br>`tests/test_request_params/test_body/test_list.py::test_required_list_str_schema` | 0.8 | `tests/test_router_include_context.py:652` — `assert response.status_code == 200` |
| R2 | Dependency Injection: кэширование и teardown | Feature: Dependency injection caching | **89%** | `tests/test_dependency_cache.py::test_sub_counter`<br>`tests/test_dependency_cache.py::test_sub_counter_no_cache`<br>`tests/test_dependency_overrides.py::test_override_with_sub_decorator_depends_k_bar`<br>`tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function` | 0.72 | `tests/test_dependency_cache.py:68` — `assert response.json() == {"counter": 1, "subcounter": 1}` |
| R3 | HTTP Basic аутентификация | Feature: HTTP Basic authentication | **100%** | `tests/test_security_http_basic_optional.py::test_security_http_basic`<br>`tests/test_security_http_base_optional.py::test_security_http_base_no_credentials`<br>`tests/test_security_http_base.py::test_security_http_base_no_credentials`<br>`tests/test_router_include_context.py::test_get_openapi_accepts_filtered_route_contexts_with_effective_paths` | 0.79 | `tests/test_security_http_basic_optional.py:26` — `assert response.json() == {"username": "john", "password": "secret"}` |
| R4 | Обработка ошибок и кастомные exception handlers | Feature: Exception handling | **100%** | `tests/test_exception_handlers.py::test_override_http_exception`<br>`tests/test_exception_handlers.py::test_override_request_validation_exception`<br>`tests/test_exception_handlers.py::test_override_server_error_exception_response`<br>`tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield` | 0.8 | `tests/test_exception_handlers.py:61` — `assert response.json() == {"exception": "http-exception"}` |
| R5 | Сериализация ответа по response_model | Feature: Response model filtering | **100%** | `tests/test_response_model_data_filter.py::test_filter_second_level_model`<br>`tests/test_jsonable_encoder.py::test_encode_dict_include_exclude_list`<br>`tests/test_pydantic_v1_error.py::test_raises_pydantic_v1_model_in_additional_responses_model` | 0.76 | `tests/test_response_model_data_filter.py:68` — `assert response.json() == {         "name": "Nibbler",         "owner": {"ema...` |

## Per-requirement detail

### R1: Валидация тела запроса по Pydantic-модели

**Coverage**: 100% (Full)  
**Confidence**: 0.8  
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
| R1.AC1 | 2 | covered | 0.8 | `tests/test_router_include_context.py:652-652` | matched 3/3 keywords via test_effective_body_fields_from_app_router_include_and_route_match_openapi |
| R1.AC2 | 3 | covered | 0.8 | `tests/test_body_alias_choices.py:139-142` | matched 3/3 keywords via test_embedded_body_requires_an_object |
| R1.AC3 | 3 | covered | 0.8 | `tests/test_multi_body_errors.py:43-53` | matched 3/3 keywords via test_jsonable_encoder_requiring_error |
| R1.AC4 | 1 | covered | 0.8 | `tests/test_request_params/test_body/test_list.py:39-50` | matched 3/3 keywords via test_required_list_str_schema |

**Evidence excerpts**

- `R1.AC1` → `tests/test_router_include_context.py:652-652` (tests/test_router_include_context.py::test_effective_body_fields_from_app_router_include_and_route_match_openapi)

  ```python
  assert response.status_code == 200
  ```

- `R1.AC2` → `tests/test_body_alias_choices.py:139-142` (tests/test_body_alias_choices.py::test_embedded_body_requires_an_object)

  ```python
  assert [(error["type"], error["loc"]) for error in response.json()["detail"]] == [
          ("missing", ["body", "items"]),
          ("missing", ["body", "first"]),
      ]
  ```

- `R1.AC3` → `tests/test_multi_body_errors.py:43-53` (tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error)

  ```python
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

- `R1.AC4` → `tests/test_request_params/test_body/test_list.py:39-50` (tests/test_request_params/test_body/test_list.py::test_required_list_str_schema)

  ```python
  assert app.openapi()["components"]["schemas"][body_model_name] == {
          "properties": {
              "p": {
                  "items": {"type": "string"},
                  "title": "P",
                  "type": "array",
              },
          },
          "required": ["p"],
          "title": body_model_
  ```

### R2: Dependency Injection: кэширование и teardown

**Coverage**: 89% (Good)  
**Confidence**: 0.72  
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
| R2.AC1 | 2 | covered | 0.8 | `tests/test_dependency_cache.py:68-68` | matched 3/3 keywords via test_sub_counter |
| R2.AC2 | 3 | covered | 0.8 | `tests/test_dependency_cache.py:78-78` | matched 3/3 keywords via test_sub_counter_no_cache |
| R2.AC3 | 2 | covered | 0.73 | `tests/test_dependency_overrides.py:299-299` | matched 2/3 keywords via test_override_with_sub_decorator_depends_k_bar; missing ['dependency_overrides'] |
| R2.AC4 | 2 | partial | 0.53 | `tests/test_dependency_yield_scope.py:232-232` | matched 1/2 keywords via test_app_level_dep_scope_function; missing ['contextmanager'] |

**Evidence excerpts**

- `R2.AC1` → `tests/test_dependency_cache.py:68-68` (tests/test_dependency_cache.py::test_sub_counter)

  ```python
  assert response.json() == {"counter": 1, "subcounter": 1}
  ```

- `R2.AC2` → `tests/test_dependency_cache.py:78-78` (tests/test_dependency_cache.py::test_sub_counter_no_cache)

  ```python
  assert response.json() == {"counter": 2, "subcounter": 1}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:299-299` (tests/test_dependency_overrides.py::test_override_with_sub_decorator_depends_k_bar)

  ```python
  assert response.status_code == 200
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:232-232` (tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function)

  ```python
  assert response.json() == {"detail": "Exception after yield"}
  ```

**Gaps**

- R2.AC4: matched 1/2 keywords via test_app_level_dep_scope_function; missing ['contextmanager']

### R3: HTTP Basic аутентификация

**Coverage**: 100% (Full)  
**Confidence**: 0.79  
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
| R3.AC1 | 3 | covered | 0.8 | `tests/test_security_http_basic_optional.py:26-26` | matched 3/3 keywords via test_security_http_basic |
| R3.AC2 | 2 | covered | 0.8 | `tests/test_security_http_base_optional.py:44-44` | matched 2/2 keywords via test_security_http_base_no_credentials |
| R3.AC3 | 3 | covered | 0.8 | `tests/test_security_http_base.py:33-33` | matched 3/3 keywords via test_security_http_base_no_credentials |
| R3.AC4 | 1 | covered | 0.73 | `tests/test_router_include_context.py:178-178` | matched 2/3 keywords via test_get_openapi_accepts_filtered_route_contexts_with_effective_paths; missing ['HTTPBasic'] |

**Evidence excerpts**

- `R3.AC1` → `tests/test_security_http_basic_optional.py:26-26` (tests/test_security_http_basic_optional.py::test_security_http_basic)

  ```python
  assert response.json() == {"username": "john", "password": "secret"}
  ```

- `R3.AC2` → `tests/test_security_http_base_optional.py:44-44` (tests/test_security_http_base_optional.py::test_security_http_base_no_credentials)

  ```python
  assert response.status_code == 200, response.text
  ```

- `R3.AC3` → `tests/test_security_http_base.py:33-33` (tests/test_security_http_base.py::test_security_http_base_no_credentials)

  ```python
  assert response.status_code == 401, response.text
  ```

- `R3.AC4` → `tests/test_router_include_context.py:178-178` (tests/test_router_include_context.py::test_get_openapi_accepts_filtered_route_contexts_with_effective_paths)

  ```python
  assert "HTTPBearer" in schema["components"]["securitySchemes"]
  ```

### R4: Обработка ошибок и кастомные exception handlers

**Coverage**: 100% (Full)  
**Confidence**: 0.8  
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
| R4.AC1 | 2 | covered | 0.8 | `tests/test_exception_handlers.py:61-61` | matched 3/3 keywords via test_override_http_exception |
| R4.AC2 | 2 | covered | 0.8 | `tests/test_exception_handlers.py:66-66` | matched 2/2 keywords via test_override_request_validation_exception |
| R4.AC3 | 3 | covered | 0.8 | `tests/test_exception_handlers.py:78-78` | matched 2/2 keywords via test_override_server_error_exception_response |
| R4.AC4 | 1 | covered | 0.8 | `tests/test_exception_handlers.py:84-85` | matched 3/3 keywords via test_traceback_for_dependency_with_yield |

**Evidence excerpts**

- `R4.AC1` → `tests/test_exception_handlers.py:61-61` (tests/test_exception_handlers.py::test_override_http_exception)

  ```python
  assert response.json() == {"exception": "http-exception"}
  ```

- `R4.AC2` → `tests/test_exception_handlers.py:66-66` (tests/test_exception_handlers.py::test_override_request_validation_exception)

  ```python
  assert response.status_code == 200
  ```

- `R4.AC3` → `tests/test_exception_handlers.py:78-78` (tests/test_exception_handlers.py::test_override_server_error_exception_response)

  ```python
  assert response.status_code == 500
  ```

- `R4.AC4` → `tests/test_exception_handlers.py:84-85` (tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield)

  ```python
  with pytest.raises(ValueError) as exc_info:
          client.get("/dependency-with-yield")
  ```

### R5: Сериализация ответа по response_model

**Coverage**: 100% (Full)  
**Confidence**: 0.76  
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
| R5.AC1 | 3 | covered | 0.73 | `tests/test_response_model_data_filter.py:68-71` | matched 2/3 keywords via test_filter_second_level_model; missing ['password'] |
| R5.AC2 | 3 | covered | 0.8 | `tests/test_response_model_data_filter.py:68-71` | matched 3/3 keywords via test_filter_second_level_model |
| R5.AC3 | 2 | covered | 0.73 | `tests/test_jsonable_encoder.py:90-90` | matched 2/3 keywords via test_encode_dict_include_exclude_list; missing ['response.json()'] |
| R5.AC4 | 1 | covered | 0.8 | `tests/test_pydantic_v1_error.py:64-70` | matched 2/2 keywords via test_raises_pydantic_v1_model_in_additional_responses_model |

**Evidence excerpts**

- `R5.AC1` → `tests/test_response_model_data_filter.py:68-71` (tests/test_response_model_data_filter.py::test_filter_second_level_model)

  ```python
  assert response.json() == {
          "name": "Nibbler",
          "owner": {"email": "johndoe@example.com"},
      }
  ```

- `R5.AC2` → `tests/test_response_model_data_filter.py:68-71` (tests/test_response_model_data_filter.py::test_filter_second_level_model)

  ```python
  assert response.json() == {
          "name": "Nibbler",
          "owner": {"email": "johndoe@example.com"},
      }
  ```

- `R5.AC3` → `tests/test_jsonable_encoder.py:90-90` (tests/test_jsonable_encoder.py::test_encode_dict_include_exclude_list)

  ```python
  assert jsonable_encoder(pet, include=["name"]) == {"name": "Firulais"}
  ```

- `R5.AC4` → `tests/test_pydantic_v1_error.py:64-70` (tests/test_pydantic_v1_error.py::test_raises_pydantic_v1_model_in_additional_responses_model)

  ```python
  with pytest.raises(PydanticV1NotSupportedError):
  
          @app.get(
              "/responses", response_model=None, responses={400: {"model": ErrorModelV1}}
          )
          def endpoint():  # pragma: no cover
              return {"ok": True}
  ```

## Methodology

Coverage is computed per requirement over an explicit acceptance-criteria checklist:
`coverage = 100 * sum(w_a * s_a) / sum(w_a)` where `s_a` is 1.0 for covered, 0.5 for partial, 0.0 for absent. Confidence is the same weighted mean over per-AC confidences, capped at 0.3 when an AC has no accepted evidence.

Retrieval: BM25 + embeddings fused with Reciprocal Rank Fusion (k=60), depth 20 per ranker, top 10 per AC, requirement pool capped at 25.

Evidence gate: every quote is verified as a verbatim substring of the cited line range in a file matching `tests/**/test_*.py`. A failed check downgrades the AC to `absent`; nothing is taken on trust.

## Run metadata

- **run_id**: `run_20261103T193532Z`
- **timestamp**: `2026-11-03T19:35:32.609743+00:00`
- **repo_url**: `https://github.com/fastapi/fastapi.git`
- **commit**: `5cb6272ed7e3e07eaf6978e1e65b94aca76fa8e0`
- **validator**: `offline`
- **model**: `None`
- **embedding_backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`
- **seed**: `42`
- **files**: `50`
- **tests**: `649`
- **tests_without_asserts**: `0`
- **python**: `3.12.10`
- **packages**: `{'openai': '3.43.0', 'numpy': '2.5.4', 'rank-bm25': '0.2.2', 'pydantic': '2.14.2', 'PyYAML': '6.0.3', 'sentence-transformers': '6.2.0'}`
- **llm_calls**: `0`
