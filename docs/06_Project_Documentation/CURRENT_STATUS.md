# CURRENT_STATUS.md

# RT-0008 — AI Archive Server

## Project Status

**Status:** IN PROGRESS

Разработка RT-0008 продолжается согласно ROADMAP.

---

# Current HF

## HF-0017 — Model Metadata Refresh & Upstream Revision Tracking

**Status:** IN PROGRESS

Goal:

Make archived/registered model metadata reproducible and refreshable without modifying authoritative model files. Track upstream Hugging Face repository revision/version metadata so the archive can detect source changes and preserve exact provenance over time.

Scope:

- provenance metadata contract for upstream revision tracking;
- Registry schema migration for upstream revision columns;
- metadata refresh service for safe, non-destructive upstream queries;
- provenance.json sidecar file for each archived model;
- scheduler integration for periodic metadata refresh;
- automated tests for revision resolution, unchanged metadata, changed-upstream detection, offline behavior, malformed IDs, and Registry/archive state preservation.

Rules:

- metadata refresh must not replace, delete, move, overwrite, or redownload authoritative archive content;
- upstream revision changes are recorded/reported conservatively;
- any future download/update policy remains an explicit separate decision.

---

## HF-0016 — Archive Automation Scheduler

**Status:** COMPLETED

Completed:
2026-08-22

Goal:

Implement a minimal, reproducible scheduler for safe periodic archive-maintenance operations.

Scope:

- scheduler module for periodic maintenance task execution;
- configurable task intervals via project config;
- integration with existing integrity, reconciliation, and archive-sync services;
- default task set: integrity verification, reconciliation, dry-run archive synchronization;
- all scheduled operations are read-only or conservative state-changing (additive only);
- no destructive operations, no archive data deletion, no Registry data removal;
- Docker Compose service for persistent scheduling;
- automated tests for scheduler logic;
- portable computed paths, no machine-specific hard-coded values.

Verified:

- 25 scheduler tests passing;
- full pytest suite (81 tests) passing;
- GitHub Actions CI validation;
- NAS Docker Compose rebuild and restart verification;
- scheduler container running and executing tasks;
- integrity check: 1 model checked, 1 passed;
- reconciliation: completed;
- archive sync dry-run: completed;
- Queue Manager health endpoint healthy;
- Download Worker running;
- archive data untouched.

## HF-0015 — Download Workspace Identity & Collision Safety

**Status:** COMPLETED

Completed:
2026-08-21

Goal:

Make transient download workspace identity-safe for full `model_id` / `repo_id` while preserving retry/resume behavior and existing partial workspace data.

Scope:

- eliminate collisions between repositories with the same model name;
- derive workspace identity from full model ID;
- preserve existing partial workspace data;
- preserve explicit retry/resume semantics;
- prevent path traversal or unsafe workspace paths;
- add collision-focused automated tests;
- verify Docker Compose runtime behavior and CI.

Verified:

- workspace identity derived from canonical `namespace/repository` format;
- different namespaces produce different workspace paths;
- same model_id maps deterministically to the same workspace path;
- path traversal, backslash, empty, malformed model IDs are rejected;
- legacy basename-only workspaces preserved and not reused;
- 20 collision/safety tests passing;
- full pytest suite (56 tests) passing;
- GitHub Actions CI validation;
- NAS Docker Compose rebuild and restart verification;
- workspace_path behavior confirmed inside runtime container;
- Queue Manager health endpoint healthy;
- Download Worker startup and polling verified;
- legacy workspaces present and unchanged;
- archive data untouched.

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
- HF-0014 — Registry Reconciliation & Production Recovery;
- HF-0015 — Download Workspace Identity & Collision Safety.

Historical numbering gaps and duplicate numbering are preserved exactly as recorded in Git.

---

# Completed

## HF-0015 — Download Workspace Identity & Collision Safety

**Status:** COMPLETED

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

HF-0017 — Model Metadata Refresh & Upstream Revision Tracking is IN PROGRESS.

---

# Historical HF Sequence

Verified historical sequence:

- HF-0010.x — Integrity verification pipeline;
- HF-0011.1–HF-0011.4 — Integrity service / history / CLI integration;
- HF-0012.2–HF-0012.5 — Integrity public API / statistics / runtime normalization;
- HF-0013.3 — Isolated download workspace;
- HF-0014 — Registry Reconciliation & Production Recovery;
- HF-0015 — Download Workspace Identity & Collision Safety;
- HF-0016 — Archive Automation Scheduler;
- HF-0017 — Model Metadata Refresh & Upstream Revision Tracking.

---

# Development Rule

Ни один новый Runtime-проект не начинается, пока документация проекта полностью не обновлена.

Документация является обязательной частью проекта и поддерживается в актуальном состоянии на каждом этапе разработки.

---

Last Updated:
2026-08-22
