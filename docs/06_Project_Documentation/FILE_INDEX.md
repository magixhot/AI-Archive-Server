# FILE_INDEX

Project: AI Infrastructure

Document ID: DOC-0001.7

Version: 1.0

Status: Active

# 1. Purpose

Данный документ содержит полный индекс файлов проекта.

Используется для:

- навигации по репозиторию;
- поиска компонентов;
- быстрого определения расположения файлов;
- поддержки документации проекта.

---

# 2. Root Directories

```
config/         Configuration files
data/           Archive storage
docker/         Docker configuration
docs/           Project documentation
logs/           Logs
registry/       SQLite registry and migrations
scripts/        Utility scripts
src/            Source code
```

---

# 3. Source Code

## src/hf_client/

```
client.py
    Hugging Face API abstraction

downloader.py
    Repository download implementation

workspace.py
    Transient download workspace identity and path safety

models.py
    HF data models

__init__.py
```

---

## src/model_registry/

```
service.py
    Registry business logic
recovery.py
    Registry recovery orchestration for empty Registry startup

bootstrap.py
    Registry schema initialization and migration bootstrap

database.py
    SQLite access

api.py
    Registry API

models.py
    Registry data models

states.py
    Model states

__init__.py
```

---

## src/download_worker/

```
worker.py
    Queue processing loop

archive.py
    Archive directory creation

registry_client.py
    Registry interface

main.py
    Worker entry point

__init__.py
```

---

## src/storage/

```
paths.py
    Archive storage paths

manager.py
    Storage directory management

validator.py
    Archive structure validation

cache.py
    Local archive cache

__init__.py
```

---

## src/queue_manager/

```
main.py
    Queue REST API

__init__.py
```

---

## src/scheduler/

```
config.py
    Scheduler configuration loading

tasks.py
    Scheduled maintenance task implementations

scheduler.py
    Periodic task scheduling loop

__main__.py
    Scheduler entry point

__init__.py
```

---

# 4. Registry

## registry/

```
data/
    registry.db

migrations/
    SQL migrations
```

---

# 5. Utility Scripts

## scripts/

```
migrate.py
    Database migration runner
```

---

# 6. Docker

## docker/

```
compose.yaml

download-worker/
    Dockerfile

queue-manager/
    Dockerfile

scheduler/
    Dockerfile
```

---

# 7. Project Documentation

Основная документация проекта располагается в:

```
docs/06_Project_Documentation/
```

Документы являются официальным источником информации о состоянии проекта и должны поддерживаться в актуальном состоянии.

```
AI_CHAT_START.md
PROJECT_CONTEXT.md
PROJECT_MAP.md
ROADMAP.md
CURRENT_STATUS.md
FILE_INDEX.md
MODULE_INDEX.md
API_INDEX.md
CODING_STANDARDS.md
DECISIONS.md
ENGINEERING_WORKFLOW.md
CHANGELOG.md
MASTER_INDEX.md
```

---

# 8. Project Directory Structure

```
AI Infrastructure
│
├── config/
├── data/
├── docker/
├── docs/
│   └── 06_Project_Documentation/
├── logs/
├── registry/
├── scripts/
└── src/
    ├── download_worker/
    ├── hf_client/
    ├── model_registry/
    ├── queue_manager/
    ├── scheduler/
    └── storage/
```

---

Last Updated:

2026-08-22

End of Document