# Coverage Report: Semantic Coverage Analysis

**Run ID**: `run_20261104T104315Z`  
**Repository**: `https://github.com/fastapi/fastapi.git` @ `61ae7934cfd742169f5c3bf7595f8cc1a5849895`  
**Validator**: `openai`  
**Embedding backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`  
**Files in scope**: 50 / tests: 649  
**Overall coverage (unweighted)**: 97.8%  
**Overall coverage (weighted by requirement weight)**: 97.8%

## Summary table

| Requirement ID | Title | Text | Coverage | Tests | Confidence | Evidence |
|---|---|---|---|---|---|---|
| R1 | Валидация тела запроса по Pydantic-модели | Feature: Request body validation | **100%** | `tests/test_multi_body_errors.py::test_put_correct_body`<br>`tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error`<br>`tests/test_body_alias_choices.py::test_model_body_alias_choice_preserves_nested_errors`<br>`tests/test_union_form_normalization.py::test_empty_scalar_is_missing` | 0.91 | `tests/test_multi_body_errors.py:25` — `assert response.status_code == 200, response.text` |
| R2 | Dependency Injection: кэширование и teardown | Feature: Dependency injection caching | **89%** | `tests/test_dependency_cache.py::test_sub_counter`<br>`tests/test_dependency_cache.py::test_sub_counter_no_cache`<br>`tests/test_dependency_overrides.py::test_override_with_sub_main_depends_k_bar`<br>`tests/test_dependency_overrides.py::test_override_with_sub_router_depends_k_bar` | 0.85 | `tests/test_dependency_cache.py:64` — `assert response.json() == {"counter": 1, "subcounter": 1}` |
| R3 | HTTP Basic аутентификация | Feature: HTTP Basic authentication | **100%** | `tests/test_security_http_basic_optional.py::test_security_http_basic`<br>`tests/test_security_http_basic_optional.py::test_security_http_basic_no_credentials`<br>`tests/test_security_http_basic_optional.py::test_security_http_basic_invalid_credentials`<br>`tests/test_security_http_basic_optional.py::test_security_http_basic_non_basic_credentials` | 0.96 | `tests/test_security_http_basic_optional.py:23` — `assert response.status_code == 200, response.text     assert response.json() ...` |
| R4 | Обработка ошибок и кастомные exception handlers | Feature: Exception handling | **100%** | `tests/test_exception_handlers.py::test_override_http_exception`<br>`tests/test_exception_handlers.py::test_override_request_validation_exception`<br>`tests/test_exception_handlers.py::test_override_server_error_exception_response`<br>`tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield` | 0.91 | `tests/test_exception_handlers.py:58` — `assert response.status_code == 200     assert response.json() == {"exception"...` |
| R5 | Сериализация ответа по response_model | Feature: Response model filtering | **100%** | `tests/test_response_model_data_filter.py::test_filter_top_level_model`<br>`tests/test_response_model_data_filter_no_inheritance.py::test_filter_top_level_model`<br>`tests/test_response_model_data_filter.py::test_filter_second_level_model`<br>`tests/test_response_model_data_filter_no_inheritance.py::test_filter_second_level_model` | 0.93 | `tests/test_response_model_data_filter.py:59` — `assert response.json() == {"email": "johndoe@example.com"}` |

## Per-requirement detail

### R1: Валидация тела запроса по Pydantic-модели

**Coverage**: 100% (Full)  
**Confidence**: 0.91  
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
| R1.AC1 | 2 | covered | 0.85 | `tests/test_multi_body_errors.py:25-37` | test_put_correct_body sends a correct body and asserts status_code == 200 plus response.json() equal to a snapshot that contains the submitted item ("item": [{"name": "Foo", "age": "5"}]), satisfying the check 'status_code == 200 and response.json() contains the submitted item'. test_model_body_alias_choice_preserves_nested_errors provides supplementary 200 + response.json() evidence (echoing {"count": 1}), though its echo payload is minimal. Confidence slightly reduced because the echo is verified via exact snapshot equality rather than explicit containment of an independently constructed payload, and only one primary test exists. |
| R1.AC2 | 3 | covered | 0.95 | `tests/test_union_form_normalization.py:148-153` | Multiple tests assert 422 with detail type 'missing' and a loc rooted at the body. test_empty_scalar_is_missing asserts error['type'] == 'missing' and error['loc'] == ['body', branch, 'value']; test_embedded_body_requires_an_object asserts ('missing', ['body', 'items']) pairs; test_absent_body_for_required_argument asserts ('missing', location). These directly satisfy 'status_code == 422 and detail contains missing and loc' for the request body. test_main_depends also shows 422/missing/loc but for a query parameter, so it is not counted as body evidence. |
| R1.AC3 | 3 | covered | 0.9 | `tests/test_multi_body_errors.py:40-53` | test_jsonable_encoder_requiring_error asserts status_code == 422 and a detail entry with type 'greater_than' and loc ['body', 0, 'age'], i.e., a value-constraint violation inside the request body — a direct match for 'status_code == 422 and detail type is greater_than' with loc, in a body location. The test_path_param_* tests also assert 422 with type 'greater_than' and loc, but their loc is ['path', 'item_id'], so they are supplementary rather than body-scoped evidence for this requirement. |
| R1.AC4 | 1 | covered | 0.95 | `tests/test_request_params/test_body/test_required_str.py:35-46` | Several tests assert app.openapi()['components']['schemas'][body_model_name] contains a 'required' list naming the body field ('required': ['p'] or alias variants), directly satisfying 'openapi components schemas required list contains field'. test_get_request_body.py::test_openapi_schema additionally asserts a body model schema with 'required': ['name', 'price']. These are explicit OpenAPI component-schema checks for required body fields. |

**Evidence excerpts**

- `R1.AC1` → `tests/test_multi_body_errors.py:25-37` (tests/test_multi_body_errors.py::test_put_correct_body)

  ```python
  assert response.status_code == 200, response.text
  ```

- `R1.AC1` → `tests/test_multi_body_errors.py:25-37` (tests/test_multi_body_errors.py::test_put_correct_body)

  ```python
  "item": [
  ```

- `R1.AC1` → `tests/test_body_alias_choices.py:196-225` (tests/test_body_alias_choices.py::test_model_body_alias_choice_preserves_nested_errors)

  ```python
  assert response.status_code == 200
  ```

- `R1.AC2` → `tests/test_union_form_normalization.py:148-153` (tests/test_union_form_normalization.py::test_empty_scalar_is_missing)

  ```python
  assert error["loc"] == ["body", branch, "value"]
  ```

- `R1.AC2` → `tests/test_body_alias_choices.py:134-142` (tests/test_body_alias_choices.py::test_embedded_body_requires_an_object)

  ```python
  ("missing", ["body", "items"]),
  ```

- `R1.AC2` → `tests/test_request_params/test_body/test_nullable_and_defaults.py:133-139` (tests/test_request_params/test_body/test_nullable_and_defaults.py::test_absent_body_for_required_argument)

  ```python
  ("missing", location),
  ```

- `R1.AC3` → `tests/test_multi_body_errors.py:40-53` (tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error)

  ```python
  "type": "greater_than",
  ```

- `R1.AC3` → `tests/test_multi_body_errors.py:40-53` (tests/test_multi_body_errors.py::test_jsonable_encoder_requiring_error)

  ```python
  "loc": ["body", 0, "age"],
  ```

- `R1.AC3` → `tests/test_path.py:334-347` (tests/test_path.py::test_path_param_gt0_0)

  ```python
  "loc": ["path", "item_id"],
  ```

- `R1.AC4` → `tests/test_request_params/test_body/test_required_str.py:35-46` (tests/test_request_params/test_body/test_required_str.py::test_required_str_schema)

  ```python
  "required": ["p"],
  ```

- `R1.AC4` → `tests/test_request_params/test_body/test_list.py:35-50` (tests/test_request_params/test_body/test_list.py::test_required_list_str_schema)

  ```python
  "required": ["p"],
  ```

- `R1.AC4` → `tests/test_get_request_body.py:29-114` (tests/test_get_request_body.py::test_openapi_schema)

  ```python
  "required": ["name", "price"],
  ```

**Gaps**

- R1.AC1: only one primary test (test_put_correct_body) demonstrates a 200 response echoing the submitted body item; the echo is asserted via exact snapshot equality rather than explicit containment of a separately constructed payload, so the AC is met but by a single, tightly coupled test.
- R1.AC3: only one body-located greater_than test exists; the remaining greater_than tests (test_path_param_*) exercise path parameters (loc ['path', 'item_id']), not request-body fields, so they do not strengthen body-scoped coverage.
- R1.AC2: test_main_depends asserts 422/missing/loc but on a query parameter ('loc': ['query', 'q']) and therefore does not contribute body-validation evidence.

### R2: Dependency Injection: кэширование и teardown

**Coverage**: 89% (Good)  
**Confidence**: 0.85  
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
| R2.AC1 | 2 | covered | 0.95 | `tests/test_dependency_cache.py:64-71` | test_sub_counter issues a request to the cached sub-dependency endpoint and asserts the first response returns counter=1 and subcounter=1, which is exactly the AC check that a default-cached dependency is called once per request. The keyword 'subcounter' and 'response.json()' are present in the assertions. |
| R2.AC2 | 3 | covered | 0.95 | `tests/test_dependency_cache.py:74-81` | test_sub_counter_no_cache matches the AC exactly: the first request asserts counter==2 and subcounter==1, proving the dependency with use_cache=False is re-invoked within a single request while the cached sub-counter increments only once. The test name contains the keyword 'sub_counter_no_cache' and the assertions contain 'counter' and 'subcounter'. |
| R2.AC3 | 2 | covered | 0.92 | `tests/test_dependency_overrides.py:252-257` | Multiple tests in test_dependency_overrides.py assert that an overridden dependency's result is returned with a 200 status, e.g. test_override_with_sub_main_depends_k_bar returns {"in": "main-depends", "params": {"k": "bar"}} with status_code == 200, and test_override_with_sub_router_depends_k_bar / test_override_with_sub_decorator_depends_k_bar / test_override_with_sub_router_decorator_depends_k_bar confirm the same across Depends locations. These satisfy the AC check of overridden result with 200. |
| R2.AC4 | 2 | partial | 0.55 | `tests/test_dependency_yield_scope.py:222-232` | There is indirect evidence that code after yield executes: test_app_level_dep_scope_function and test_router_level_dep_scope_function assert a 503 response with detail 'Exception after yield', proving the after-yield (teardown) code path ran, and test_traceback_for_dependency_with_yield raises ValueError from a yield dependency teardown path. However, no test asserts that teardown code runs AFTER a successful (200) response is delivered (e.g., a teardown flag/log checked post-response), and the keyword 'contextmanager' does not appear in any candidate test. The successful-response yield-scope test (test_app_level_dep_scope_request) only asserts {"status": "ok"} without any teardown verification. |

**Evidence excerpts**

- `R2.AC1` → `tests/test_dependency_cache.py:64-71` (tests/test_dependency_cache.py::test_sub_counter)

  ```python
  assert response.json() == {"counter": 1, "subcounter": 1}
  ```

- `R2.AC2` → `tests/test_dependency_cache.py:74-81` (tests/test_dependency_cache.py::test_sub_counter_no_cache)

  ```python
  assert response.json() == {"counter": 2, "subcounter": 1}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:252-257` (tests/test_dependency_overrides.py::test_override_with_sub_main_depends_k_bar)

  ```python
  assert response.json() == {"in": "main-depends", "params": {"k": "bar"}}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:340-345` (tests/test_dependency_overrides.py::test_override_with_sub_router_depends_k_bar)

  ```python
  assert response.status_code == 200
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:99-102` (tests/test_dependency_overrides.py::test_decorator_depends_q_foo)

  ```python
  assert response.json() == {"in": "decorator-depends"}
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:222-232` (tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function)

  ```python
  assert response.json() == {"detail": "Exception after yield"}
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:209-212` (tests/test_dependency_yield_scope.py::test_router_level_dep_scope_function)

  ```python
  assert response.json() == {"detail": "Exception after yield"}
  ```

- `R2.AC4` → `tests/test_exception_handlers.py:82-88` (tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield)

  ```python
  with pytest.raises(ValueError) as exc_info:
          client.get("/dependency-with-yield")
  ```

**Gaps**

- R2.AC4: no test verifies teardown code executes after a successful 200 response (e.g., asserting a teardown side effect/state after the response completes); existing evidence only shows after-yield code running via exceptions that produce 503 responses.
- R2.AC4: no candidate test uses the 'contextmanager' keyword or directly asserts a teardown action (log entry, flag, cleanup list) for a normal completion path.

### R3: HTTP Basic аутентификация

**Coverage**: 100% (Full)  
**Confidence**: 0.96  
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
| R3.AC1 | 3 | covered | 0.97 | `tests/test_security_http_basic_optional.py:23-26` | Multiple tests send valid Basic credentials and assert status 200 plus the username in the response JSON ('john'), satisfying both parts of the check. Equivalent coverage also exists in test_security_http_basic_realm.py::test_security_http_basic (21-24) and test_security_http_basic_realm_description.py::test_security_http_basic (21-24). |
| R3.AC2 | 2 | covered | 0.95 | `tests/test_security_http_basic_optional.py:29-32` | The optional Basic test with no credentials asserts status 200 and the exact fallback message 'Create an account first', matching the AC check. (The similar test_security_http_base_optional.py::test_security_http_base_no_credentials also matches but uses the 'Other' scheme, not Basic.) |
| R3.AC3 | 3 | covered | 0.95 | `tests/test_security_http_basic_optional.py:35-41` | Both branches of the AC are covered in the optional Basic suite: invalid Basic credentials and non-Basic credentials each assert 401, WWW-Authenticate header exactly equal to 'Basic', and the 'Not authenticated' detail. The realm variants assert 'Basic realm="simple"' (not exact 'Basic'), so they are supplementary rather than primary evidence for the exact-equality check. |
| R3.AC4 | 1 | covered | 0.95 | `tests/test_security_http_basic_optional.py:53-79` | The OpenAPI schema tests assert the full schema including components.securitySchemes.HTTPBasic with scheme 'basic'. The realm and realm_description variants (lines 52-78 and 52-84) assert the same scheme, with the latter adding a description. |

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

- `R3.AC3` → `tests/test_security_http_basic_optional.py:44-50` (tests/test_security_http_basic_optional.py::test_security_http_basic_non_basic_credentials)

  ```python
  assert response.status_code == 401, response.text
      assert response.headers["WWW-Authenticate"] == "Basic"
      assert response.json() == {"detail": "Not authenticated"}
  ```

- `R3.AC4` → `tests/test_security_http_basic_optional.py:53-79` (tests/test_security_http_basic_optional.py::test_openapi_schema)

  ```python
  "securitySchemes": {"HTTPBasic": {"type": "http", "scheme": "basic"}}
  ```

### R4: Обработка ошибок и кастомные exception handlers

**Coverage**: 100% (Full)  
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
| R4.AC1 | 2 | covered | 0.95 | `tests/test_exception_handlers.py:58-61` | test_override_http_exception asserts exactly the AC check: status_code == 200 and response body exception == 'http-exception'. |
| R4.AC2 | 2 | covered | 0.95 | `tests/test_exception_handlers.py:64-67` | test_override_request_validation_exception asserts exactly the AC check: status_code == 200 and response body exception == 'request-validation'. |
| R4.AC3 | 3 | covered | 0.85 | `tests/test_exception_handlers.py:75-79` | test_override_server_error_exception_response asserts status_code == 500 and body exception == 'server-error', matching the AC check. The client setup with raise_server_exceptions=False is not visible in the provided assertion lines, so slight uncertainty remains, but the assertions themselves match the check verbatim. Related 500-status tests (test_sync_raise_server_error, test_async_raise_server_error, test_sync_async_raise_server_error, test_sync_sync_raise_server_error) assert only status 500 and lack the 'server-error' body check, so they are secondary corroboration only. |
| R4.AC4 | 1 | covered | 0.9 | `tests/test_exception_handlers.py:82-88` | test_traceback_for_dependency_with_yield triggers a ValueError from a dependency and asserts that the last traceback frame's path is the test file and its lineno equals the raise statement's first line number, which is exactly the AC check. |

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

- `R4.AC4` → `tests/test_exception_handlers.py:82-88` (tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield)

  ```python
  assert str(last_frame.path) == __file__
      assert last_frame.lineno == raise_value_error.__code__.co_firstlineno
  ```

### R5: Сериализация ответа по response_model

**Coverage**: 100% (Full)  
**Confidence**: 0.93  
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
| R5.AC1 | 3 | covered | 0.95 | `tests/test_response_model_data_filter.py:59-63` | Two tests assert exact equality of the full response JSON with only the 'email' field at the top level, which proves extra fields (e.g., password) are stripped by response_model serialization. Exact-equality assertions are the strongest form of 'no extra fields' check. |
| R5.AC2 | 3 | covered | 0.95 | `tests/test_response_model_data_filter.py:66-71` | Multiple tests assert exact response JSON where the nested 'owner' object contains only 'email', verifying second-level stripping by response_model. Both single-model and list-of-models variants exist in two files. |
| R5.AC3 | 2 | covered | 0.85 | `tests/test_response_model_include_exclude.py:116-124` | Tests in test_response_model_include_exclude.py assert exact filtered response JSON for both include and exclude variants (including nested cases), confirming only included fields are present and excluded fields are absent. Confidence slightly reduced because the provided snippets show only assertion lines; the actual response_model_include/response_model_exclude parameter usage is inferred from the file/test names and the exact filtered JSON shapes rather than directly visible in the cited lines. |
| R5.AC4 | 1 | covered | 0.95 | `tests/test_response_model_invalid.py:10-16` | A dedicated test wraps route creation with an invalid (non-Pydantic) response_model in pytest.raises(FastAPIError). Additional tests raise FastAPIError for invalid annotated response models and PydanticV1NotSupportedError for unsupported models passed via response_model, reinforcing coverage. |

**Evidence excerpts**

- `R5.AC1` → `tests/test_response_model_data_filter.py:59-63` (tests/test_response_model_data_filter.py::test_filter_top_level_model)

  ```python
  assert response.json() == {"email": "johndoe@example.com"}
  ```

- `R5.AC1` → `tests/test_response_model_data_filter_no_inheritance.py:61-65` (tests/test_response_model_data_filter_no_inheritance.py::test_filter_top_level_model)

  ```python
  assert response.json() == {"email": "johndoe@example.com"}
  ```

- `R5.AC2` → `tests/test_response_model_data_filter.py:66-71` (tests/test_response_model_data_filter.py::test_filter_second_level_model)

  ```python
  assert response.json() == {
      "name": "Nibbler",
      "owner": {"email": "johndoe@example.com"},
  }
  ```

- `R5.AC2` → `tests/test_response_model_data_filter_no_inheritance.py:68-73` (tests/test_response_model_data_filter_no_inheritance.py::test_filter_second_level_model)

  ```python
  assert response.json() == {
      "name": "Nibbler",
      "owner": {"email": "johndoe@example.com"},
  }
  ```

- `R5.AC2` → `tests/test_response_model_data_filter.py:74-79` (tests/test_response_model_data_filter.py::test_list_of_models)

  ```python
  assert response.json() == [
      {"name": "Nibbler", "owner": {"email": "johndoe@example.com"}},
      {"name": "Zoidberg", "owner": {"email": "johndoe@example.com"}},
  ]
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

- `R5.AC3` → `tests/test_response_model_include_exclude.py:147-153` (tests/test_response_model_include_exclude.py::test_nested_exclude_simple_dict)

  ```python
  assert response.status_code == 200, response.text
  assert response.json() == {
      "baz": "simple_exclude_dict model2 baz",
      "ref": {"foo": "simple_exclude_dict model foo"},
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

- `R5.AC4` → `tests/test_response_model_as_return_annotation.py:499-508` (tests/test_response_model_as_return_annotation.py::test_invalid_response_model_field)

  ```python
  with pytest.raises(FastAPIError) as e:
  
      @app.get("/")
      def read_root() -> Response | None:
          return Response(content="Foo")
  ```

- `R5.AC4` → `tests/test_pydantic_v1_error.py:45-55` (tests/test_pydantic_v1_error.py::test_raises_pydantic_v1_model_in_response_model)

  ```python
  with pytest.raises(PydanticV1NotSupportedError):
  
      @app.get("/response-model", response_model=ResponseModelV1)
      def endpoint():  # pragma: no cover
          return {"name": "test"}
  ```

**Gaps**

- AC3: The cited assertion lines do not directly display the response_model_include/response_model_exclude decorator arguments; parameter usage is inferred from file/test naming and exact filtered JSON expectations, so coverage is slightly less certain than AC1/AC2/AC4.
- AC4: No test verifies the runtime HTTP-500-on-invalid-response-model path (ResponseValidationError at request time is covered, but only via tests about return-annotation mismatch rather than an explicitly invalid response_model at request time).

## Methodology

Coverage is computed per requirement over an explicit acceptance-criteria checklist:
`coverage = 100 * sum(w_a * s_a) / sum(w_a)` where `s_a` is 1.0 for covered, 0.5 for partial, 0.0 for absent. Confidence is the same weighted mean over per-AC confidences, capped at 0.3 when an AC has no accepted evidence.

Retrieval: BM25 + embeddings fused with Reciprocal Rank Fusion (k=60), depth 30 per ranker, top 10 per AC, requirement pool capped at 25.

Evidence gate: every quote is verified as a verbatim substring of the cited line range in a file matching `tests/**/test_*.py`. A failed check downgrades the AC to `absent`; nothing is taken on trust.

## Run metadata

- **run_id**: `run_20261104T104315Z`
- **timestamp**: `2026-11-04T10:43:15.799530+00:00`
- **repo_url**: `https://github.com/fastapi/fastapi.git`
- **commit**: `61ae7934cfd742169f5c3bf7595f8cc1a5849895`
- **validator**: `openai`
- **model**: `glm-5.3`
- **embedding_backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`
- **seed**: `42`
- **files**: `50`
- **tests**: `649`
- **tests_without_asserts**: `0`
- **python**: `3.12.10`
- **packages**: `{'openai': '3.43.0', 'numpy': '2.5.4', 'rank-bm25': '0.2.2', 'pydantic': '2.14.2', 'PyYAML': '6.0.3', 'sentence-transformers': '6.2.0'}`
- **llm_calls**: `5`
