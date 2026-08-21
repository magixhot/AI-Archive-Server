# CURRENT_STATUS.md

# RT-0008 — AI Archive Server

## Project Status

**Status:** IN PROGRESS

Разработка RT-0008 продолжается согласно ROADMAP.

---

# Current HF

На данный момент активный HF-этап не назначен.

Последний завершённый этап:

## HF-0014 — Registry Reconciliation & Production Recovery

**Status:** COMPLETED

Completed:
2026-08-21

HF-0014 завершил production hardening Registry recovery и Synology runtime recovery.

---

# HF-0014 Verified Results

Подтверждено:

- authoritative archive reconciliation;
- Registry bootstrap and migrations;
- automatic Registry recovery after loss of `registry.db`;
- recovery from historical authoritative archive `/app/02_Models`;
- recovery from managed archive `/app/AI-Archive/models`;
- no automatic reconciliation when Registry already contains models;
- no accidental downgrade of existing VALIDATED records during normal restart;
- recovery without repeated Hugging Face download;
- Queue Manager readiness gating;
- Download Worker startup only after Queue Manager health;
- duplicate model protection;
- Download Worker failure isolation;
- persistent FAILED diagnostics;
- explicit retry lifecycle;
- retry metadata reset;
- retained partial download workspace;
- Container Manager restart recovery;
- full NAS reboot recovery;
- successful controlled Registry-loss recovery test;
- GitHub Actions CI validation.

Controlled Registry-loss test restored:

- `Qwen/Qwen3-0.6B`;
- `Qwen/Qwen3-30B-A3B-Instruct-2507`;
- `google/gemma-3-27b-it`;
- `moonshotai/Kimi-K2-Instruct`.

Recovered archive records are restored conservatively as:

```text
ARCHIVED
```

They are not automatically promoted to:

```text
VALIDATED
```

because validation state must not be invented after Registry loss.

Latest production recovery wiring commit:

```text
5aada76 Enable_automatic_registry_recovery
```

GitHub Actions result:

```text
completed / success
```

---

# Historical HF Sequence

Verified historical sequence:

- HF-0010.x — Integrity verification pipeline;
- HF-0011.1–HF-0011.4 — Integrity service / history / CLI integration;
- HF-0012.2–HF-0012.5 — Integrity public API / statistics / runtime normalization;
- HF-0013.3 — Isolated download workspace;
- HF-0014 — Registry Reconciliation & Production Recovery.

Historical numbering gaps and duplicate numbering are preserved exactly as recorded in Git.

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

### Maintained Project Documentation

- CURRENT_STATUS.md
- FILE_INDEX.md
- MODULE_INDEX.md
- API_INDEX.md
- CODING_STANDARDS.md
- DECISIONS.md
- ENGINEERING_WORKFLOW.md
- CHANGELOG.md
- COMPONENT_REGISTRY.md

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

### HF-0009 — Integrity Checker

**Status:** COMPLETED

### HF-0010 — Synchronization

**Status:** COMPLETED

### HF-0011 — Integrity Service Layer

**Status:** COMPLETED

### HF-0012 — Integrity Public API / Runtime Normalization

**Status:** COMPLETED

### HF-0013 — Download Workspace Isolation

**Status:** COMPLETED

### HF-0014 — Registry Reconciliation & Production Recovery

**Status:** COMPLETED

---

# Implemented Components

- Hugging Face Client
- Queue Manager
- Download Worker
- Archive Builder
- Registry
- SQLite Registry
- Model Cache
- Integrity Layer
- Registry Synchronization
- Registry Bootstrap
- Registry Recovery
- Authoritative Archive Reconciliation
- Docker Compose
- REST API
- GitHub Actions CI
- Real model downloading via `huggingface_hub`

---

# Current Runtime Startup Architecture

```text
registry-bootstrap
        │
        ├── schema
        ├── migrations
        └── Registry recovery when Registry is empty
                 │
                 ├── historical archive
                 │      /app/02_Models
                 │
                 └── managed archive
                        /app/AI-Archive/models
        │
        ▼
queue-manager
        │
        ▼
healthcheck = healthy
        │
        ▼
download-worker
```

If Registry already contains models, startup recovery does not modify Registry records.

---

# Next Task

Следующий HF-этап пока не назначен.

Перед началом нового Runtime development milestone необходимо:

1. завершить документационное закрытие HF-0014;
2. зафиксировать документацию отдельным Git commit;
3. убедиться, что CI остаётся зелёным;
4. определить следующий HF в соответствии с ROADMAP и актуальными приоритетами RT-0008.

Новый HF не должен создаваться только ради продолжения нумерации.

---

# Development Rule

Ни один новый Runtime-проект не начинается, пока документация проекта полностью не обновлена.

Документация является обязательной частью проекта и поддерживается в актуальном состоянии на каждом этапе разработки.

---

Last Updated:
2026-08-21
