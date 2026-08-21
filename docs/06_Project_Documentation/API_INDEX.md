# API_INDEX

Project: AI Infrastructure

Document ID: DOC-0001.9

Version: 1.0

Status: Active

# 1. Purpose

Данный документ содержит индекс всех публичных API и интерфейсов AI Archive Server.

Используется для:

- поиска публичных функций;
- документирования интерфейсов модулей;
- анализа взаимодействия компонентов;
- поддержки разработки.

---

# 2. Model Registry API

## add_model(model)

Назначение:

Регистрация новой модели в Registry.

---

## get_models()

Назначение:

Получение списка зарегистрированных моделей.

---

## update_status(model_id, status)

Назначение:

Обновление состояния модели.

---

## model_exists(model_id)

Назначение:

Проверка наличия модели в Registry.

---

# 3. Queue Manager API

## GET /health

Назначение:

Проверка готовности Queue Manager.

---

## POST /models

Назначение:

Регистрация модели и постановка в очередь загрузки.

---

## POST /models/{model_id}/retry

Назначение:

Явный повтор загрузки модели со статусом FAILED.

---

## GET /models

Назначение:

Получение зарегистрированных моделей, включая error_message.

---

## GET /models/{model_id}

Назначение:

Получение состояния конкретной модели, включая error_message.

---

## GET /families

Назначение:

Получение списка семейств моделей.

---

# 4. Download Worker API

## process_queue()

Назначение:

Основной цикл обработки очереди.

---

## create_model_directory()

Назначение:

Создание структуры архива модели.

Создаёт:

- каталог модели;
- `manifest.json`.

---

# 5. Storage API

## get_cached_archive(model_id)

Назначение:

Возвращает путь к валидному локальному архиву модели либо `None`.

Перед использованием локального архива проверяются:

- `manifest.json`;
- структура архива;
- контрольные суммы файлов.

---

# 6. Archive Validation API

## validate_archive(archive_path)

Назначение:

Проверка корректности архива модели.

Выполняет проверку:

- manifest;
- метаданных;
- структуры репозитория;
- файлов архива.

Возвращает результаты проверки и итоговое поле `valid`.

---

# 7. Hugging Face Client API

## model_exists(repo_id)

Назначение:

Проверка существования репозитория.

Возвращает:

`bool`

---

## get_model_info(repo_id)

Назначение:

Получение информации о модели.

Возвращает:

`HFModelInfo`

---

## download_repository(repo_id, local_dir)

Назначение:

Загрузка репозитория Hugging Face.

Возвращает:

Локальный путь к скачанному репозиторию.

---

# 8. Registry Client API

## get_queued_models()

Назначение:

Получение списка моделей, ожидающих обработки.

---

## update_model_status()

Назначение:

Обновление состояния модели в Registry.

---

# 9. Registry Recovery Interfaces

## bootstrap_registry(...)

Назначение:

Идемпотентная инициализация Registry и применение migrations.

---

## recover_registry(...)

Назначение:

Production recovery orchestration для пустой Registry.

Выполняет bootstrap, проверяет наличие существующих записей и запускает reconciliation только если Registry пуста.

---

## reconcile_managed_archive(...)

Назначение:

Восстановление Registry records из managed archive AI-Archive/models без повторной загрузки моделей.

---

## reconcile_archive(...)

Назначение:

Сверка authoritative archive с Registry без повторной загрузки моделей.

---

## retry_failed(...)

Назначение:

Повторная постановка FAILED модели в очередь.

---

## get_all_models()

Назначение:

Получение расширенных Registry records с lifecycle и diagnostic metadata.

---

## get_model(...)

Назначение:

Получение расширенной Registry record конкретной модели.

---

# 10. Planned Public APIs

Планируемые интерфейсы:

- Synchronization
- Integrity Checker
- Scheduler
- Automation
- Monitoring

Развитие публичных API определяется документами ROADMAP.md и CURRENT_STATUS.md.

---

# 11. API Design Rules

Все публичные интерфейсы должны:

- иметь стабильный контракт;
- быть документированы;
- сохранять обратную совместимость;
- иметь понятные имена;
- быть независимыми от внутренней реализации модулей.

---

Last Updated:

2026-08-21

End of Document