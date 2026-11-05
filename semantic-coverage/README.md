# Semantic Coverage — сверка требований и автотестов

Инструмент сопоставляет бизнес-требования с автотестами и выдаёт оценку покрытия, которую можно проверить: у каждого вывода есть `файл:строка` и дословная цитата, прошедшая машинную проверку.

Демонстрация выполнена на `fastapi/fastapi` @ `5cb6272ed7e3e07eaf6978e1e65b94aca76fa8e0`.

---

## Статус

| | |
|---|---|
| Пайплайн | работает, `verify` — 10/10 PASS |
| Режим валидации | LLM `glm-5.3` через OpenAI-совместимый API (5 вызовов, temperature=0, seed=42) |
| Прогон | `artifacts/run_20261104T133102Z` |
| Тесты | `pytest demo/tests` — 11 passed |
| Публикация форка | **выполнена**: [`outworkAnton/fastapi`, ветка `semantic-coverage-demo`](https://github.com/outworkAnton/fastapi/tree/semantic-coverage-demo) |

---

## Артефакты

| Файл | Назначение |
|---|---|
| [`solution_brief.md`](solution_brief.md) | Архитектура, обоснование, компромиссы, границы |
| [`tz_compliance.md`](tz_compliance.md) | Матрица соответствия `TZ_AGENT.md`: артефакты, решения, пайплайн, метрики |
| [`coverage_report.md`](coverage_report.md) | Отчёт по покрытию (сгенерирован из прогона) |
| [`risk_robustness.md`](risk_robustness.md) | Риски, реализованные контроли, измерения |
| [`demo_summary.md`](demo_summary.md) | Итоги демонстрации и рекомендации |
| [`AI_USAGE_LOG.md`](AI_USAGE_LOG.md) | Как применялся AI и что было отвергнуто |
| [`TZ_AGENT.md`](TZ_AGENT.md) | Исходное ТЗ на исполнение |
| `artifacts/run_*/` | Сырые данные прогона: `tests.jsonl`, пулы, ответы, отчёты, метрики |

---

## Структура

```
demo/
├── requirements.yaml      # 5 требований, 20 AC (RU + EN-термины + веса)
├── file_manifest.csv      # 50 файлов: 40 целевых + 10 контрольных
├── gold_set.csv           # 35 размеченных пар для метрик
├── tools/build_manifest.py
├── src/
│   ├── ingest.py          # AST-парсер pytest
│   ├── index.py           # BM25, эмбеддинги, хэширующий fallback
│   ├── retrieve.py        # три ранкера + RRF
│   ├── validate.py        # offline / openai + evidence gate
│   ├── score.py           # формула покрытия
│   ├── report.py          # Markdown + JSON
│   ├── verify.py          # 10 инвариантов
│   └── cli.py
└── tests/                 # 11 unit-тестов
```

---

## Быстрый старт

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

git clone --depth 1 https://github.com/fastapi/fastapi.git .repos/fastapi
python demo/tools/build_manifest.py --repo .repos/fastapi --out demo/file_manifest.csv

# полный прогон (offline)
python -m demo.cli ingest
python -m demo.cli retrieve
python -m demo.cli validate --provider offline
python -m demo.cli report
python -m demo.cli metrics
python -m demo.cli verify

# проверки самого инструмента
pytest demo/tests -q
```

Первая команда `retrieve` скачивает модель эмбеддингов (~470 МБ). Дальше работает кэш `.cache/emb`.

### С LLM

```dotenv
# .env
LLM_BASE_URL=https://api.z.ai/api/coding/paas/v4
LLM_API_KEY=<key>
LLM_MODEL=glm-5.3
```

```powershell
python -m demo.cli selfcheck
python -m demo.cli validate --provider openai
python -m demo.cli report
```

---

## Снимок прогона

| Метрика | Значение |
|---|---|
| Файлов / тестов | 50 / 649 |
| Тестов без assert | 0 |
| Покрытие (невзвешенное / взвешенное) | 97.8% / 97.8% |
| R1 / R2 / R3 / R4 / R5 | 100 / 89 / 100 / 100 / 100 |
| Цитат / уникальных тестов | 42 / 39 (все верифицированы evidence gate, 0 отклонений) |
| Precision@5 | 0.92 |
| Recall@pool | 0.96 |
| Стабильность (Jaccard × 3) | 1.00 |
| LLM-фаза | 138 с: 5 вызовов `glm-5.3`, все ответы распарсены с первой попытки |

---

## Как это работает

1. **Ingest.** AST разбирает `tests/**/test_*.py`, извлекает функции `test_*`, ассерты и `pytest.raises` с точными строками, HTTP-сигналы (`POST /items`, `status_code == 422`).
2. **Retrieve.** Для каждого AC три ранкера дают по 30 кандидатов: BM25, мультиязычные эмбеддинги и keyword-overlap. Объединение — Reciprocal Rank Fusion (k=60), затем топ-10 на AC и пул ≤25 на требование.
3. **Validate.** Offline: взвешенное совпадение ключевых слов, доменный фильтр, `excludes`. LLM: строгая JSON-схема, `temperature=0`, retry.
4. **Gate.** Цитата обязана быть дословной подстрокой указанных строк в файле, матчащем `tests/**/test_*.py`. Иначе AC понижается.
5. **Score.** `coverage = 100 · Σ(w·s) / Σw`, где `s` = 1.0 / 0.5 / 0.0.

---

## Сверка с `TZ_AGENT.md`

Построчная матрица соответствия — в [`tz_compliance.md`](tz_compliance.md): артефакты A1–A12, решения D1–D12, пайплайн §9, метрики §12, запреты §14. Итог сверки:

| Блок ТЗ | Статус |
|---|---|
| Артефакты A1–A12 (§6), критерии приёмки | ✅ выполнены |
| Решения D1–D12 (§2) | ✅ соблюдены; D6: клиент провайдер-агностичный, фактическая модель финального прогона `glm-5.3` записана в `run_meta.json` (замена модели без правок кода — механизм D6) |
| Пайплайн §9: ingest → index → RRF → LLM-валидация → evidence gate | ✅ финальный прогон исполнен LLM (`glm-5.3`, 5 вызовов, 0 retry); RRF по рангам, пул ≤25 — по формуле ТЗ |
| Метрики §12 | ✅ P@5 0.92 (цель 0.80), Jaccard 1.0 (цель 0.90), EvidenceValidity 42/42 (цель 1.00); Recall измерен на пуле требования: 0.96; CoverageMAE не считался — требует сквозной human-разметки |
| Самопроверка §13 / запреты §14 | ✅ verify 10/10 PASS; все 8 запретов соблюдаются |

Пункты, исполненные не в точной букве ТЗ (уровень gold set, форма показателя Recall, CoverageMAE), открыто перечислены в матрице с обоснованиями — как требует сам ТЗ (§12.2: «если цель не достигнута — так и написать»). Сверх ТЗ добавлены: offline-валидатор как детерминированный baseline-режим и третий ранкер в RRF.

---

## Публикация

Демонстрация опубликована: **[`outworkAnton/fastapi`, ветка `semantic-coverage-demo`](https://github.com/outworkAnton/fastapi/tree/semantic-coverage-demo)**, папка `semantic-coverage/`.

Содержимое папки: `TZ_AGENT.md`, четыре deliverable, `tz_compliance.md` (сверка с ТЗ), `AI_USAGE_LOG.md`, `requirements.txt`, `.env.example`, `demo/` (пайплайн и тесты), `artifacts/run_*/` — все прогоны, включая LLM-эксперименты (бесплатная Nemotron с нестабильными статусами — 8 её неточных цитат отклонены evidence gate; контрольные прогоны `glm-5.3`) и первый offline-прогон с некорректными доказательствами: история итераций сохранена, а не вычищена.

Быстрая проверка после клонирования форка: скопировать `semantic-coverage/demo` и `semantic-coverage/requirements.txt`, выполнить команды из раздела «Быстрый старт», затем `python -m demo.cli verify` — ожидается 10/10 PASS.

---

## Ограничения

- Не запускает тесты: оценивает наличие и содержание проверок, а не их прохождение.
- Offline-валидатор лексический: известный false negative — R2.AC4 (`tests/test_dependency_contextmanager.py`).
- Полнота ограничена декомпозицией требований: неописанное поведение не будет найдено.
- Один репозиторий, один фреймворк.

