# ENGINEERING_WORKFLOW.md

# AI Archive Server

## Engineering Workflow

---

# Purpose

Данный документ определяет единый инженерный процесс разработки Runtime-проектов.

Каждый новый HF-этап должен следовать этому процессу.

Документация является частью исходного кода проекта.

---

# Development Workflow

```
Documentation
        ↓
Architecture Review
        ↓
Implementation
        ↓
Code Review
        ↓
Functional Testing
        ↓
Infrastructure First
        ↓
Docker Compose Integration Test
        ↓
Documentation Update
        ↓
Git Commit
        ↓
HF Completed
```

---

# Documentation First

Перед началом любого HF необходимо:

1. Прочитать AI_CHAT_START.md.
2. Проверить CURRENT_STATUS.md.
3. Ознакомиться с DECISIONS.md.
4. Проверить ROADMAP.md.

Только после этого начинается разработка.

---

# One File → One Review

Каждый изменённый файл проходит отдельный цикл проверки.

```
File
 ↓
Review
 ↓
Fix
 ↓
Review
 ↓
Approved
```

После утверждения переходят к следующему файлу.

---

# Infrastructure First

Перед поиском ошибки в коде необходимо проверить:

1. Docker Compose
2. Containers
3. Volumes
4. Storage Paths
5. Registry
6. Configuration
7. Network
8. Только после этого Python-код

Большинство ошибок распределённой системы связано с инфраструктурой, а не с алгоритмами.

---

# Docker Integration Test

Ни один HF не считается завершённым без проверки через Docker Compose.

Проверяется:

- запуск сервисов;
- взаимодействие сервисов;
- работа volumes;
- работа Registry;
- работа архивного хранилища.

---

# Debugging

Во время поиска ошибок допускается временный диагностический код.

Правила:

- диагностический код не коммитится;
- после завершения проверки полностью удаляется;
- рабочая версия проекта не содержит временных print().

---

# Multi-Workstation Development

Проект должен одинаково работать на любой рабочей станции.

Правила:

- только относительные пути;
- использование pathlib;
- Docker Compose;
- отсутствие абсолютных путей Windows;
- одинаковая структура проекта.

---

# Documentation Update

После завершения каждого HF обновляется документация проекта.

Минимальный набор документации определяется характером выполненных изменений.

Обновляются только документы, область ответственности которых была затронута.

Как правило:

- CURRENT_STATUS.md — при изменении текущего состояния проекта;
- CHANGELOG.md — при завершении крупных этапов, изменении архитектуры или принятии новых решений.

При необходимости обновляются:

- ROADMAP.md;
- MODULE_INDEX.md;
- API_INDEX.md;
- FILE_INDEX.md;
- DECISIONS.md;
- COMPONENT_REGISTRY.md.

Документация обновляется только при изменении её предметной области и не должна изменяться формально "для отметки".

---

# Definition of Done

HF считается завершённым только после выполнения всех этапов процесса разработки и успешного Docker Integration Test.

---

# Goal

Создать воспроизводимый инженерный процесс разработки для всех Runtime-проектов экосистемы AI Runtime Engineering Template.