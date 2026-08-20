# API_INDEX

Project: AI Infrastructure

Document ID: DOC-0001.9

Version: 1.1

Status: Active


# 1. Purpose

Данный документ содержит индекс публичных API и основных программных интерфейсов AI Archive Server.

Используется для:

- поиска публичных функций;
- документирования интерфейсов модулей;
- анализа взаимодействия компонентов;
- поддержки разработки;
- передачи API-контекста новым инженерным сессиям.

Фактическое operational state определяется `CURRENT_STATUS.md`.

---

# 2. HTTP API

HTTP API предоставляет Queue Manager.

Runtime service:

```text
queue-manager