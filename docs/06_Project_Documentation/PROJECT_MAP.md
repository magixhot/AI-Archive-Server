# PROJECT_MAP

Project: AI Infrastructure

Document ID: DOC-0001.2

Version: 1.0

Status: Active


# 1. Purpose

Данный документ является картой проекта AI Infrastructure.

Он показывает:

- общую структуру проекта;
- взаимосвязь компонентов;
- архитектурные уровни;
- Runtime-проекты;
- направление развития AI Infrastructure.


# 2. Global Project Structure

AI Infrastructure
│
├── PROJECT-0000 (Master Index)
├── Standards
├── Infrastructure
├── Documentation
└── Runtime Projects

PROJECT-0000 является мастер-индексом AI Infrastructure и объединяет Runtime-проекты и документацию.

# 3. Runtime Projects

## RT-0008 — AI Archive Server

Status:
Active

Назначение:

Создание автономного сервера хранения AI-моделей.


## RT-0009 — AI Runtime

Status:
Planned

Назначение:

Локальный запуск AI-моделей.


## RT-0010 — AI Deployment

Status:
Planned

Назначение:

Развёртывание AI-сервисов.


## RT-0011 — Automation System

Status:
Planned

Назначение:

Автоматизация обслуживания AI Infrastructure.


# 4. RT-0008 Architecture

## RT-0008 — AI Archive Server

│
├── HF Client
│
├── Downloader
│
├── Metadata
│
├── Archive Builder
│
├── Model Registry
│
├── Query Layer
│
├── API
│
├── Storage Layer
│
└── Integrity Checker


Все перечисленные компоненты работают совместно и образуют единый сервер архива.


# 5. Component Responsibilities

HF Client

Получение моделей из Hugging Face.


Downloader

Загрузка моделей.


Metadata

Хранение информации о моделях.


Archive Builder

Создание архивной структуры.


Model Registry

Регистрация моделей.


Query Layer

Поиск моделей.


API

Программный интерфейс.


Storage Layer

Управление расположением файлов.


Integrity Checker

Проверка целостности архива.


# 6. Active Runtime

На текущем этапе основным Runtime-проектом AI Infrastructure является активный проект, определяемый документом CURRENT_STATUS.md.

PROJECT_MAP.md описывает архитектурную структуру проекта и не содержит оперативной информации о ходе разработки.

# 7. Navigation

Рекомендуемый порядок изучения документации:

1. AI_CHAT_START.md
2. PROJECT_CONTEXT.md
3. PROJECT_MAP.md
4. CURRENT_STATUS.md
5. FILE_INDEX.md
6. MODULE_INDEX.md
7. API_INDEX.md

После этого можно переходить к документации конкретного Runtime-проекта.


# 8. Development Rule

Любой новый компонент должен:

- соответствовать архитектуре проекта;
- быть задокументирован;
- иметь понятное назначение;
- не нарушать существующую структуру;
- расширять существующую архитектуру, а не заменять её.


End of Document
