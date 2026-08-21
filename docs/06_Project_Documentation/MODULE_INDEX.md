# MODULE_INDEX

Project: AI Infrastructure

Document ID: DOC-0001.8

Version: 1.1

Status: Active


# 1. Purpose

Данный документ описывает логическую структуру модулей AI Archive Server, их ответственность и взаимодействие.

Используется для:

- понимания архитектуры Runtime;
- навигации между модулями;
- определения границ ответственности;
- анализа взаимодействия подсистем;
- передачи архитектурного контекста новым инженерным сессиям.

Документ описывает логические модули.

Фактическое состояние проекта определяется `CURRENT_STATUS.md`.

---

# 2. Runtime Architecture

Основной Runtime pipeline:

```text
Client
   │
   ▼
Queue Manager
   │
   ▼
Model Registry
   │
   ▼
QUEUED
   │
   ▼
Download Worker
   │
   ▼
Model Cache
   │
   ├── cache hit
   │      │
   │      ▼
   │   Existing validated archive
   │      │
   │      ▼
   │   Registry
   │
   └── cache miss
          │
          ▼
      HF Client
          │
          ▼
   Download Workspace
          │
          ▼
    Archive Builder
          │
          ▼
    Integrity Layer
          │
          ▼
   Authoritative Archive
          │
          ▼
     Model Registry
```

Registry read operations are exposed through Queue Manager API.

---

# 3. Startup Architecture

Runtime startup is coordinated through Docker Compose.

```text
registry-bootstrap
        │
        ▼
service_completed_successfully
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

This prevents services from starting against an uninitialized Registry or unavailable Queue Manager.

---

# 4. Core Modules

## 4.1 Queue Manager

Location:

```text
src/queue_manager/
```

Purpose:

Runtime HTTP control plane.

Responsibilities:

- health endpoint;
- model registration;
- model listing;
- model lookup;
- model family listing;
- explicit retry requests;
- interaction with Model Registry API.

Important runtime behavior:

- duplicate registration does not automatically requeue an existing model;
- existing model status is returned from Registry;
- retry is explicit;
- retry is allowed only for `FAILED` models.

Queue Manager is also the readiness dependency for Download Worker startup.

---

## 4.2 Download Worker

Location:

```text
src/download_worker/
```

Purpose:

Persistent queue-processing worker.

Responsibilities:

- polling queued models;
- checking Model Cache;
- transitioning model lifecycle state;
- downloading repositories;
- initiating archive creation;
- recording failures;
- continuing operation after individual model failures.

Normal acquisition flow:

```text
QUEUED
   ↓
DOWNLOADING
   ↓
archive pipeline
   ↓
VALIDATED
```

Failure flow:

```text
QUEUED
   ↓
DOWNLOADING
   ↓
exception
   ↓
FAILED
```

A model-specific exception must not terminate the persistent worker.

The worker remains running and continues processing later queue items.

---

## 4.3 HF Client

Location:

```text
src/hf_client/
```

Purpose:

Interaction with Hugging Face Hub.

Responsibilities:

- repository access;
- model metadata retrieval;
- repository download;
- Hugging Face authentication support.

Repository downloads are written first into transient download workspace.

They are not authoritative archives until the archive pipeline completes successfully.

---

## 4.4 Download Workspace

Runtime location:

```text
data/downloads/
```

Purpose:

Transient workspace used during repository acquisition.

Workspace identity is derived from the full Hugging Face model ID
(`namespace/repository`) to prevent collisions between repositories
with the same model name in different namespaces.

Properties:

- may contain incomplete downloads;
- may remain after failed acquisition;
- may be reused by a later explicit retry;
- is not authoritative storage;
- must not be interpreted as a valid archive solely because a directory exists;
- old basename-only workspaces (e.g. `data/downloads/Qwen3-0.6B`) are preserved
  but not automatically reused or migrated.

Canonical workspace path format:

```text
data/downloads/<namespace>/<repository>/
```

Legacy workspace path (preserved, not reused):

```text
data/downloads/<model-name>/
```

Partial workspace retention is intentional.

Identity and path safety are implemented in:

```text
src/hf_client/workspace.py
```

---

## 4.5 Model Cache

Location:

```text
src/storage/cache.py
```

Purpose:

Detect an already available valid local archive before remote acquisition.

Responsibilities:

- locating a local model archive;
- validating archive integrity;
- returning a usable archive path;
- preventing unnecessary repeated downloads.

A cache hit is accepted only when archive validation succeeds.

Model Cache does not own:

- Registry reconstruction;
- authoritative archive discovery;
- Registry reconciliation;
- queue recovery.

Those responsibilities belong to separate modules.

---

## 4.6 Archive Builder

Location:

```text
src/archive/
```

Purpose:

Create the canonical model archive representation.

Responsibilities include:

- constructing archive structure;
- copying repository content into archive representation;
- generating archive metadata;
- generating manifest data;
- coordinating archive lifecycle operations.

Archive Builder operates after successful repository acquisition.

---

## 4.7 Integrity Layer

Location:

```text
src/integrity/
```

Purpose:

Validate archive integrity.

Responsibilities:

- manifest validation;
- file verification;
- checksum verification;
- detection of invalid or incomplete archives.

Integrity validation is required before an archive can be treated as a valid cache source.

---

## 4.8 Storage Layer

Location:

```text
src/storage/
```

Purpose:

Provide archive storage operations.

Responsibilities include:

- archive path handling;
- local archive lookup;
- cache interaction;
- storage-related operations.

The authoritative archive and transient download workspace are separate concepts.

```text
data/downloads/
```

is transient.

```text
AI-Archive/models/
```

is authoritative model archive storage in the Synology runtime deployment.

---

# 5. Model Registry

Location:

```text
src/model_registry/
```

Purpose:

Persistent metadata and lifecycle authority for Runtime models.

Responsibilities:

- model registration;
- model lookup;
- model listing;
- family listing;
- lifecycle state management;
- storage metadata;
- checksum metadata;
- failure diagnostics;
- retry state reset;
- Registry bootstrap support;
- migration support.

Registry uses SQLite.

---

# 6. Registry Lifecycle

Supported model states include:

```text
QUEUED
DOWNLOADING
DOWNLOADED
ARCHIVING
ARCHIVED
VALIDATING
VALIDATED
READY
FAILED
```

State definitions are maintained in:

```text
src/model_registry/states.py
```

Registry is authoritative for current model lifecycle state.

---

# 7. Failure Diagnostics

A failed model is represented with:

```text
status = FAILED
error_message = <diagnostic information>
```

Failure diagnostics are persisted in Registry.

Public Registry query responses expose `error_message`.

For a non-failed model:

```text
error_message = null
```

This permits operational diagnosis without direct SQLite access.

---

# 8. Retry Module Behavior

Retry logic is implemented through Model Registry service/API and Queue Manager.

Public operation:

```text
POST /models/{model_id}/retry
```

Allowed transition:

```text
FAILED
   ↓
QUEUED
```

Retry is rejected when the model is not `FAILED`.

During retry, attempt-specific metadata is reset:

```text
error_message = NULL
download_started = NULL
download_finished = NULL
```

Existing transient workspace is not automatically destroyed.

This permits reuse/resume behavior by the download layer.

---

# 9. Registry Bootstrap

Location:

```text
src/model_registry/
```

Purpose:

Ensure Registry is initialized before Runtime services depend on it.

Docker Compose service:

```text
registry-bootstrap
```

Responsibilities:

- initialize Registry database when required;
- apply schema;
- apply migrations;
- record migration state;
- safely skip already applied migrations;
- support idempotent repeated startup.
- invoke Registry recovery orchestration after bootstrap;
- skip reconciliation when Registry already contains models;
- restore archive-backed records from historical and managed authoritative storage when Registry is empty.

Queue Manager starts only after bootstrap completes successfully.

---

# 10. Registry Migrations

Location:

```text
src/model_registry/migrations/
```

Purpose:

Version Registry schema changes without destructive manual database replacement.

Known migrations include:

```text
000_create_migration_table.sql
001_add_download_metadata.sql
002_add_archive_lifecycle.sql
```

Migration processing must be idempotent.

Existing Registry data must be preserved.

---

# 11. Reconciliation

Location:

```text
src/reconciliation/
```

Purpose:

Discover authoritative archives that already exist on storage and reconcile them with Registry.

Responsibilities include:

- authoritative archive discovery;
- model root discovery;
- model identity resolution;
- metadata reconstruction;
- Registry reconciliation.

Conceptual flow:

```text
Authoritative Archive
        │
        ▼
   Reconciliation
        │
        ▼
  Model identity
        │
        ▼
 Model Registry
```

Reconciliation is distinct from Model Cache.

Model Cache answers:

```text
Can this specific archive be used?
```

Reconciliation answers:

```text
What authoritative archives already exist,
and how should Registry represent them?
```

---

# 12. Archive Synchronization

Archive synchronization is implemented as a separate storage operation.

Purpose:

Safely synchronize archive content without destructive replacement.

Core rules:

- inspect changes before applying them;
- copy required changes;
- do not delete destination archive content implicitly;
- preserve authoritative archive safety.

Synchronization does not replace reconciliation.

---

# 13. Query API

The Runtime query interface is exposed through Queue Manager.

Current model operations include:

```text
GET  /health
POST /models
GET  /models
GET  /models/{model_id}
POST /models/{model_id}/retry
GET  /families
```

Detailed endpoint documentation belongs to:

```text
API_INDEX.md
```

---

# 14. Docker Runtime

Runtime services:

```text
registry-bootstrap
queue-manager
download-worker
```

Docker Compose is the authoritative service-management mechanism.

Container Manager is used for observation and platform-level restart behavior, not as the configuration source.

Runtime configuration must remain reproducible from repository-controlled files.

---

# 15. Recovery Behavior

Registry recovery is orchestrated by src/model_registry/recovery.py.

When Registry is empty, recovery reconciles:

- /app/02_Models historical authoritative archive;
- /app/AI-Archive/models managed archive.

Recovered records are restored conservatively as ARCHIVED and are not automatically promoted to VALIDATED.

When Registry already contains models, recovery exits without modifying existing records.

The current Runtime architecture has been verified across:

```text
Container Manager restart
NAS reboot
Registry bootstrap
Queue Manager health gating
Download Worker restart
failed model processing
explicit model retry
```

Persistent state survives service recreation through mounted storage.

Runtime services recover automatically according to Docker Compose restart policy and dependency configuration.

---

# 16. Module Boundaries

The following boundaries are intentional.

Model Cache:

```text
find + validate existing archive
```

Reconciliation:

```text
discover authoritative archive + restore Registry representation
```

Registry:

```text
metadata + lifecycle authority
```

Download Worker:

```text
queue execution + acquisition orchestration
```

HF Client:

```text
remote Hugging Face interaction
```

Archive Builder:

```text
canonical archive construction
```

Integrity Layer:

```text
archive verification
```

Queue Manager:

```text
HTTP control plane
```

Registry Bootstrap:

```text
database initialization + migrations
```

These responsibilities must not be merged implicitly.

---

# 17. Future Modules

Planned or not yet completed architectural areas include:

```text
Scheduler
Automation
Monitoring
Web UI
```

Future module implementation is governed by:

```text
ROADMAP.md
CURRENT_STATUS.md
```

No future module should be considered implemented solely because it appears in architectural documentation.

---

# 18. Architecture Principles

Each module must:

- have one primary responsibility;
- preserve clear module boundaries;
- minimize hidden coupling;
- expose explicit interfaces;
- preserve authoritative data;
- avoid destructive implicit recovery;
- support reproducible deployment;
- support automated testing;
- avoid machine-specific absolute paths;
- remain compatible with multi-computer development;
- follow the principle `Extend, never replace`.

---

# 19. Current Runtime Module Map

```text
Client
  │
  ▼
Queue Manager
  │
  ├──────────────► Query Operations
  │
  ├──────────────► Retry Control
  │
  ▼
Model Registry
  ▲
  │
  ├──────── Registry Bootstrap
  │          │
  │          └── Migrations
  │
  ├──────── Reconciliation
  │          ▲
  │          │
  │    Authoritative Archive
  │
  └──────── Download Worker
               │
               ▼
           Model Cache
            │       │
      cache hit   cache miss
            │       │
            │       ▼
            │    HF Client
            │       │
            │       ▼
            │  Download Workspace
            │       │
            │       ▼
            │  Archive Builder
            │       │
            │       ▼
            │  Integrity Layer
            │       │
            └───────┴────────► Authoritative Archive
```

---

Last Updated:

2026-08-21

End of Document