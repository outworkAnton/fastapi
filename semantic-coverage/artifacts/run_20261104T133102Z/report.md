# Coverage Report: Semantic Coverage Analysis

**Run ID**: `run_20261104T133102Z`  
**Repository**: `https://github.com/fastapi/fastapi.git` @ `61ae7934cfd742169f5c3bf7595f8cc1a5849895`  
**Validator**: `openai`  
**Embedding backend**: `st:paraphrase-multilingual-MiniLM-L12-v2`  
**Files in scope**: 50 / tests: 649  
**Overall coverage (unweighted)**: 97.8%  
**Overall coverage (weighted by requirement weight)**: 97.8%

## Summary table

| Requirement ID | Title | Text | Coverage | Tests | Confidence | Evidence |
|---|---|---|---|---|---|---|
| R1 | Валидация тела запроса по Pydantic-модели | Feature: Request body validation | **100%** | `tests/test_multi_body_errors.py::test_put_correct_body`<br>`tests/test_body_alias_choices.py::test_model_body_alias_choice_preserves_nested_errors`<br>`tests/test_body_alias_choices.py::test_embedded_body_requires_an_object`<br>`tests/test_request_params/test_body/test_nullable_and_defaults.py::test_absent_body_for_required_argument` | 0.92 | `tests/test_multi_body_errors.py:25` — `assert response.status_code == 200, response.text     assert response.json() ...` |
| R2 | Dependency Injection: кэширование и teardown | Feature: Dependency injection caching | **89%** | `tests/test_dependency_cache.py::test_sub_counter`<br>`tests/test_dependency_cache.py::test_sub_counter_no_cache`<br>`tests/test_dependency_overrides.py::test_override_with_sub_main_depends_k_bar`<br>`tests/test_dependency_cache.py::test_normal_counter` | 0.81 | `tests/test_dependency_cache.py:64` — `assert response.json() == {"counter": 1, "subcounter": 1}` |
| R3 | HTTP Basic аутентификация | Feature: HTTP Basic authentication | **100%** | `tests/test_security_http_basic_optional.py::test_security_http_basic`<br>`tests/test_security_http_basic_realm.py::test_security_http_basic`<br>`tests/test_security_http_basic_realm_description.py::test_security_http_basic`<br>`tests/test_security_http_basic_optional.py::test_security_http_basic_no_credentials` | 0.96 | `tests/test_security_http_basic_optional.py:23` — `assert response.status_code == 200, response.text     assert response.json() ...` |
| R4 | Обработка ошибок и кастомные exception handlers | Feature: Exception handling | **100%** | `tests/test_exception_handlers.py::test_override_http_exception`<br>`tests/test_exception_handlers.py::test_override_request_validation_exception`<br>`tests/test_exception_handlers.py::test_override_server_error_exception_response`<br>`tests/test_exception_handlers.py::test_traceback_for_dependency_with_yield` | 0.95 | `tests/test_exception_handlers.py:58` — `assert response.status_code == 200     assert response.json() == {"exception"...` |
| R5 | Сериализация ответа по response_model | Feature: Response model filtering | **100%** | `tests/test_response_model_data_filter.py::test_filter_top_level_model`<br>`tests/test_response_model_data_filter_no_inheritance.py::test_filter_top_level_model`<br>`tests/test_response_model_data_filter.py::test_filter_second_level_model`<br>`tests/test_response_model_data_filter_no_inheritance.py::test_filter_second_level_model` | 0.93 | `tests/test_response_model_data_filter.py:59` — `assert response.json() == {"email": "johndoe@example.com"}` |

## Per-requirement detail

### R1: Валидация тела запроса по Pydantic-модели

**Coverage**: 100% (Full)  
**Confidence**: 0.92  
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
| R1.AC1 | 2 | covered | 0.9 | `tests/test_multi_body_errors.py:25-37` | test_put_correct_body sends a correct request body, asserts status_code == 200, and asserts response.json() equals a snapshot containing the submitted item payload (echo). test_model_body_alias_choice_preserves_nested_errors also asserts a 200 with an echoed body-model response as secondary evidence. |
| R1.AC2 | 3 | covered | 0.95 | `tests/test_body_alias_choices.py:134-142` | Multiple tests assert 422 with detail type 'missing' and a loc rooted at 'body' for omitted/empty required body fields (union form normalization, embedded body, absent body for required argument). This satisfies the check: status_code == 422, detail contains missing and loc. \| rejected evidence: tests/test_union_form_normalization.py::test_empty_scalar_is_missing: quote not found verbatim in the cited lines |
| R1.AC3 | 3 | covered | 0.9 | `tests/test_multi_body_errors.py:40-53` | test_jsonable_encoder_requiring_error asserts 422 with detail type 'greater_than' and loc ['body', 0, 'age'], i.e., a value-constraint violation on a request-body Pydantic model. The tests/test_path.py greater_than tests also assert 422/greater_than but on path parameters, so they are not counted as primary body-validation evidence. |
| R1.AC4 | 1 | covered | 0.95 | `tests/test_request_params/test_body/test_required_str.py:35-46` | Multiple schema tests assert app.openapi()['components']['schemas'][model] contains a 'required' list naming the body field (e.g., required: ['p'], ['p_alias'], ['p_val_alias']). test_get_request_body.py::test_openapi_schema also asserts the Product body schema with required: ['name', 'price']. |

**Evidence excerpts**

- `R1.AC1` → `tests/test_multi_body_errors.py:25-37` (tests/test_multi_body_errors.py::test_put_correct_body)

  ```python
  assert response.status_code == 200, response.text
      assert response.json() == snapshot(
          {
              "item": [
  ```

- `R1.AC1` → `tests/test_body_alias_choices.py:196-225` (tests/test_body_alias_choices.py::test_model_body_alias_choice_preserves_nested_errors)

  ```python
  assert response.status_code == 200
      assert response.json() == {"count": 1}
  ```

- `R1.AC2` → `tests/test_body_alias_choices.py:134-142` (tests/test_body_alias_choices.py::test_embedded_body_requires_an_object)

  ```python
  assert response.status_code == 422
      assert [(error["type"], error["loc"]) for error in response.json()["detail"]] == [
          ("missing", ["body", "items"]),
          ("missing", ["body", "first"]),
      ]
  ```

- `R1.AC2` → `tests/test_request_params/test_body/test_nullable_and_defaults.py:133-139` (tests/test_request_params/test_body/test_nullable_and_defaults.py::test_absent_body_for_required_argument)

  ```python
  assert response.status_code == 422
      assert [(error["type"], error["loc"]) for error in response.json()["detail"]] == [
          ("missing", location),
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
  ```

- `R1.AC4` → `tests/test_request_params/test_body/test_required_str.py:35-46` (tests/test_request_params/test_body/test_required_str.py::test_required_str_schema)

  ```python
  assert app.openapi()["components"]["schemas"][body_model_name] == {
          "properties": {
              "p": {"title": "P", "type": "string"},
          },
          "required": ["p"],
  ```

- `R1.AC4` → `tests/test_request_params/test_body/test_list.py:35-50` (tests/test_request_params/test_body/test_list.py::test_required_list_str_schema)

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
  ```

- `R1.AC4` → `tests/test_get_request_body.py:29-114` (tests/test_get_request_body.py::test_openapi_schema)

  ```python
  "Product": {
                          "title": "Product",
                          "required": ["name", "price"],
  ```

### R2: Dependency Injection: кэширование и teardown

**Coverage**: 89% (Good)  
**Confidence**: 0.81  
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
| R2.AC1 | 2 | covered | 0.9 | `tests/test_dependency_cache.py:64-71` | test_sub_counter asserts that on the first request counter == 1 and subcounter == 1 (single call per request via default cache), and on the second request both increment to 2, confirming per-request caching behavior. test_normal_counter provides supplementary evidence for the counter alone. |
| R2.AC2 | 3 | covered | 0.95 | `tests/test_dependency_cache.py:74-81` | test_sub_counter_no_cache asserts exactly the expected values for a non-cached sub-dependency: counter == 2 while subcounter == 1 on the first response, and a diverging pattern (counter 4, subcounter 3) on the second, showing the non-cached dependency is re-invoked. |
| R2.AC3 | 2 | covered | 0.85 | `tests/test_dependency_overrides.py:252-257` | Multiple tests in test_dependency_overrides.py assert 200 responses whose bodies are the overridden dependency's outputs (e.g., 'main-depends', 'router-depends', 'decorator-depends'), demonstrating that dependency_overrides replaces the implementation. The assertion bodies come from the override functions (values not produced by the original dependencies), and status_code == 200 is asserted. The setup lines calling app.dependency_overrides are not shown, so confidence is slightly below full. |
| R2.AC4 | 2 | partial | 0.45 | `tests/test_dependency_yield_scope.py:222-232` | Tests in test_dependency_yield_scope.py demonstrate that code after yield in a dependency executes ('Exception after yield' surfaces in the response detail), which proves the after-yield block runs. However, no test asserts teardown side effects completing AFTER a successful response (e.g., a flag/state recorded post-yield verified after a 200), and no contextmanager-based teardown verification is present. test_app_level_dep_scope_request only asserts a 200 body with no teardown check; test_traceback_for_dependency_with_yield checks traceback frames, not teardown. |

**Evidence excerpts**

- `R2.AC1` → `tests/test_dependency_cache.py:64-71` (tests/test_dependency_cache.py::test_sub_counter)

  ```python
  assert response.json() == {"counter": 1, "subcounter": 1}
  ```

- `R2.AC1` → `tests/test_dependency_cache.py:64-71` (tests/test_dependency_cache.py::test_sub_counter)

  ```python
  assert response.json() == {"counter": 2, "subcounter": 2}
  ```

- `R2.AC1` → `tests/test_dependency_cache.py:54-61` (tests/test_dependency_cache.py::test_normal_counter)

  ```python
  assert response.json() == {"counter": 1}
  ```

- `R2.AC2` → `tests/test_dependency_cache.py:74-81` (tests/test_dependency_cache.py::test_sub_counter_no_cache)

  ```python
  assert response.json() == {"counter": 2, "subcounter": 1}
  ```

- `R2.AC2` → `tests/test_dependency_cache.py:74-81` (tests/test_dependency_cache.py::test_sub_counter_no_cache)

  ```python
  assert response.json() == {"counter": 4, "subcounter": 3}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:252-257` (tests/test_dependency_overrides.py::test_override_with_sub_main_depends_k_bar)

  ```python
  assert response.status_code == 200
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:252-257` (tests/test_dependency_overrides.py::test_override_with_sub_main_depends_k_bar)

  ```python
  assert response.json() == {"in": "main-depends", "params": {"k": "bar"}}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:99-102` (tests/test_dependency_overrides.py::test_decorator_depends_q_foo)

  ```python
  assert response.json() == {"in": "decorator-depends"}
  ```

- `R2.AC3` → `tests/test_dependency_overrides.py:340-345` (tests/test_dependency_overrides.py::test_override_with_sub_router_depends_k_bar)

  ```python
  assert response.json() == {"in": "router-depends", "params": {"k": "bar"}}
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:222-232` (tests/test_dependency_yield_scope.py::test_app_level_dep_scope_function)

  ```python
  assert response.json() == {"detail": "Exception after yield"}
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:209-212` (tests/test_dependency_yield_scope.py::test_router_level_dep_scope_function)

  ```python
  assert response.json() == {"detail": "Exception after yield"}
  ```

- `R2.AC4` → `tests/test_dependency_yield_scope.py:235-245` (tests/test_dependency_yield_scope.py::test_app_level_dep_scope_request)

  ```python
  assert response.json() == {"status": "ok"}
  ```

**Gaps**

- R2.AC4: no test verifies teardown completion after a successful (200) response, e.g., asserting a post-yield flag/list/lock state after the response is received; only error-path execution of after-yield code ('Exception after yield') is exercised.
- R2.AC4: no contextmanager-based teardown verification is present in the candidate tests.
- R2.AC3: only assertion bodies are available; the actual app.dependency_overrides[...] assignment lines are not shown, so coverage of the override mechanism is inferred from test file/name and overridden result values.

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
| R3.AC1 | 3 | covered | 0.97 | `tests/test_security_http_basic_optional.py:23-26` | Three tests send valid Basic credentials and assert status 200 with a JSON body containing username 'john', exactly matching the check (status_code == 200 and username match). |
| R3.AC2 | 2 | covered | 0.95 | `tests/test_security_http_basic_optional.py:29-32` | The optional Basic auth test with no credentials asserts status_code == 200 and the exact fallback message 'Create an account first', matching both keywords of the check. |
| R3.AC3 | 3 | covered | 0.95 | `tests/test_security_http_basic_optional.py:35-41` | Two tests in the non-realm optional Basic file cover both branches of the AC: invalid Basic credentials and a non-Basic Authorization header. Each asserts status 401, WWW-Authenticate header exactly equal to 'Basic', and the 'Not authenticated' detail, matching the check exactly. (The realm variants assert 'Basic realm="simple"', which is a superset but not exact equality; the non-realm tests satisfy the strict check.) |
| R3.AC4 | 1 | covered | 0.95 | `tests/test_security_http_basic_optional.py:53-79` | Three OpenAPI schema snapshot tests assert the full schema including components.securitySchemes.HTTPBasic with type 'http' and scheme 'basic', satisfying the check that the HTTPBasic scheme equals 'basic'. \| rejected evidence: tests/test_security_http_basic_realm_description.py::test_openapi_schema: quote not found verbatim in the cited lines |

**Evidence excerpts**

- `R3.AC1` → `tests/test_security_http_basic_optional.py:23-26` (tests/test_security_http_basic_optional.py::test_security_http_basic)

  ```python
  assert response.status_code == 200, response.text
      assert response.json() == {"username": "john", "password": "secret"}
  ```

- `R3.AC1` → `tests/test_security_http_basic_realm.py:21-24` (tests/test_security_http_basic_realm.py::test_security_http_basic)

  ```python
  assert response.status_code == 200, response.text
      assert response.json() == {"username": "john", "password": "secret"}
  ```

- `R3.AC1` → `tests/test_security_http_basic_realm_description.py:21-24` (tests/test_security_http_basic_realm_description.py::test_security_http_basic)

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
  "components": {
                  "securitySchemes": {"HTTPBasic": {"type": "http", "scheme": "basic"}}
              },
  ```

- `R3.AC4` → `tests/test_security_http_basic_realm.py:52-78` (tests/test_security_http_basic_realm.py::test_openapi_schema)

  ```python
  "components": {
                  "securitySchemes": {"HTTPBasic": {"type": "http", "scheme": "basic"}}
              },
  ```

**Gaps**

- The realm and realm_description variants assert WWW-Authenticate equals 'Basic realm="simple"' rather than bare 'Basic'; only the non-realm optional tests verify the exact header value required by R3.AC3.
- No direct targeted assertion on securitySchemes.HTTPBasic.scheme alone; R3.AC4 is verified only via full-schema snapshot equality, which is still sufficient but less granular.

### R4: Обработка ошибок и кастомные exception handlers

**Coverage**: 100% (Full)  
**Confidence**: 0.95  
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
| R4.AC1 | 2 | covered | 0.98 | `tests/test_exception_handlers.py:58-61` | test_override_http_exception asserts exactly the AC check: response status_code == 200 and JSON body {"exception": "http-exception"} returned by the custom HTTPException handler. |
| R4.AC2 | 2 | covered | 0.98 | `tests/test_exception_handlers.py:64-67` | test_override_request_validation_exception asserts exactly the AC check: status_code == 200 and body exception == request-validation. |
| R4.AC3 | 3 | covered | 0.9 | `tests/test_exception_handlers.py:75-79` | test_override_server_error_exception_response asserts status_code == 500 and body exception == server-error, exactly matching the AC check. The client must be constructed with raise_server_exceptions=False for these assertions to be reachable (the complementary test_override_server_error_exception_raises shows the exception propagates as RuntimeError otherwise), although that client construction is not visible in the provided assertion snippet, so confidence is slightly reduced. |
| R4.AC4 | 1 | covered | 0.95 | `tests/test_exception_handlers.py:82-88` | test_traceback_for_dependency_with_yield asserts that the last traceback frame's lineno equals raise_value_error.__code__.co_firstlineno (the original raise line in the dependency) and that the frame path is the test file containing the dependency, directly satisfying the AC check. |

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

**Gaps**

- AC3: the provided snippet for test_override_server_error_exception_response does not show the TestClient(..., raise_server_exceptions=False) setup; only the outcome assertions (500 + server-error body) are visible, so the 'raise_server_exceptions is False' condition is inferred rather than directly evidenced.

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
| R5.AC1 | 3 | covered | 0.95 | `tests/test_response_model_data_filter.py:59-63` | Top-level stripping is directly verified: the tests assert exact equality of response.json() to an object containing only email, which proves extra fields (e.g. password) are stripped at the top level by response_model. Two independent test files cover this. |
| R5.AC2 | 3 | covered | 0.95 | `tests/test_response_model_data_filter.py:66-71` | Nested-model stripping is verified: the assertions compare response.json() to objects whose nested owner contains only email, confirming extra fields are stripped one level down. Both single-object and list-of-models variants are present in two test files. |
| R5.AC3 | 2 | covered | 0.85 | `tests/test_response_model_include_exclude.py:116-124` | Dedicated include/exclude tests assert the exact filtered JSON: test_nested_include_simple verifies only included fields are present, and test_nested_exclude_simple / test_nested_exclude_simple_dict verify excluded fields are absent. The assertions match the AC keywords (include, exclude, response.json()); the endpoint decorators using response_model_include/response_model_exclude are not shown in the snippets but the file name and exact filtered outputs strongly indicate endpoint-level coverage. |
| R5.AC4 | 1 | covered | 0.95 | `tests/test_response_model_invalid.py:10-16` | A dedicated test asserts that registering a route with an invalid (non-Pydantic) response_model raises FastAPIError at app definition time, exactly matching the AC check (pytest.raises on invalid response model). test_invalid_response_model_field provides additional coverage of a related invalid-response-model error path. |

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

**Gaps**

- AC3: the provided snippets do not show the endpoint definitions using response_model_include/response_model_exclude decorators; coverage is inferred from test names, file name, and exact filtered JSON assertions (confidence slightly reduced).
- AC3: no explicit top-level (non-nested) include/exclude endpoint assertion is present in the snippet list; all shown include/exclude assertions are on nested structures.

## Methodology

Coverage is computed per requirement over an explicit acceptance-criteria checklist:
`coverage = 100 * sum(w_a * s_a) / sum(w_a)` where `s_a` is 1.0 for covered, 0.5 for partial, 0.0 for absent. Confidence is the same weighted mean over per-AC confidences, capped at 0.3 when an AC has no accepted evidence.

Retrieval: BM25 + embeddings fused with Reciprocal Rank Fusion (k=60), depth 30 per ranker, top 10 per AC, requirement pool capped at 25.

Evidence gate: every quote is verified as a verbatim substring of the cited line range in a file matching `tests/**/test_*.py`. A failed check downgrades the AC to `absent`; nothing is taken on trust.

## Run metadata

- **run_id**: `run_20261104T133102Z`
- **timestamp**: `2026-11-04T13:31:02.964299+00:00`
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
