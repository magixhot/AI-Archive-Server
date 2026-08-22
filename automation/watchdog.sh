#!/usr/bin/env bash
# HF-0018 — Watchdog / Timeout Monitor
# Monitors worker bridge health and triggers notification on failure.
# Designed to be launched by systemd --user timer.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_ARCHIVE_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

STATE_DIR="${REPO_ROOT}/.automation/state"
LOCK_DIR="${REPO_ROOT}/.automation/lock"
LOG_FILE="${STATE_DIR}/watchdog.log"
WORKER_PID_FILE="${STATE_DIR}/worker-bridge.pid"
SUPERVISOR_PID_FILE="${LOCK_DIR}/supervisor.pid"
WATCHDOG_TIMEOUT="${OPENCODE_WATCHDOG_TIMEOUT:-600}"
NOTIFY_SCRIPT="${SCRIPT_DIR}/notify.sh"

mkdir -p "${STATE_DIR}" "${LOCK_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

is_process_alive() {
    local pid_file="$1"
    if [[ ! -f "${pid_file}" ]]; then
        return 1
    fi
    local pid
    pid="$(cat "${pid_file}")"
    if kill -0 "${pid}" 2>/dev/null; then
        return 0
    fi
    return 1
}

check_worker_health() {
    if is_process_alive "${WORKER_PID_FILE}"; then
        return 0
    fi
    return 1
}

check_supervisor_health() {
    if is_process_alive "${SUPERVISOR_PID_FILE}"; then
        return 0
    fi
    return 1
}

check_queue_manager() {
    if command -v docker &>/dev/null; then
        if docker compose ps queue-manager 2>/dev/null | grep -q "Up"; then
            return 0
        fi
    fi
    return 1
}

notify_failure() {
    local message="$1"
    if [[ -x "${NOTIFY_SCRIPT}" ]]; then
        bash "${NOTIFY_SCRIPT}" "AI Archive Watchdog" "${message}" || true
    fi
    log "ALERT: ${message}"
}

main() {
    log "Watchdog check starting"

    local issues=0

    if ! check_worker_health; then
        log "Worker bridge: NOT RUNNING"
        issues=$((issues + 1))
    else
        log "Worker bridge: healthy"
    fi

    if ! check_supervisor_health; then
        log "Supervisor: NOT RUNNING"
        issues=$((issues + 1))
    else
        log "Supervisor: healthy"
    fi

    if ! check_queue_manager; then
        log "Queue Manager: NOT DETECTED"
    else
        log "Queue Manager: healthy"
    fi

    if [[ ${issues} -gt 0 ]]; then
        notify_failure "AI Archive automation has ${issues} issue(s). Check watchdog.log for details."
    fi

    log "Watchdog check complete: ${issues} issue(s) found"
    return ${issues}
}

main "$@"
