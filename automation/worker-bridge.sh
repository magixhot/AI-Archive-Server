#!/usr/bin/env bash
# HF-0018 — OpenCode Worker Bridge
# Bridges the local OpenCode agent to the remote repository.
# Designed to be launched by systemd --user service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_ARCHIVE_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

STATE_DIR="${REPO_ROOT}/.automation/state"
LOCK_DIR="${REPO_ROOT}/.automation/lock"
LOG_FILE="${STATE_DIR}/worker-bridge.log"
PID_FILE="${LOCK_DIR}/worker-bridge.pid"
WORKER_TIMEOUT="${OPENCODE_WORKER_TIMEOUT:-300}"

mkdir -p "${STATE_DIR}" "${LOCK_DIR}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

cleanup() {
    rm -f "${PID_FILE}"
    log "Worker bridge stopped"
}

check_stale_pid() {
    if [[ -f "${PID_FILE}" ]]; then
        local old_pid
        old_pid="$(cat "${PID_FILE}")"
        if kill -0 "${old_pid}" 2>/dev/null; then
            log "Worker bridge already running (PID ${old_pid})"
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

wait_for_opencode() {
    local retries=0
    local max_retries=10
    while ! command -v opencode &>/dev/null; do
        retries=$((retries + 1))
        if [[ ${retries} -ge ${max_retries} ]]; then
            log "ERROR: opencode not found after ${max_retries} attempts"
            exit 1
        fi
        log "Waiting for opencode to be available (attempt ${retries}/${max_retries})..."
        sleep 5
    done
}

wait_for_repo() {
    if [[ ! -f "${REPO_ROOT}/opencode.json" ]]; then
        log "ERROR: Repository not found at ${REPO_ROOT}"
        exit 1
    fi
}

run_worker() {
    log "Worker bridge starting (PID $$)"
    log "Repository: ${REPO_ROOT}"
    log "Worker timeout: ${WORKER_TIMEOUT}s"

    while true; do
        log "Worker bridge heartbeat — $(date '+%Y-%m-%d %H:%M:%S')"

        if [[ -f "${REPO_ROOT}/.automation/state/supervisor-shutdown" ]]; then
            log "Shutdown signal detected, exiting"
            break
        fi

        sleep "${WORKER_TIMEOUT}"
    done
}

main() {
    check_stale_pid
    acquire_lock
    wait_for_opencode
    wait_for_repo
    run_worker
}

main "$@"
