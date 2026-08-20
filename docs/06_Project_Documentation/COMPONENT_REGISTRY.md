# COMPONENT_REGISTRY

Project: AI Infrastructure

Document ID: DOC-0001.4

Version: 1.1

Status: Active


# 1. Purpose

Данный документ является единым реестром компонентов AI Infrastructure.

Реестр используется для:

- регистрации компонентов проекта;
- хранения уникальных идентификаторов;
- предотвращения дублирования идентификаторов;
- навигации между Runtime-проектами и документацией;
- фиксации официальных component identifiers;
- сохранения исторической идентичности завершённых компонентов.

Текущее operational state проекта определяется `CURRENT_STATUS.md`.

---

# 2. Component Types

## PROJECT

Документы и компоненты верхнего уровня проекта.

## DOC

Документация проекта.

## STD

Стандарты проекта.

## ADR

Архитектурные решения.

## RT

Runtime-проекты.

## HF

Исторические этапы реализации Runtime-проектов.

## MD

Реестр семейств AI-моделей.

---

# 3. PROJECT Components

## PROJECT-0000

Name:

Master Index

Status:

Active

Description:

Главный индекс проекта AI Infrastructure.

---

# 4. Runtime Projects

## RT-0008

Name:

AI Archive Server

Status:

Active

Description:

Автономный сервер acquisition, preservation, validation, reconciliation и хранения AI-моделей.

Current operational target:

```text
Synology DS925+
Docker Compose
automatic queue-driven model acquisition
authoritative model archive
Registry recovery
production hardening