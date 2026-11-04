# Semantic Coverage — сверка требований и автотестов

Инструмент сопоставляет бизнес-требования с автотестами и выдаёт оценку покрытия, которую можно проверить: у каждого вывода есть `файл:строка` и дословная цитата, прошедшая машинную проверку.

Демонстрация выполнена на `fastapi/fastapi` @ `5cb6272ed7e3e07eaf6978e1e65b94aca76fa8e0`.

---

## Статус

| | |
|---|---|
| Пайплайн | работает, `verify` — 10/10 PASS |
| Режим валидации | `offline` (LLM-ключ не предоставлен) |
| Прогон | `artifacts/run_20261103T224401Z` |
| Тесты | `pytest demo/tests` — 11 passed |
| Публикация форка | **выполнена**: [`outworkAnton/fastapi`, ветка `semantic-coverage-demo`](https://github.com/outworkAnton/fastapi/tree/semantic-coverage-demo) |

---

## Артефакты

| Файл | Назначение |
|---|---|
| [`solution_brief.md`](solution_brief.md) | Архитектура, обоснование, компромиссы, границы |
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
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=<key>
LLM_MODEL=deepseek/deepseek-flash
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
| Цитат / уникальных тестов | 21 / 20 |
| Precision@5 | 0.92 |
| Recall@pool | 0.96 |
| Стабильность (Jaccard × 3) | 1.00 |
| Время полного прогона | 21.55 с |
| LLM-вызовов | 0 |

---

## Как это работает

1. **Ingest.** AST разбирает `tests/**/test_*.py`, извлекает функции `test_*`, ассерты и `pytest.raises` с точными строками, HTTP-сигналы (`POST /items`, `status_code == 422`).
2. **Retrieve.** Для каждого AC три ранкера дают по 30 кандидатов: BM25, мультиязычные эмбеддинги и keyword-overlap. Объединение — Reciprocal Rank Fusion (k=60), затем топ-10 на AC и пул ≤25 на требование.
3. **Validate.** Offline: взвешенное совпадение ключевых слов, доменный фильтр, `excludes`. LLM: строгая JSON-схема, `temperature=0`, retry.
4. **Gate.** Цитата обязана быть дословной подстрокой указанных строк в файле, матчащем `tests/**/test_*.py`. Иначе AC понижается.
5. **Score.** `coverage = 100 · Σ(w·s) / Σw`, где `s` = 1.0 / 0.5 / 0.0.

---

## Отклонения от `TZ_AGENT.md`

Зафиксированы явно, чтобы не выглядели импровизацией:

| ТЗ | Факт | Причина |
|---|---|---|
| `chromadb` | numpy + `sentence-transformers` | Убирает скрытую загрузку англоязычной ONNX-модели; для 649 тестов ANN не нужен |
| 2 ранкера | 3 ранкера (+ keyword) | Векторный ранкер шумит и вытеснял точные совпадения; RRF по трём ранкам убрал ложные срабатывания на контрольных файлах |
| gold set на уровне AC | на уровне требования | P@5 в ТЗ определён как `top5(R)`; разметка 25 пар top-5 + 10 экспертных |
| `validator=openai` по умолчанию | `offline` | Ключ не предоставлен; LLM-путь реализован и готов |
| `pool_cap` 25 | 25 | совпадает |

---

## Публикация

Демонстрация опубликована: **[`outworkAnton/fastapi`, ветка `semantic-coverage-demo`](https://github.com/outworkAnton/fastapi/tree/semantic-coverage-demo)**, папка `semantic-coverage/`.

Содержимое папки: `TZ_AGENT.md`, четыре deliverable, `AI_USAGE_LOG.md`, `requirements.txt`, `.env.example`, `demo/` (пайплайн и тесты), `artifacts/run_*/` — все четыре прогона, включая первый offline-прогон с некорректными доказательствами: история итераций сохранена, а не вычищена.

Быстрая проверка после клонирования форка: скопировать `semantic-coverage/demo` и `semantic-coverage/requirements.txt`, выполнить команды из раздела «Быстрый старт», затем `python -m demo.cli verify` — ожидается 10/10 PASS.

---

## Ограничения

- Не запускает тесты: оценивает наличие и содержание проверок, а не их прохождение.
- Offline-валидатор лексический: известный false negative — R2.AC4 (`tests/test_dependency_contextmanager.py`).
- Полнота ограничена декомпозицией требований: неописанное поведение не будет найдено.
- Один репозиторий, один фреймворк.

