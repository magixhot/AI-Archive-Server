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

## POST /queue

Назначение:

Добавление модели в очередь загрузки.

Пример ответа:

```json
{
    "model_id": "...",
    "status": "QUEUED"
}
```

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

# 9. Planned Public APIs

Планируемые интерфейсы:

- Synchronization
- Integrity Checker
- Scheduler
- Automation
- Monitoring

Развитие публичных API определяется документами ROADMAP.md и CURRENT_STATUS.md.

---

# 10. API Design Rules

Все публичные интерфейсы должны:

- иметь стабильный контракт;
- быть документированы;
- сохранять обратную совместимость;
- иметь понятные имена;
- быть независимыми от внутренней реализации модулей.

---

Last Updated:

2026-07-29

End of Document