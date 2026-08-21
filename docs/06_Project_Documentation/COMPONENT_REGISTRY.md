# COMPONENT_REGISTRY

Project: AI Infrastructure

Document ID: DOC-0001.4

Version: 1.0

Status: Active


# 1. Purpose

Данный документ является единым реестром компонентов AI Infrastructure.

Реестр используется для:

- регистрации компонентов проекта;
- хранения уникальных идентификаторов;
- предотвращения дублирования идентификаторов;
- навигации между Runtime-проектами и документацией.


# 2. Component Types

PROJECT

Документы верхнего уровня проекта.


DOC

Документация проекта.


STD

Стандарты проекта.


ADR

Архитектурные решения.


RT

Runtime-проекты.


HF

Этапы реализации Runtime-проектов.


MD

Реестр семейств AI-моделей.


# 3. PROJECT Components

## PROJECT-0000

Name:

Master Index

Status:

Active

Description:

Главный индекс проекта AI Infrastructure.


# 4. Runtime Projects

## RT-0008

Name:

AI Archive Server

Status:

Active

Description:

Автономный сервер хранения AI-моделей.


## RT-0009

Name:

AI Runtime

Status:

Planned

Description:

Локальный запуск AI-моделей.


## RT-0010

Name:

AI Deployment

Status:

Planned

Description:

Развёртывание AI-сервисов.


## RT-0011

Name:

Automation System

Status:

Planned

Description:

Автоматизация обслуживания AI Infrastructure.


# 5. HF Components

## HF-0001

Name:

Hugging Face Client

Status:

Completed


## HF-0002

Name:

Model Downloader

Status:

Completed


## HF-0003

Name:

Metadata Layer

Status:

Completed


## HF-0004

Name:

Archive Builder

Status:

Completed


## HF-0005

Name:

Model Registry

Status:

Completed


## HF-0006

Name:

Query API

Status:

Completed


## HF-0007

Name:

Storage Layer

Status:

Completed


## HF-0008

Name:

Model Cache

Status:

Completed


## HF-0009

Name:

Integrity Checker

Status:

Completed


## HF-0010

Name:

Archive Synchronization

Status:

Completed


## HF-0011

Name:

Integrity Service Layer

Status:

Completed

Description:

Historical Git milestone.

Verified sequence:

- HF-0011.1 — add integrity service layer
- HF-0011.2 — add integrity history storage
- HF-0011.3 — auto save integrity history
- HF-0011.4 — connect CLI to integrity service


## HF-0012

Name:

Integrity Public API / Runtime Normalization

Status:

Completed

Description:

Historical Git milestone.

Verified sequence includes:

- HF-0012.2 — add latest integrity result reader
- HF-0012.3 — add integrity public API
- HF-0012.3 — add integrity statistics CLI
- HF-0012.4 — normalize internal imports
- HF-0012.5 — normalize runtime packaging

Historical numbering is preserved exactly as recorded in Git.


## HF-0013

Name:

Download Workspace Isolation

Status:

Completed

Description:

Historical Git milestone.

Verified commit:

- HF-0013.3 — isolate download workspace

Historical gaps HF-0013.1 and HF-0013.2 are preserved and are not renumbered retroactively.


## HF-0014

Name:

Registry Reconciliation & Production Recovery

Status:

Completed

Description:

Completed RT-0008 production recovery milestone.

Scope:

- authoritative archive reconciliation;
- Registry bootstrap and migrations;
- Queue Manager readiness gating;
- duplicate model protection;
- Download Worker failure handling;
- explicit retry for FAILED models;
- Registry error diagnostics;
- retry lifecycle reset;
- Synology restart recovery;
- NAS reboot recovery;
- controlled Registry-loss recovery without redownload;


## HF-0015

Name:

Download Workspace Identity & Collision Safety

Status:

Completed

Description:

Completed RT-0008 workspace identity milestone.

Scope:

- full model identity for transient download workspace;
- collision prevention for equal repository names in different namespaces;
- preservation of retry/resume semantics;
- preservation of existing partial workspace data;
- safe workspace path construction;
- automated collision tests;
- Docker Compose and CI verification.


# 6. Standards

## STD-0001

AI Model Archive Standard

Status:

Active


## STD-0002

AI Infrastructure Operating Manual

Status:

Active


## STD-0003

Project Documentation Standard

Status:

Planned


## STD-0006

Container Standards

Status:

Planned


# 7. Architecture Decision Records

## ADR-0001

Docker Compose Standard

Status:

Accepted


## ADR-0002

Project Documentation Workflow

Status:

Accepted


## ADR-0003

Model Cache Responsibility

Status:

Accepted


# 8. Documentation

## DOC-0001

Project Documentation Framework

Status:

Completed


# 9. Model Registry

## MD-0001

Qwen


## MD-0002

Gemma


## MD-0003

Kimi


## MD-0004

DeepSeek


## MD-0005

Llama


## MD-0006

Mistral


Status:

Planned


# 10. Identifier Rules

Каждый идентификатор проекта:

- является уникальным;
- никогда не переиспользуется;
- сохраняется даже после удаления компонента;
- используется во всей документации проекта;
- регистрируется в данном документе.


# 11. Component Status Values

Planned

Компонент запланирован.


In Progress

Компонент находится в активной разработке.


Active

Компонент является действующей частью проекта.


Completed

Компонент полностью завершён.


Accepted

Архитектурное решение принято.


Reserved

Идентификатор зарезервирован для будущего использования.


Deprecated

Компонент больше не развивается, но сохраняется для совместимости и истории.


End of Document