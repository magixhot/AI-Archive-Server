# LOCAL_AGENT_INSTALLATION.md

# AI Archive Server

## Local Agent Bootstrap — Second Computer Installation

Document ID: DOC-0001.14

Version: 1.0

Status: Active

---

# 1. Purpose

This document describes how to install the OpenCode Worker/Supervisor automation on a new Windows + WSL computer.

The bootstrap is portable and idempotent: rerunning it will not duplicate configuration or damage existing state.

---

# 2. Prerequisites

## Required

| Prerequisite | Install | Verify |
|---|---|---|
| Git | https://git-scm.com | `git --version` |
| Python 3.12+ | https://www.python.org | `python3 --version` |
| SSH client | Pre-installed on WSL | `ssh -V` |
| Repository clone | `git clone <repo-url>` | `ls opencode.json` |

## Optional

| Prerequisite | Install | Purpose |
|---|---|---|
| OpenCode | https://opencode.ai | Local AI agent |
| GitHub CLI | https://cli.github.com | PR/issue management |
| Docker | https://docs.docker.com/desktop | NAS runtime access |

---

# 3. Installation Procedure

## Step 1: Clone the repository

```bash
git clone <repository-url>
cd AI-Archive-Server
```

## Step 2: Verify prerequisites

```bash
bash automation/check.sh
```

This runs a dry-run validation that reports exactly what is installed and what is missing. It makes no changes.

## Step 3: Run bootstrap

```bash
bash automation/bootstrap.sh --install
```

The bootstrap will:
- verify all prerequisites
- create `.automation/state/` and `.automation/lock/` directories
- install systemd --user service and timer templates
- update `.gitignore` with automation state entries
- prepare the notification helper

## Step 4: Reload systemd

```bash
systemctl --user daemon-reload
```

## Step 5: Start services

```bash
systemctl --user start opencode-worker
systemctl --user start opencode-supervisor
systemctl --user start opencode-watchdog.timer
```

## Step 6: Verify

```bash
systemctl --user status opencode-worker
systemctl --user status opencode-supervisor
systemctl --user status opencode-watchdog.timer
```

---

# 4. SSH Configuration for NAS Access

To enable non-destructive NAS prerequisite checks, configure the `ai-nas` SSH alias:

```bash
# ~/.ssh/config
Host ai-nas
    HostName <NAS-IP-or-hostname>
    User <NAS-username>
    IdentityFile ~/.ssh/<private-key>
```

The bootstrap will detect and report the presence of this alias.

**Never commit private SSH keys or credentials to the repository.**

---

# 5. Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `AI_ARCHIVE_ROOT` | Auto-detected | Override project root discovery |
| `OPENCODE_WORKER_TIMEOUT` | `300` | Worker heartbeat interval (seconds) |
| `OPENCODE_SUPERVISOR_MAX_RESTARTS` | `5` | Max worker restarts per window |
| `OPENCODE_SUPERVISOR_RESTART_WINDOW` | `3600` | Restart counting window (seconds) |
| `OPENCODE_SUPERVISOR_RESTART_DELAY` | `10` | Delay between restart attempts (seconds) |
| `OPENCODE_WATCHDOG_TIMEOUT` | `600` | Watchdog check interval (seconds) |

---

# 6. Available Commands

## Dry-run validation

```bash
bash automation/check.sh
```

## Full bootstrap (install)

```bash
bash automation/bootstrap.sh --install
```

## Check mode (no changes)

```bash
bash automation/bootstrap.sh --check
```

## Uninstall

```bash
bash automation/bootstrap.sh --uninstall
```

---

# 7. systemd Units

The following units are installed to `~/.config/systemd/user/`:

| Unit | Type | Purpose |
|---|---|---|
| `opencode-worker.service` | Service | Worker bridge process |
| `opencode-worker.timer` | Timer | Periodic worker bridge restart |
| `opencode-supervisor.service` | Service | Supervisor with restart logic |
| `opencode-supervisor.timer` | Timer | Periodic supervisor restart |
| `opencode-watchdog.service` | Oneshot | Health check execution |
| `opencode-watchdog.timer` | Timer | Periodic health check schedule |

---

# 8. Troubleshooting

## Worker bridge not starting

```bash
# Check logs
journalctl --user -u opencode-worker -n 50

# Check if opencode is available
which opencode

# Check PID file
cat .automation/lock/worker-bridge.pid
```

## Supervisor not restarting worker

```bash
# Check restart count
cat .automation/state/supervisor-restarts

# Check supervisor logs
journalctl --user -u opencode-supervisor -n 50
```

## Watchdog reports issues

```bash
# Run watchdog manually
bash automation/watchdog.sh

# Check watchdog logs
cat .automation/state/watchdog.log
```

## Notifications not working

The notification helper supports:
- Windows (via `powershell.exe` in WSL)
- Linux (via `notify-send`)
- macOS (via `osascript`)

If none are available, notifications are logged to `.automation/state/notifications.log`.

---

# 9. Security Notes

- **Never commit** GitHub tokens, SSH private keys, passwords, or auth material
- The bootstrap **verifies** prerequisite presence but **never invents** secrets
- All paths are derived from `HOME`, script location, or repository root
- No machine-specific Windows profile paths are hard-coded
- State directories (`.automation/state/`, `.automation/lock/`) are gitignored

---

# 10. Uninstallation

```bash
bash automation/bootstrap.sh --uninstall
```

This stops and removes all systemd units. State directories are preserved for manual cleanup.

To remove state:

```bash
rm -rf .automation/
```

---

Last Updated:

2026-08-22

End of Document
