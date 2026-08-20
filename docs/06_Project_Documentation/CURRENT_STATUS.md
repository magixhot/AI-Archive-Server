# CURRENT_STATUS.md

# RT-0008 — AI Archive Server

## Project Status

**Status:** IN PROGRESS

Разработка продолжается согласно ROADMAP.

---

# Current HF

## HF-0014 — Registry Reconciliation & Production Recovery

**Status:** IN PROGRESS

Historical milestone reconciliation completed.

Verified historical sequence:

- HF-0010.x — Integrity verification pipeline
- HF-0011.1–HF-0011.4 — Integrity service / history / CLI integration
- HF-0012.2–HF-0012.5 — Integrity public API / statistics / runtime normalization
- HF-0013.3 — Isolated download workspace

Historical numbering gaps and duplicate numbering are preserved exactly as recorded in Git.

Current scope:

- authoritative archive reconciliation;
- Registry bootstrap and recovery;
- Synology runtime reliability;
- failure handling;
- retry semantics;
- production hardening.

---

# Completed

## Documentation

### DOC-0001 — Project Documentation Framework

**Status:** COMPLETED

### Approved

- AI_CHAT_START.md
- PROJECT_CONTEXT.md
- PROJECT_MAP.md
- ROADMAP.md

### In Review

- CURRENT_STATUS.md
- FILE_INDEX.md
- MODULE_INDEX.md
- API_INDEX.md
- CODING_STANDARDS.md
- DECISIONS.md
- ENGINEERING_WORKFLOW.md
- CHANGELOG.md

---

## Runtime

### HF-0001 — Hugging Face Client

**Status:** COMPLETED

### HF-0002 — Queue Manager

**Status:** COMPLETED

### HF-0003 — Model Registry

**Status:** COMPLETED

### HF-0004 — Download Worker

**Status:** COMPLETED

### HF-0005 — Archive Builder

**Status:** COMPLETED

### HF-0006 — Queue Processing Pipeline

**Status:** COMPLETED

### HF-0007 — Real Hugging Face Downloader

**Status:** COMPLETED

### HF-0008 — Model Cache

**Status:** COMPLETED

### HF-0010 — Synchronization

**Status:** COMPLETED

---

## Implemented Components

- Hugging Face Client
- Queue Manager
- Download Worker
- Archive Builder
- Registry
- SQLite Registry
- Model Cache
- Registry Synchronization
- Docker Compose
- REST API
- Real model downloading via `huggingface_hub`

---

# Current Architecture

```text
             Model Cache
                  │
        ┌─────────┴─────────┐
        │                   │
   cache hit          cache miss
        │                   │
        ▼                   ▼
    Local Storage      HF Client
                            │
                            ▼
                       Downloader
                            │
                            ▼
                     Archive Builder
                            │
                            ▼
                         Registry
                            │
                            ▼
                      Local Storage
                            │
                            ▼
                         REST API
                            │
                            ▼
                            CLI
```

Архитектурная цепочка считается рабочей.

---

# Next Task

## HF-0014 — Registry Reconciliation & Production Recovery

**Status:** IN PROGRESS

### Goal

Завершить production hardening Registry recovery и runtime recovery на Synology.

HF-0014 должен обеспечивать:

- автоматическую сверку Registry и authoritative archive;
- восстановление после удаления `registry.db`;
- восстановление после переноса архива;
- восстановление после восстановления из резервной копии;
- повторную регистрацию моделей без повторного скачивания;
- корректную обработку FAILED downloads;
- явный retry lifecycle;
- устойчивый запуск после restart и NAS reboot.

---

# Development Rule

Ни один новый Runtime-проект не начинается, пока документация проекта полностью не обновлена.

Документация является обязательной частью проекта и поддерживается в актуальном состоянии на каждом этапе разработки.

---

Last Updated:
2026-08-20