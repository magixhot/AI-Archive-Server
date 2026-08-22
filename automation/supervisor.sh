#!/usr/bin/env bash
# HF-0018 — OpenCode Supervisor
# Supervises the OpenCode Worker Bridge and restarts on failure.
# Designed to be launched by systemd --user service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_ARCHIVE_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

STATE_DIR="${REPO_ROOT}/.automation/state"
LOCK_DIR="${REPO_ROOT}/.automation/lock"
LOG_FILE="${STATE_DIR}/supervisor.log"
PID_FILE="${LOCK_DIR}/supervisor.pid"
WORKER_SCRIPT="${SCRIPT_DIR}/worker-bridge.sh"
WATCHDOG_SCRIPT="${SCRIPT_DIR}/watchdog.sh"
MAX_RESTARTS="${OPENCODE_SUPERVISOR_MAX_RESTARTS:-5}"
RESTART_WINDOW="${OPENCODE_SUPERVISOR_RESTART_WINDOW:-3600}"
RESTART_DELAY="${OPENCODE_SUPERVISOR_RESTART_DELAY:-10}"

mkdir -p "${STATE_DIR}" "${LOCK_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

cleanup() {
    rm -f "${PID_FILE}"
    rm -f "${STATE_DIR}/worker-bridge.pid"
    log "Supervisor stopped"
}

check_stale_pid() {
    if [[ -f "${PID_FILE}" ]]; then
        local old_pid
        old_pid="$(cat "${PID_FILE}")"
        if kill -0 "${old_pid}" 2>/dev/null; then
            log "Supervisor already running (PID ${old_pid})"
            exit 0
        fi
        log "Removing stale PID file for ${old_pid}"
        rm -f "${PID_FILE}"
    fi
}

acquire_lock() {
    echo $$ > "${PID_FILE}"
    trap cleanup EXIT INT TERM
}

get_restart_count_in_window() {
    local state_file="${STATE_DIR}/supervisor-restarts"
    local now
    now="$(date +%s)"
    local window_start=$((now - RESTART_WINDOW))

    if [[ ! -f "${state_file}" ]]; then
        echo 0
        return
    fi

    local count=0
    while IFS= read -r line; do
        local ts
        ts="$(echo "${line}" | cut -d' ' -f1)"
        if [[ ${ts} -ge ${window_start} ]]; then
            count=$((count + 1))
        fi
    done < "${state_file}"

    echo "${count}"
}

record_restart() {
    local state_file="${STATE_DIR}/supervisor-restarts"
    date +%s >> "${state_file}"

    local now
    now="$(date +%s)"
    local window_start=$((now - RESTART_WINDOW))
    local tmp="${state_file}.tmp"
    : > "${tmp}"
    while IFS= read -r line; do
        local ts
        ts="$(echo "${line}" | cut -d' ' -f1)"
        if [[ ${ts} -ge ${window_start} ]]; then
            echo "${line}" >> "${tmp}"
        fi
    done < "${state_file}" 2>/dev/null || true
    mv "${tmp}" "${state_file}"
}

start_worker() {
    log "Starting worker bridge..."
    bash "${WORKER_SCRIPT}" &
    local worker_pid=$!
    log "Worker bridge started (PID ${worker_pid})"
    echo ${worker_pid} > "${STATE_DIR}/worker-bridge.pid"
    wait "${worker_pid}" || true
    local exit_code=$?
    log "Worker bridge exited with code ${exit_code}"
    return ${exit_code}
}

supervise() {
    local restart_count

    while true; do
        start_worker
        restart_count="$(get_restart_count_in_window)"

        if [[ ${restart_count} -ge ${MAX_RESTARTS} ]]; then
            log "ERROR: Too many restarts (${restart_count}/${MAX_RESTARTS}) in ${RESTART_WINDOW}s window"
            log "Supervisor exiting to prevent restart loop"
            break
        fi

        record_restart
        log "Restarting worker in ${RESTART_DELAY}s (restart ${restart_count}/${MAX_RESTARTS} in window)..."
        sleep "${RESTART_DELAY}"
    done
}

main() {
    check_stale_pid
    acquire_lock
    log "Supervisor starting (PID $$)"
    log "Repository: ${REPO_ROOT}"
    log "Max restarts: ${MAX_RESTARTS} per ${RESTART_WINDOW}s window"
    supervise
}

main "$@"
