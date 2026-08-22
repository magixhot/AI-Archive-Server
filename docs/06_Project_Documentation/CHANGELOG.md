# CHANGELOG

Project: AI Infrastructure

Document ID: DOC-0001.12

Version: 1.0

Status: Active


# Purpose

Данный документ содержит историю значимых изменений проекта AI Infrastructure.

Фиксируются только:

- изменения архитектуры;
- изменения структуры проекта;
- новые стандарты;
- принятые архитектурные решения;
- завершённые этапы разработки.

Мелкие изменения исходного кода, исправления опечаток и косметические изменения в журнал не заносятся.

---

# Change Log

# 2026-07-24

## PROJECT-0000 — Master Index

Создан главный индекс проекта AI Infrastructure.

Определена базовая архитектура проекта.

Создана структура основных разделов проекта.

---

# 2026-07-25

## RT-0008 — AI Archive Server

Начата разработка AI Archive Server.

Создан фундамент серверной архитектуры.

---

# 2026-07-26

## HF-0001 — Hugging Face Client

Status:

Completed

Реализован клиент взаимодействия с Hugging Face.

---

## HF-0002 — Model Downloader

Status:

Completed

Реализована загрузка моделей.

---

## HF-0003 — Metadata Layer

Status:

Completed

Добавлена обработка и хранение метаданных моделей.

---

## HF-0004 — Archive Builder

Status:

Completed

Реализовано формирование архивной структуры моделей.

---

## HF-0005 — Model Registry

Status:

Completed

Добавлен реестр моделей.

---

## HF-0006 — Query API

Status:

Completed

Добавлен API поиска и получения информации о моделях.

---

## HF-0007 — Storage Layer

Status:

Completed

Реализован уровень хранения архивов моделей.

---

# 2026-07-27

Продолжено развитие AI Archive Server.

Улучшена архитектура хранения моделей.

Подготовлена основа для проверки целостности архивов.

---

# 2026-07-28

## HF-0008 — Model Cache

Status:

Completed

Добавлена проверка локального архива перед загрузкой модели из Hugging Face.

Model Cache использует только валидные архивы с:

- manifest.json;
- полной структурой архива;
- корректными контрольными суммами файлов.

При наличии валидного локального архива повторная загрузка модели не выполняется.

---

## HF-0009 — Integrity Checker

Status:

Completed

Добавлена проверка целостности архивов моделей.

---

## HF-0010 — Archive Synchronization

Status:

Completed

Добавлена безопасная однонаправленная синхронизация архивных файлов.

Особенности:

- предварительный режим проверки изменений;
- отсутствие удаления файлов в целевом архиве;
- безопасная синхронизация только необходимых изменений.

---

## ADR-0003 — Model Cache Responsibility

Status:

Accepted

Принято архитектурное решение:

Model Cache отвечает только за:

- поиск локального архива;
- проверку целостности;
- возврат пути к валидному архиву.

Восстановление Registry, синхронизация Storage и Registry, а также восстановление очереди выделены в отдельный этап разработки.

---

## DOC-0001 — Project Documentation Framework

Status:

Completed

Завершена разработка единой системы проектной документации AI Infrastructure.

Созданы и согласованы основные документы Documentation Framework:

- AI_CHAT_START.md
- PROJECT_CONTEXT.md
- PROJECT_MAP.md
- DIRECTORY_STRUCTURE.md
- COMPONENT_REGISTRY.md
- ROADMAP.md
- CURRENT_STATUS.md
- FILE_INDEX.md
- MODULE_INDEX.md
- API_INDEX.md
- CODING_STANDARDS.md
- DECISIONS.md
- ENGINEERING_WORKFLOW.md
- CHANGELOG.md

Сформированы основные правила документации проекта:

- каждый документ имеет единственную область ответственности;
- документы не дублируют друг друга;
- CURRENT_STATUS.md является единственным источником актуального состояния проекта;
- CHANGELOG.md хранит только историю завершённых изменений;
- документация рассматривается как часть архитектуры проекта.

---

# Documentation Rules

В журнал заносятся только:

- новые Runtime-проекты;
- завершённые HF-этапы;
- новые стандарты;
- принятые архитектурные решения;
- изменения архитектуры;
- изменения структуры проекта;
- завершение крупных этапов разработки.

В журнал не заносятся:

- текущий статус проекта;
- будущие планы;
- исправления опечаток;
- косметические изменения;
- мелкие изменения исходного кода;
- изменения комментариев.

---

# Current Status

Последнее зарегистрированное событие:

HF-0017 — Model Metadata Refresh & Upstream Revision Tracking

Status:

Completed

---

# 2026-08-21

## HF Milestone Reconciliation

Status:

Completed

Проведена сверка исторических HF milestones с фактической Git history.

Подтверждено:

- HF-0011 — Integrity Service Layer;
- HF-0012 — Integrity Public API / Runtime Normalization;
- HF-0013 — Download Workspace Isolation;
- HF-0014 — Registry Reconciliation & Production Recovery.

Исторические пропуски и дублирование нумерации сохранены без ретроактивного переименования.

---

# 2026-08-21

## HF-0014 — Registry Reconciliation & Production Recovery

Status:

Completed

Завершён production recovery milestone для RT-0008.

Подтверждено:

- automatic Registry recovery after loss of registry.db;
- reconciliation from historical and managed authoritative archives;
- nonempty Registry recovery guard;
- recovery without repeated model download;
- Queue Manager readiness gating;
- Download Worker failure isolation;
- persistent FAILED diagnostics;
- explicit retry lifecycle;
- Container Manager restart recovery;
- NAS reboot recovery;
- successful controlled Registry-loss recovery test;
- GitHub Actions CI validation.

Final production wiring commit:

5aada76 Enable_automatic_registry_recovery

---

# 2026-08-21

## HF-0015 — Download Workspace Identity & Collision Safety

Status:

Completed

Завершён milestone collision safety для transient download workspace.

Подтверждено:

- workspace identity derived from canonical `namespace/repository` format;
- different namespaces produce different workspace paths;
- path traversal and unsafe model IDs rejected;
- legacy basename-only workspaces preserved and not reused;
- 20 collision/safety tests;
- full pytest suite (56 tests) passing;
- GitHub Actions CI validation;
- NAS Docker Compose rebuild and runtime verification;
- workspace_path behavior confirmed inside runtime container;
- Queue Manager health endpoint healthy;
- Download Worker startup and polling verified.

---

# 2026-08-22

## HF-0016 — Archive Automation Scheduler

Status:

Completed

Завершён milestone планировщика автоматического обслуживания архива.

Реализовано:

- scheduler module для периодического выполнения задач обслуживания;
- конфигурируемые интервалы через config/scheduler.json;
- интеграция с integrity, reconciliation, archive-sync сервисами;
- задачи: integrity verification, reconciliation, archive sync (dry-run);
- все операции read-only или additive state-changing;
- Docker Compose service для постоянного планирования;
- 25 автоматических тестов;
- 81 тест проходит (полная тестовая suites);
- GitHub Actions CI validation;
- NAS Docker Compose rebuild и restart verification;
- scheduler container выполняет задачи в runtime.

---

# 2026-08-22

## HF-0017 — Model Metadata Refresh & Upstream Revision Tracking

Status:

Completed

Завершён milestone обновления метаданных моделей и отслеживания upstream-ревизий.

Реализовано:

- provenance metadata contract для отслеживания upstream revision;
- Registry schema migration для upstream revision columns;
- metadata refresh service для безопасных неинвазивных upstream-запросов;
- provenance.json sidecar-файл для каждой архивной модели;
- scheduler integration для периодического обновления метаданных;
- automated tests для revision resolution, unchanged metadata, changed-upstream detection, offline behavior, malformed IDs, и Registry/archive state preservation.

Правила:

- metadata refresh не заменяет, не удаляет, не перемещает и не перезаписывает авторитетные архивные файлы;
- upstream revision changes записываются консервативно;
- любая будущая download/update policy остаётся отдельным решением.

---

Last Updated:

2026-08-22

End of Document