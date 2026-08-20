# ROADMAP

Project: AI Infrastructure

Document ID: DOC-0001.6

Version: 1.1

Status: Active


# 1. Purpose

Данный документ определяет долгосрочный план развития проекта AI Infrastructure.

Roadmap является официальным планом развития проекта и обновляется после завершения крупных этапов.

Текущее operational state и точный локальный commit фиксируются в `CURRENT_STATUS.md`.


# 2. Project Vision

Создать автономную AI-инфраструктуру, позволяющую:

- хранить оригинальные AI-модели;
- автоматически получать модели из внешних источников;
- проверять целостность и происхождение сохранённых artifacts;
- восстанавливать Registry на основе authoritative archive;
- запускать модели локально;
- автоматизировать обслуживание;
- минимизировать зависимость от внешних сервисов;
- обеспечивать reproducible deployment на Synology и других поддерживаемых host systems.


# 3. Architecture Direction

AI Infrastructure развивается по трём уровням:

```text
AI Infrastructure
│
├── Engineering Layer
│   └── AI-Engineering
│
├── Runtime Layer
│   ├── RT-0008 — AI Archive Server
│   ├── RT-0009 — AI Runtime
│   └── future Runtime projects
│
└── Infrastructure / Deployment Layer
    ├── Docker Compose
    ├── Storage
    ├── Networking
    └── Synology DS925+