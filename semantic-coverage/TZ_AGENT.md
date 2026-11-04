# ТЗ: Semantic Coverage — сверка бизнес-требований и автотестов

| Поле | Значение |
|---|---|
| Версия | 1.0 |
| Дата | 2026-11-03 |
| Исполнитель | AI-агент (Kilo / deepseek-flash) с человеком-ревьюером |
| Источник требований | `task.md` (тестовое задание) |
| Статус | К исполнению |
| Оценка трудозатрат | 13–17 ч агентского времени + 2–3 ч человеческой разметки |

---

## 0. Как пользоваться этим документом

Документ — исполняемая спецификация, а не описание. Агент выполняет фазы **строго по порядку**, после каждой фазы прогоняет проверку из блока «DoD фазы» и **не переходит дальше при провале**. Все артефакты пишутся в пути, указанные в §5. Любое число, путь или номер строки в итоговых документах обязаны происходить из файлов в `artifacts/run_*/` — см. §14 «Запреты».

Если проверка невозможна (нет ключа, нет сети, нет модели) — **остановиться и сообщить**, а не подставлять правдоподобные значения.

---

## 1. Цель

Спроектировать и продемонстрировать систему **semantic coverage**, которая сопоставляет бизнес-требования с автотестами реального репозитория и выдаёт:

- карту `требование → тесты`;
- оценку покрытия 0–100% с явной формулой;
- confidence;
- **программно проверяемые доказательства** (файл + строки + дословная цитата).

Демонстрация выполняется на реальном публичном репозитории, реальным прогоном, с воспроизводимым результатом.

---

## 2. Зафиксированные решения (decision log)

| № | Решение | Значение | Обоснование |
|---|---|---|---|
| D1 | Базовый репозиторий | **`fastapi/fastapi`** | Python-стек совпадает с прототипом; тесты pytest парсятся через `ast` надёжнее regex; высокая узнаваемость на защите |
| D2 | Публикация демо | **Fork FastAPI + папка `semantic-coverage/` в ветке `semantic-coverage-demo`** | Формально «свой GitHub-проект», лицензия MIT сохраняется, история и авторство не теряются |
| D3 | Формат требований | **Gherkin + чек-лист AC с ID и весами** | Gherkin читается комиссией, AC даёт проверяемую единицу скоринга |
| D4 | Модель скоринга | **Взвешенный чек-лист AC**, непрерывные 0–100 | Устраняет субъективность шкалы 0/25/50/75/100 |
| D5 | Пайплайн | **Hybrid (BM25 + multilingual embeddings) → RRF → LLM-валидация** | RRF устойчив к разным шкалам score/distance; LLM нужен только для финального суждения |
| D6 | LLM | **DeepSeek V4 Flash**, OpenAI-совместимый клиент, модель задаётся `LLM_MODEL` (по умолчанию `deepseek/deepseek-flash`) | Выбор заказчика; провайдер-агностичный клиент позволяет заменить модель без правок кода |
| D7 | Эмбеддинги | **`sentence-transformers` + `paraphrase-multilingual-MiniLM-L12-v2`**, косинус, in-memory numpy | Требования на русском, тесты на английском — нужна кросс-языковая модель. Отказ от chromadb убирает скрытую загрузку англоязычной ONNX-модели и лишний слой |
| D8 | Объём | **≤50 тестовых файлов, 5 требований** | Ровно по ТЗ; в выборку входят 10 контрольных файлов из других доменов для измерения ложных срабатываний |
| D9 | Gold set | **25 пар (15 позитивных, 10 негативных)**, ручная разметка по mutation-критерию | Позволяет измерить Precision@5, Recall@10, устойчивость |
| D10 | Прототип | **Рабочий CLI + реальный прогон + кэш + seed** | Отчёт генерируется из результата, а не пишется вручную |
| D11 | Язык | **Русский** для всех документов; код, имена и логи — английский | Соответствие языку задания |
| D12 | Упаковка | **4 отдельных deliverable-файла + `README.md`-навигатор** | Прямое соответствие ожидаемым артефактам |

---

## 3. Границы работ

**Входит в объём:**
- выбор и фиксация ≤50 тестовых файлов FastAPI;
- 5 требований с AC (RU + EN-термины) и весами;
- парсер pytest-тестов, индексация, гибридный поиск, RRF;
- LLM-валидация с программной проверкой цитат;
- скоринг по формуле, генерация отчёта;
- gold set и метрики качества;
- 4 обязательных документа + README + лог использования AI;
- публикация fork-ветки.

**Не входит:**
- запуск самих тестов FastAPI и покрытие строк (code coverage);
- mutation testing как исполняемый инструмент (используется только как критерий разметки);
- поддержка других языков/фреймворков;
- UI/dashboard;
- CI-интеграция (описывается как план, не реализуется).

---

## 4. Предусловия и окружение

### 4.1. Инструменты

- Python **3.11+**, `venv`
- Git, GitHub CLI `gh` (опционально, но желательно)
- PowerShell 7+
- Доступ к LLM API (ключ) и к интернету для первой загрузки модели эмбеддингов

### 4.2. Переменные окружения (`.env`, в git не коммитить)

```dotenv
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=<key>
LLM_MODEL=deepseek/deepseek-flash
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
REPO_DIR=.repos/fastapi
SEED=42
```

### 4.3. Зависимости (`requirements.txt` — заменить текущий)

```text
openai>=1.40
sentence-transformers>=3.0
numpy>=1.26
rank-bm25>=0.2.2
snowballstemmer>=2.2
pydantic>=2.7
PyYAML>=6.0
python-dotenv>=1.0
pytest>=8.0
```

Удаляются: `jieba`, `chromadb`, `pathlib`, `dataclasses-json`, `tree-sitter*` — не используются либо вредны (см. §15).

### 4.4. Проверка окружения (выполнить до начала работ)

```powershell
python --version
python -c "import openai, sentence_transformers, numpy, rank_bm25, snowballstemmer, pydantic, yaml; print('ok')"
python -c "import os; from openai import OpenAI; c=OpenAI(base_url=os.environ['LLM_BASE_URL'], api_key=os.environ['LLM_API_KEY']); print([m.id for m in c.models.list()][:5])"
```

**Стоп-условие:** если список моделей не содержит `LLM_MODEL` — зафиксировать фактический id в `.env` и в `run_meta.json`, не продолжать с догадкой.

---

## 5. Целевая структура

```
AI-Based-Test/
├── TZ_AGENT.md                  # этот документ
├── README.md                    # навигатор + how to run + snapshot результатов
├── solution_brief.md            # deliverable 1
├── coverage_report.md           # deliverable 2 (сгенерирован, затем отревьюен)
├── risk_robustness.md           # deliverable 3
├── demo_summary.md              # deliverable 4
├── AI_USAGE_LOG.md              # как использовался AI, что отвергнуто
├── requirements.txt
├── .env.example
├── .gitignore
├── drafts/                      # архив старых черновиков, НЕ оценивается
│   ├── execution_plan.md
│   ├── coverage_report.draft.md
│   ├── demo_summary.draft.md
│   ├── risk_robustness.draft.md
│   ├── semantic_coverage.py
│   └── requirements.draft.txt
├── demo/
│   ├── requirements.yaml
│   ├── file_manifest.csv
│   ├── gold_set.csv
│   ├── src/
│   │   ├── cli.py               # ingest | retrieve | validate | report | verify
│   │   ├── config.py
│   │   ├── models.py            # pydantic-схемы
│   │   ├── ingest.py            # AST-парсер pytest
│   │   ├── index.py             # BM25 + embeddings + кэш
│   │   ├── retrieve.py          # RRF, сбор пула
│   │   ├── validate.py          # LLM + evidence gate
│   │   ├── score.py             # формулы §10
│   │   ├── report.py            # md/json
│   │   └── verify.py            # самопроверка §13
│   └── tests/
│       ├── test_parser.py
│       ├── test_rrf.py
│       ├── test_scoring.py
│       └── test_evidence_gate.py
├── artifacts/
│   └── run_<UTC>/
│       ├── run_meta.json
│       ├── tests.jsonl
│       ├── retrieval_debug.json
│       ├── llm_raw/<req_id>.json
│       ├── report.json
│       ├── report.md
│       └── metrics.json
├── .cache/                      # gitignored
└── .repos/fastapi/              # gitignored клон зафиксированного коммита
```

---

## 6. Артефакты и критерии приёмки

| # | Артефакт | Обязателен | Критерий приёмки |
|---|---|---|---|
| A1 | `solution_brief.md` | да | 1–3 страницы: проблема, архитектура (схема потока данных), почему жизнеспособно, компромиссы, границы применимости |
| A2 | `coverage_report.md` | да | Таблица с колонками: Requirement ID / название / текст, Coverage score, Список тестов, Confidence, Evidence. Плюс разбивка по AC и приложение с цитатами |
| A3 | `risk_robustness.md` | да | ≥6 рисков: причина → механизм контроля → **как реализовано в коде** (ссылка на модуль) → как измеряется |
| A4 | `demo_summary.md` | да | Что покрыто/не покрыто, топ-3 разрыва, выводы для команды, ссылка на run id |
| A5 | `README.md` | да | Навигация по файлам, команды запуска, snapshot ключевых цифр, ссылка на fork-ветку |
| A6 | Прототип `demo/` | да (звёздочка) | `python -m demo.cli verify` → exit 0; `pytest demo/tests` → зелёный |
| A7 | `AI_USAGE_LOG.md` | да | Где применён AI, какие промпты/итерации, какие выходы отвергнуты и почему |
| A8 | `demo/file_manifest.csv` | да | ≤50 строк `in_scope=1`, все пути существуют на зафиксированном коммите |
| A9 | `demo/requirements.yaml` | да | 5 требований, ≥15 AC, валидно по схеме §7 |
| A10 | `demo/gold_set.csv` | да | ≥20 пар, бинарная разметка, рубрика в шапке файла |
| A11 | `artifacts/run_*/` | да | Полный набор из §5, `run_meta.json` содержит commit, модель, seed |
| A12 | Fork-ветка | да | Публичная ссылка, папка `semantic-coverage/` с A1–A7 |

---

## 7. Модель требований

### 7.1. Схема `demo/requirements.yaml`

```yaml
schema_version: 1
language: ru
requirements:
  - id: R1
    title: "Валидация тела запроса по Pydantic-модели"
    weight: 3                  # 3 critical | 2 important | 1 normal
    gherkin: |
      Feature: Валидация тела запроса
        Scenario: Валидное тело
          Given приложение с POST /items и моделью Item(name: str, price: float)
          When клиент отправляет {"name": "x", "price": 1.5}
          Then ответ 200 и тело совпадает с отправленным
        Scenario: Невалидное тело
          Given приложение с POST /items и моделью Item(name: str, price: float)
          When клиент отправляет {"price": "not-a-number"}
          Then ответ 422 и в detail указан loc ["body", "price"]
    acceptance_criteria:
      - id: R1.AC1
        text_ru: "Валидное тело возвращает 200 и эхо-ответ"
        text_en: "valid request body returns 200 and echoes payload"
        weight: 2
        check: "status_code == 200 and response.json() == payload"
      - id: R1.AC2
        text_ru: "Отсутствие обязательного поля возвращает 422"
        text_en: "missing required field returns 422 validation error"
        weight: 3
        check: "status_code == 422 and loc mentions missing field"
      - id: R1.AC3
        text_ru: "Неверный тип поля возвращает 422 с указанием поля"
        text_en: "wrong field type returns 422 with field location"
        weight: 3
        check: "status_code == 422 and 'price' in str(detail)"
```

### 7.2. Обязательные свойства AC

1. Каждый AC **бинарно проверяем**: можно ответить «покрыт / не покрыт» без интерпретации.
2. Каждый AC описывает **наблюдаемое поведение** (status code, поле ответа, побочный эффект), а не реализацию.
3. `text_en` обязателен: BM25 работает по английским терминам, тесты FastAPI англоязычные — кросс-языковой разрыв закрывается явно, а не замалчивается.
4. Веса: `3` — критично для бизнеса, `2` — важно, `1` — желательно.
5. Минимум 3 AC на требование, итого ≥15.

### 7.3. Предлагаемый набор требований (проверить на наличие тестов в репозитории)

| ID | Требование | Домен FastAPI | Ожидаемые тестовые файлы (glob) |
|---|---|---|---|
| R1 | Валидация тела по Pydantic: 200 / 422 / локация ошибки | request body | `tests/test_body*.py`, `tests/test_json_body*.py` |
| R2 | Dependency Injection: параметры, `use_cache`, teardown | dependencies | `tests/test_dependency*.py` |
| R3 | HTTP Basic auth: 401 без/с неверными кредами, 200 с валидными | security | `tests/test_security_http_basic*.py` |
| R4 | Обработка ошибок: `HTTPException`, кастомный `exception_handler` | error handling | `tests/test_handlers*.py`, `tests/test_exception*.py` |
| R5 | `response_model`: фильтрация полей, `exclude_unset`/`exclude_none` | response serialization | `tests/test_response_model*.py` |

**Правило:** если для AC не находится ни одного кандидата — это **легитимный разрыв**, он попадает в отчёт как 0% и в `gaps`. Требование не переписывается под найденные тесты.

---

## 8. Отбор файлов (≤50)

### 8.1. Алгоритм

1. Зафиксировать коммит: `git -C .repos/fastapi rev-parse HEAD` → в `run_meta.json`.
2. Собрать кандидатов по glob-паттернам §7.3.
3. Отсортировать по числу тестовых функций (убывание), обрезать до **40** файлов.
4. Добавить **10 контрольных** файлов из доменов, не связанных с R1–R5 (например `tests/test_tutorial*`, `tests/test_ws_router*`), — они нужны для проверки ложных срабатываний.
5. Записать `demo/file_manifest.csv`.

### 8.2. Формат манифеста

```csv
path,tests_count,domain,selected_reason,in_scope
tests/test_body_fields.py,12,R1,"matches test_body*.py glob, high test density",1
tests/test_ws_router.py,8,control,"negative control, unrelated domain",1
```

### 8.3. DoD фазы отбора

- строк с `in_scope=1` ≤ 50;
- каждый `path` существует на зафиксированном коммите (`Test-Path`);
- в манифесте есть ≥8 контрольных файлов;
- в `README.md` зафиксировано: «учтено N файлов из M в репозитории».

---

## 9. Пайплайн

```
requirements.yaml
      │  (AC: text_ru + text_en + weight)
      ▼
[1] INGEST      AST-парсер pytest → tests.jsonl
      │         (id, file, line_start, line_end, name, docstring, asserts[], signals)
      ▼
[2] INDEX       BM25(tokens_en) + embeddings(multilingual) → кэш
      │
      ▼
[3] RETRIEVE    по каждому AC: BM25 top-N + vector top-N → RRF → top-K
      │         пул требования = union по AC, cap 25
      ▼
[4] VALIDATE    LLM: AC × пул → status + confidence + evidence
      │         ▸ evidence gate: цитата обязана дословно совпасть с файлом
      ▼
[5] SCORE       формула §10 → coverage, confidence, grade
      │
      ▼
[6] REPORT      report.json + report.md (+ метрики §12)
```

### 9.1. Ingest (AST, не regex)

Для каждого файла `tests/**/test_*.py`:

- `ast.parse`; обойти `FunctionDef` с именем `test_*` (включая методы классов);
- `test_id = "<relpath>::<qualname>"`;
- `line_start` = `node.lineno`, `line_end` = `node.end_lineno`;
- `name` = имя функции, разбитое по `_`;
- `docstring` — если есть;
- `asserts` — исходники всех `ast.Assert` через `ast.get_source_segment` (не более 10, каждый ≤200 символов);
- `signals` — эвристики: HTTP-метод и путь из `client.<method>("...")`, `status_code == N`, ключи `response.json()`, имена фикстур;
- `search_text` = `name_words + docstring + asserts + signals`.

Отбрасывать функции без единого `assert` — но **считать их отдельно** (`tests_without_asserts`) и вывести в метрики: это индикатор фиктивного покрытия.

### 9.2. Index

- BM25: токенизация `[a-z0-9_]+`, lowercase, стоп-слова EN, стемминг `snowballstemmer` (english). Индексируется `search_text`.
- Эмбеддинги: `paraphrase-multilingual-MiniLM-L12-v2`, L2-нормализация, матрица `float32` в памяти, косинус = скалярное произведение.
- Кэш: `.cache/emb/<sha256(model+text)>.npy`; `.cache/bm25/<sha256(corpus)>.pkl`.
- **Никакой сети после первой загрузки модели.** Если модель не скачалась — стоп, не деградировать молча.

### 9.3. Retrieve + RRF

Для каждого AC отдельно:

```
rank_bm25   = top 20 по BM25 (запрос: text_en + signals)
rank_vector = top 20 по косинусу (запрос: text_ru + " " + text_en)

RRF(d) = Σ_r 1 / (60 + rank_r(d))        # r ∈ {bm25, vector}, k=60
```

- top-K = 10 на AC; пул требования — union, cap 25, порядок по сумме RRF.
- В `retrieval_debug.json` писать для каждого AC: запросы, top-10 из каждого ранкера, итоговый RRF-список. Это основа для защиты «почему нашёлся этот тест».

**Запрещено** смешивать `score` BM25 и `distance` эмбеддингов напрямую (это была ошибка черновика). Только RRF по рангам.

### 9.4. Validate (LLM)

Один вызов на требование: все AC + пул (компактно: `test_id`, имя, docstring ≤120 симв., до 5 asserts, `file:line_start-line_end`).

**Контракт ответа (JSON, strict):**

```json
{
  "requirement_id": "R1",
  "acs": [
    {
      "ac_id": "R1.AC2",
      "status": "covered",
      "confidence": 0.88,
      "reasoning": "тест проверяет 422 и loc содержит отсутствующее поле",
      "evidence": [
        {"test_id": "tests/test_body_fields.py::test_missing_field",
         "file": "tests/test_body_fields.py",
         "line_start": 41, "line_end": 44,
         "quote": "assert response.status_code == 422"}
      ]
    }
  ],
  "gaps": ["..."],
  "notes": "..."
}
```

Валидация ответа (Pydantic, `demo/src/models.py`):

- `status ∈ {covered, partial, absent}`;
- `0 ≤ confidence ≤ 1`;
- `evidence` обязателен для `covered`/`partial`, для `absent` — пустой;
- `test_id` обязан присутствовать в пуле;
- `file` обязан совпадать с файлом из `test_id`;
- `line_start ≤ line_end`, обе строки в пределах файла.

**Retry:** до 3 попыток. При ошибке схемы — repair-промпт с текстом ошибки. После 3 неудач: требование помечается `unverified`, `coverage = null`, попадает в раздел «требует ручной проверки». **Оценка не выдумывается.**

Параметры: `temperature=0`, `top_p=1`, `seed=SEED` (если провайдер поддерживает — иначе зафиксировать `capabilities.seed=false` в `run_meta.json` и не утверждать обратное).

### 9.5. Evidence gate (ключевой механизм доверия)

После получения ответа, **до** скоринга, для каждого evidence:

```python
window = "\n".join(read_lines(file)[line_start-1:line_end])
ok = normalize(quote) in normalize(window)          # normalize: схлопнуть пробелы, strip
```

Дополнительно:
- `file` обязан матчить `tests/**/test_*.py` — production-файлы отклоняются (это была ошибка черновика: `create-cart.ts`);
- `line_start/line_end` обязаны попадать в диапазон функции теста из `tests.jsonl`;
- предупреждение, если в окне нет `assert` (в метрики как `evidence_without_assert`).

**Если все evidence для `covered`/`partial` отклонены** → статус понижается до `absent`, `confidence ≤ 0.3`, в `gaps` пишется `evidence_unverified`. Молчаливое доверие к LLM запрещено.

---

## 10. Скоринг

Обозначения: `A(R)` — множество AC требования R; `w_a` — вес AC; `s_a` — статус.

```
s_a = 1.0  (covered)
s_a = 0.5  (partial)
s_a = 0.0  (absent)

coverage(R) = 100 * Σ w_a·s_a / Σ w_a          → округление до целого
```

Градации (производные, не источник истины):

| coverage | grade |
|---|---|
| 90–100 | Full |
| 70–89 | Good |
| 40–69 | Partial |
| 1–39 | Weak |
| 0 | None |
| null | Unverified |

```
confidence(R) = Σ w_a·c_a / Σ w_a              → 2 знака
c_a = conf из LLM; если evidence отклонён → c_a = min(c_a, 0.3)
```

Агрегаты по проекту — **обе метрики, с явными подписями**:

```
overall_unweighted = mean(coverage(R))
overall_weighted   = 100 * Σ W_R·coverage(R) / Σ W_R,  W_R = Σ_{a∈A(R)} w_a
```

Требования с `unverified` исключаются из агрегатов и перечисляются отдельно. В отчёте обязательна строка с формулой и входными данными — чтобы число можно было пересчитать вручную.

---

## 11. Отчёт

### 11.1. Обязательная таблица (`coverage_report.md`)

| Requirement ID | Название | Текст (кратко) | Coverage | Tests | Confidence | Evidence |
|---|---|---|---|---|---|---|

`Tests` — список `test_id` с ссылкой `file:line`. `Evidence` — 1–2 дословные цитаты с `file:line_start-line_end`.

### 11.2. Разбивка по AC (обязательна)

Для каждого требования — таблица `AC | weight | status | confidence | evidence | reasoning`. Без неё score невоспроизводим.

### 11.3. Раздел разрывов

Для каждого `absent`/`partial`: чего не хватает, какой AC не покрыт, какой тест было бы достаточно добавить (1–2 предложения).

### 11.4. Приложение A: методология

Формулы §10, RU/EN-обработка, RRF, evidence gate, ограничения.

### 11.5. Приложение B: run metadata

`run_id`, commit SHA, модель, embedding-модель, seed, дата, число файлов/тестов, cache hit rate.

---

## 12. Gold set и метрики

### 12.1. Разметка

Файл `demo/gold_set.csv`:

```csv
ac_id,test_id,relevant,rationale
R1.AC2,tests/test_body_fields.py::test_missing_field,1,"упадёт при поломке валидации обязательного поля"
R1.AC2,tests/test_ws_router.py::test_websocket,0,"другой домен"
```

**Рубрика (в шапке файла):** пара релевантна (`relevant=1`), если при внесении дефекта в поведение, описанное AC, этот тест упадёт. Это mutation-критерий, а не «похожесть формулировок».

Состав: 15 позитивных, 10 негативных (негативные — из контрольных файлов и из соседних AC). Всего 25.

### 12.2. Метрики (в `artifacts/run_*/metrics.json`)

```
P@5      = mean_R ( |relevant ∩ top5(R)| / min(5, |top5(R)|) )
Recall@10= mean_R ( |relevant ∩ top10(R)| / |relevant(R)| )
CoverageMAE = mean_R |coverage_system(R) − coverage_human(R)|   # по gold set
Jaccard  = |∩ matched за 3 прогона| / |∪ matched за 3 прогона|
EvidenceValidity = accepted / total evidence
```

Цели: `P@5 ≥ 0.80`, `Recall@10 ≥ 0.80`, `CoverageMAE ≤ 15 п.п.`, `Jaccard ≥ 0.90`, `EvidenceValidity = 1.00`.

Если цель не достигнута — **так и написать** в `risk_robustness.md` и `demo_summary.md`, с числом и гипотезой причины. Подгонять разметку под результат запрещено.

### 12.3. Воспроизводимость

- 3 прогона `validate` на одном коммите и модели;
- сравнение matched-множеств и coverage;
- `run_meta.json` для каждого прогона;
- расхождение >5 п.п. по coverage — отдельный пункт в отчёте.

---

## 13. Самопроверка (`python -m demo.cli verify`)

Команда обязана проверить и вернуть exit 0 только при полном прохождении:

1. Все evidence проходят quote-check.
2. Все `test_id` указывают на `tests/**/test_*.py` и существуют в `tests.jsonl`.
3. Каждый coverage имеет входные данные (веса + статусы) в `report.json`.
4. В отчёте ровно 5 требований; у каждого ≥3 AC.
5. `file_manifest.csv` ≤50 `in_scope=1`, все пути существуют на зафиксированном коммите.
6. `gold_set.csv` ≥20 пар, обе метки присутствуют.
7. `run_meta.json` содержит commit, модель, embedding-модель, seed.
8. Нет чисел в `coverage_report.md`, отсутствующих в `report.json` (regex-сверка score-колонки).
9. Нет production-файлов в `matched_tests`.

Провал любого пункта → печать конкретного нарушения со ссылкой на файл/строку.

---

## 14. Запреты (нарушение = провал задания)

1. **Никаких цифр, путей и номеров строк, не полученных из прогона.** В документах допускаются только значения из `artifacts/run_*`; ручные экспертные оценки помечаются явно как `manual`.
2. **Не выдавать production-файл за тест.** Валидируется путём.
3. **Не ставить `covered` без evidence**, прошедшего quote-check.
4. **Не переписывать требования после прогона**, чтобы поднять score.
5. **Не подгонять gold set** под результат системы.
6. **Не утверждать детерминизм**, если провайдер не поддерживает `seed`; писать фактическое состояние в `run_meta.json`.
7. **Не коммитить** `.env`, `.cache/`, `.repos/`, ключи.
8. **Не оставлять `unverified` тихо** — только явным разделом отчёта.

---

## 15. Реестр исправлений предыдущих черновиков

| Находка аудита | Действие в этом ТЗ |
|---|---|
| Нет `solution_brief.md` и `requirements_gherkin.md` | Создать A1 и A9 (`demo/requirements.yaml`), ссылки в документах только на существующие пути |
| Отчёты вымышлены, прогона не было | Запрет §14.1; обязательный `artifacts/run_*`; `verify` сверяет числа |
| Production-файл в matched_tests | Evidence gate §9.5 + проверка §13.2 |
| Шкала покрытия субъективна | Взвешенный чек-лист AC §10, непрерывный score |
| «80%» — невзвешенное среднее порядковых | Два агрегата с явными формулами §10 |
| «4 теста» при 3 уникальных файлах | `test_id` уникален; счётчик = `len(set(test_id))` |
| 250 LLM-вызовов vs $0.15 vs 5 вызовов | Один вызов на требование §9.4; стоимость считать по факту токенов из `run_meta.json` |
| GPT-4 в тексте, gpt-4o-mini в коде | Модель только из `LLM_MODEL`, фактический id в `run_meta.json` |
| Митигации описаны, не реализованы | Каждый риск в A3 обязан ссылаться на модуль реализации |
| Distance/similarity смешаны, вектор инвертирован | Только RRF по рангам §9.3 |
| Glob не покрывает `.spec.ts` / `__tests__` | Переход на FastAPI + AST-парсер §9.1 |
| Обрезка кода 500 символов ломает цитаты | Полные диапазоны строк из AST + quote-check §9.5 |
| `gaps` может быть строкой | Pydantic-схема §9.4 |
| Мусорные зависимости | `requirements.txt` §4.3 |
| Китайский фрагмент, «сценарие» | Вычитка; документы перезаписываются с нуля |
| Нет «своего GitHub-проекта» | D2, A12 |
| Не показан лимит ≤50 файлов | Манифест §8 |

---

## 16. Порядок выполнения (фазы)

### Фаза 0. Подготовка (0.5 ч)
1. Создать `.env` из `.env.example`, проверить §4.4.
2. Переместить черновики в `drafts/`: `execution_plan.md`, `semantic_coverage.py`, `coverage_report.md` → `coverage_report.draft.md`, `demo_summary.md` → `demo_summary.draft.md`, `risk_robustness.md` → `risk_robustness.draft.md`, `requirements.txt` → `requirements.draft.txt`. `First_sight.md` — в `drafts/` (личный разбор, не deliverable).
3. Создать `.gitignore`: `.env`, `.cache/`, `.repos/`, `__pycache__/`, `*.pyc`.
4. `gh repo fork fastapi/fastapi --clone` → `.repos/fastapi`; `git checkout -b semantic-coverage-demo`; зафиксировать SHA.

**DoD:** `.env` валиден, модель отвечает, `drafts/` заполнен, SHA записан.

### Фаза 1. Манифест файлов (1–1.5 ч)
§8. Записать `demo/file_manifest.csv`.

**DoD:** ≤50 in-scope, все пути существуют, ≥8 контрольных.

### Фаза 2. Требования (1.5–2 ч)
§7. Записать `demo/requirements.yaml` (5 требований, ≥15 AC, RU+EN, веса).

**DoD:** валидация по Pydantic-схеме проходит; каждый AC бинарно проверяем.

### Фаза 3. Ingest + Index (2–3 ч)
§9.1–9.2. Реализовать `ingest.py`, `index.py`, `cli.py`.

**DoD:** `python -m demo.cli ingest` создаёт `tests.jsonl`; 0 ошибок парсинга; `tests_without_asserts` посчитан; `pytest demo/tests/test_parser.py` зелёный.

### Фаза 4. Retrieve + RRF (1.5–2 ч)
§9.3.

**DoD:** для каждого AC пул ≤25; `retrieval_debug.json` записан; `test_rrf.py` зелёный (проверка, что RRF инвариантен к масштабу score).

### Фаза 5. Validate + Evidence gate (2–3 ч)
§9.4–9.5.

**DoD:** 5 вызовов (плюс retry) успешны; `EvidenceValidity = 1.00`; при искусственно испорченной цитате тест `test_evidence_gate.py` подтверждает отклонение.

### Фаза 6. Score + Report + Метрики (1.5–2 ч)
§10–12. Разметить gold set **до** просмотра результата системы.

**DoD:** `report.json`/`report.md`/`metrics.json` созданы; метрики посчитаны; 3 прогона для Jaccard.

### Фаза 7. Документы (2 ч)
A1–A5, A7. Все числа — из `artifacts/`.

**DoD:** 4 deliverable + README + AI_USAGE_LOG; в каждом числе — ссылка на run id.

### Фаза 8. Публикация и защита (1 ч)
1. Скопировать `TZ_AGENT.md`, A1–A7, `demo/`, `artifacts/run_*` в fork: `semantic-coverage/`.
2. Commit + push ветки `semantic-coverage-demo`.
3. В `README.md` — ссылка на ветку.
4. Пробежать чек-лист §18 и подготовить ответы §19.

**DoD:** ссылка открывается, структура совпадает, `verify` в форке проходит.

---

## 17. Definition of Done (всего задания)

- [ ] 5 требований, ≥15 AC, RU+EN, веса — `requirements.yaml`
- [ ] ≤50 файлов, манифест с обоснованием и контролем
- [ ] Прототип запускается с нуля по README на чистой машине
- [ ] `verify` → exit 0, `pytest demo/tests` → зелёный
- [ ] Все evidence проходят quote-check (100%)
- [ ] Метрики посчитаны, цели либо достигнуты, либо честно описаны
- [ ] 4 deliverable + README + AI_USAGE_LOG
- [ ] Нет ни одного числа без источника в `artifacts/`
- [ ] Публичная fork-ветка со ссылкой
- [ ] Готовы ответы на 10 вопросов защиты

---

## 18. Маппинг на критерии оценки задания

| Критерий задания | Где закрывается |
|---|---|
| Качество ресерч-подхода | D1/D5/D7 с обоснованием, сравнение альтернатив в `solution_brief.md` §2, `AI_USAGE_LOG.md` |
| Ясность архитектуры | §9 (поток данных), схема в A1, контракты в `demo/src/models.py` |
| Объяснимость и доказательность | Evidence gate §9.5, приложение с цитатами §11.2, `retrieval_debug.json` |
| Устойчивость и контроль неопределённости | §12 метрики, `unverified`-статус, `run_meta.json`, 3 прогона |
| Прагматичность | Фазы 0–8, MVP за 13–17 ч, отказ от chromadb/reranker |
| Качество коммуникации и защиты | A1–A5, README, §19 |

---

## 19. Подготовка к защите (тезисы)

1. **Почему гибрид, а не чистый LLM?** Стоимость и воспроизводимость: LLM видит 25 кандидатов вместо 2000 тестов; поиск детерминирован и кэшируем.
2. **Почему RRF, а не взвешенная сумма score?** BM25 неограничен, косинус в [0,1] — суммы несопоставимы; RRF работает только с рангами и не требует калибровки.
3. **Как гарантируете, что evidence не выдуман?** Цитата проверяется как подстрока реального окна файла; при провале статус понижается, а не «исправляется».
4. **Где система ошибается?** Кросс-языковой матчинг (RU-требование ↔ EN-тест), тесты без assert, «формально релевантные» тесты без проверки нужного поля.
5. **Почему score не 100%, если тест есть?** Покрытие считается по AC, а не по факту наличия похожего теста.
6. **Как измерили качество?** Gold set 25 пар по mutation-критерию, P@5, Recall@10, CoverageMAE, Jaccard.
7. **Что будет при смене модели?** Кэш инвалидируется по `model`, прогон повторяется, agreement между моделями фиксируется числом.
8. **Как масштабировать на 10 000 тестов?** Инкрементальный ingest по `git diff`, кластеризация по доменам, ANN-индекс, batch-валидация, кэш.
9. **Почему не mutation testing?** Дорого по времени; используем как критерий разметки и как направление развития.
10. **Что бы сделали иначе с ещё одной неделей?** Fine-tune эмбеддингов на 200 размеченных парах, CI-гейт, active learning на низком confidence.

---

## 20. Шпаргалка команд

```powershell
# окружение
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# пайплайн
python -m demo.cli ingest   --manifest demo/file_manifest.csv --repo .repos/fastapi
python -m demo.cli retrieve --requirements demo/requirements.yaml
python -m demo.cli validate --requirements demo/requirements.yaml
python -m demo.cli report   --out artifacts/run_$(Get-Date -Format yyyyMMddTHHmmssZ)
python -m demo.cli verify   --run artifacts/run_<id>

# проверки
pytest demo/tests -q
git -C .repos/fastapi rev-parse HEAD
```

---

## 21. Стоп-условия

Остановиться и доложить, если:

- LLM-модель недоступна или `LLM_MODEL` не найден у провайдера;
- модель эмбеддингов не скачивается;
- после 3 retry схема ответа не валидна для ≥2 требований;
- `verify` падает по пункту, который нельзя исправить без изменения требований или gold set;
- обнаружено, что часть AC невозможно проверить по коду тестов (тогда — зафиксировать как разрыв, не «дорисовывать»).

**Во всех случаях результат оформляется как есть, с указанием, что именно не удалось.**
