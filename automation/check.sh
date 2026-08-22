#!/usr/bin/env bash
# HF-0018 — Validation / Dry-Run Check
# Verifies all prerequisites and reports what would be installed.
# Does NOT make any changes to the system.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_ARCHIVE_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

ok()   { PASS=$((PASS + 1)); echo -e "  ${GREEN}OK${NC}    $1"; }
fail() { FAIL=$((FAIL + 1)); echo -e "  ${RED}FAIL${NC}  $1"; }
warn() { WARN=$((WARN + 1)); echo -e "  ${YELLOW}WARN${NC}  $1"; }

check_command() {
    local name="$1"
    local required="${2:-false}"
    if command -v "${name}" &>/dev/null; then
        ok "${name}: $(command -v "${name}")"
    elif [[ "${required}" == "true" ]]; then
        fail "${name}: not found (required)"
    else
        warn "${name}: not found (optional)"
    fi
}

main() {
    echo "HF-0018 — Validation Check"
    echo "Repository: ${REPO_ROOT}"
    echo ""

    echo "=== Commands ==="
    check_command git true
    check_command python3 true
    check_command opencode false
    check_command gh false
    check_command ssh true
    check_command docker false
    check_command systemctl false
    echo ""

    echo "=== Authentication ==="
    if command -v gh &>/dev/null; then
        if gh auth status &>/dev/null 2>&1; then
            ok "gh auth: authenticated"
        else
            warn "gh auth: not authenticated"
        fi
    fi
    echo ""

    echo "=== SSH Config ==="
    if [[ -f "${HOME}/.ssh/config" ]]; then
        if grep -q "ai-nas" "${HOME}/.ssh/config" 2>/dev/null; then
            ok "SSH alias 'ai-nas': configured"
        else
            warn "SSH alias 'ai-nas': not found in ~/.ssh/config"
        fi
    else
        warn "~/.ssh/config: not found"
    fi
    echo ""

    echo "=== Repository Files ==="
    for f in opencode.json AI_AGENT_INSTRUCTIONS.md pyproject.toml compose.yaml; do
        if [[ -f "${REPO_ROOT}/${f}" ]]; then
            ok "${f}"
        else
            fail "${f}: not found"
        fi
    done
    echo ""

    echo "=== Automation Files ==="
    for f in bootstrap.sh worker-bridge.sh supervisor.sh watchdog.sh notify.sh check.sh; do
        if [[ -f "${SCRIPT_DIR}/${f}" ]]; then
            ok "automation/${f}"
        else
            fail "automation/${f}: not found"
        fi
    done
    echo ""

    echo "=== Templates ==="
    for f in opencode-worker.service opencode-worker.timer opencode-supervisor.service opencode-supervisor.timer opencode-watchdog.service opencode-watchdog.timer; do
        if [[ -f "${SCRIPT_DIR}/templates/${f}" ]]; then
            ok "templates/${f}"
        else
            fail "templates/${f}: not found"
        fi
    done
    echo ""

    echo "=== State Directories (would be created) ==="
    echo "  State: ${REPO_ROOT}/.automation/state/"
    echo "  Lock:  ${REPO_ROOT}/.automation/lock/"
    echo ""

    echo "=== systemd Units (would be installed to) ==="
    echo "  ${HOME}/.config/systemd/user/"
    echo ""

    echo "=== Summary ==="
    echo "  ${PASS} passed, ${FAIL} failed, ${WARN} warnings"
    echo ""

    if [[ ${FAIL} -gt 0 ]]; then
        echo "RESULT: FAIL — missing required prerequisites"
        exit 1
    elif [[ ${WARN} -gt 0 ]]; then
        echo "RESULT: PASS with warnings — optional prerequisites missing"
        exit 0
    else
        echo "RESULT: PASS — all checks passed"
        exit 0
    fi
}

main "$@"
