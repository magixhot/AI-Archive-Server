#!/usr/bin/env bash
# HF-0018 — Portable Local Agent Bootstrap
# Portable bootstrap for OpenCode Worker/Supervisor automation.
# Safe to rerun: idempotent, no destructive changes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0
DRY_RUN=false

log_pass() { PASS=$((PASS + 1)); echo -e "  ${GREEN}PASS${NC} $1"; }
log_fail() { FAIL=$((FAIL + 1)); echo -e "  ${RED}FAIL${NC} $1"; }
log_warn() { WARN=$((WARN + 1)); echo -e "  ${YELLOW}WARN${NC} $1"; }
log_info() { echo -e "  ${YELLOW}INFO${NC} $1"; }

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Portable bootstrap for AI Archive Server local agent automation.

Options:
  --check       Dry-run mode: verify prerequisites and report what would
                be installed without making changes.
  --install     Install automation (default if no mode specified).
  --uninstall   Remove installed automation units.
  --help        Show this help message.

EOF
    exit 0
}

# --- Prerequisite checks ---

check_git() {
    if command -v git &>/dev/null; then
        log_pass "git found: $(git --version)"
    else
        log_fail "git not found — required"
    fi
}

check_python() {
    if command -v python3 &>/dev/null; then
        local ver
        ver="$(python3 --version 2>&1)"
        log_pass "python3 found: ${ver}"
    else
        log_fail "python3 not found — required"
    fi
}

check_opencode() {
    if command -v opencode &>/dev/null; then
        log_pass "opencode found: $(command -v opencode)"
    else
        log_warn "opencode not found — install from https://opencode.ai"
    fi
}

check_gh() {
    if command -v gh &>/dev/null; then
        log_pass "gh (GitHub CLI) found: $(command -v gh)"
        if gh auth status &>/dev/null 2>&1; then
            log_pass "gh auth status: authenticated"
        else
            log_warn "gh auth status: not authenticated — run 'gh auth login'"
        fi
    else
        log_warn "gh (GitHub CLI) not found — install from https://cli.github.com"
    fi
}

check_ssh() {
    if command -v ssh &>/dev/null; then
        log_pass "ssh found: $(command -v ssh)"
    else
        log_fail "ssh not found — required for NAS access"
    fi

    if grep -q "ai-nas" "${HOME}/.ssh/config" 2>/dev/null; then
        log_pass "SSH alias 'ai-nas' found in ~/.ssh/config"
    else
        log_warn "SSH alias 'ai-nas' not found in ~/.ssh/config — configure manually"
    fi
}

check_systemd() {
    if command -v systemctl &>/dev/null; then
        if systemctl --user status &>/dev/null 2>&1; then
            log_pass "systemd --user available"
        else
            log_warn "systemd --user may not be available"
        fi
    else
        log_warn "systemctl not found — systemd integration disabled"
    fi
}

check_docker() {
    if command -v docker &>/dev/null; then
        log_pass "docker found: $(command -v docker)"
    else
        log_warn "docker not found — NAS runtime operations unavailable"
    fi
}

check_dependencies() {
    echo "=== Prerequisite Checks ==="
    check_git
    check_python
    check_opencode
    check_gh
    check_ssh
    check_systemd
    check_docker
    echo ""
}

# --- Project working-directory discovery ---

discover_project_root() {
    if [[ -n "${AI_ARCHIVE_ROOT:-}" ]] && [[ -d "${AI_ARCHIVE_ROOT}" ]]; then
        echo "${AI_ARCHIVE_ROOT}"
        return
    fi

    local candidate
    candidate="$(cd "${SCRIPT_DIR}/.." && pwd)"
    if [[ -f "${candidate}/opencode.json" ]] && [[ -f "${candidate}/pyproject.toml" ]]; then
        echo "${candidate}"
        return
    fi

    log_fail "Cannot discover project root. Set AI_ARCHIVE_ROOT or run from repository."
    exit 1
}

# --- State/lock directory creation ---

ensure_state_dirs() {
    local project_root="$1"
    local state_dir="${project_root}/.automation/state"
    local lock_dir="${project_root}/.automation/lock"

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_info "Would create state directory: ${state_dir}"
        log_info "Would create lock directory: ${lock_dir}"
        return
    fi

    mkdir -p "${state_dir}" "${lock_dir}"
    log_pass "State directories created: ${state_dir}, ${lock_dir}"
}

# --- systemd user service installation ---

install_systemd_units() {
    local project_root="$1"
    local templates_dir="${SCRIPT_DIR}/templates"
    local systemd_dir="${HOME}/.config/systemd/user"
    local opencode_bin
    opencode_bin="$(command -v opencode 2>/dev/null || echo "")"

    if ! command -v systemctl &>/dev/null; then
        log_warn "systemctl not available — skipping systemd unit installation"
        return
    fi

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_info "Would install systemd user units to: ${systemd_dir}"
        for tmpl in "${templates_dir}"/*.service "${templates_dir}"/*.timer; do
            [[ -f "${tmpl}" ]] || continue
            log_info "  Would install: $(basename "${tmpl}")"
        done
        return
    fi

    mkdir -p "${systemd_dir}"

    for tmpl in "${templates_dir}"/*.service "${templates_dir}"/*.timer; do
        [[ -f "${tmpl}" ]] || continue
        local name
        name="$(basename "${tmpl}")"
        local dest="${systemd_dir}/${name}"

        if [[ -f "${dest}" ]]; then
            log_info "Unit already exists, skipping: ${name}"
            continue
        fi

        sed \
            -e "s|@@REPO_ROOT@@|${project_root}|g" \
            -e "s|@@OPENCODE_BIN@@|${opencode_bin}|g" \
            -e "s|@@HOME@@|${HOME}|g" \
            "${tmpl}" > "${dest}"
        log_pass "Installed: ${name}"
    done
}

# --- OpenCode configuration verification ---

verify_opencode_config() {
    local project_root="$1"
    local opencode_json="${project_root}/opencode.json"
    local instructions="${project_root}/AI_AGENT_INSTRUCTIONS.md"

    if [[ -f "${opencode_json}" ]]; then
        log_pass "opencode.json found at project root"
    else
        log_fail "opencode.json not found at project root"
    fi

    if [[ -f "${instructions}" ]]; then
        log_pass "AI_AGENT_INSTRUCTIONS.md found at project root"
    else
        log_warn "AI_AGENT_INSTRUCTIONS.md not found"
    fi
}

# --- .gitignore update ---

ensure_gitignore_entries() {
    local project_root="$1"
    local gitignore="${project_root}/.gitignore"
    local entries_needed=(
        ".automation/state/"
        ".automation/lock/"
    )

    if [[ ! -f "${gitignore}" ]]; then
        log_warn ".gitignore not found"
        return
    fi

    local changed=false
    for entry in "${entries_needed[@]}"; do
        if grep -qF "${entry}" "${gitignore}" 2>/dev/null; then
            continue
        fi
        if [[ "${DRY_RUN}" == "true" ]]; then
            log_info "Would add to .gitignore: ${entry}"
        else
            echo "" >> "${gitignore}"
            echo "# HF-0018 automation state" >> "${gitignore}"
            echo "${entry}" >> "${gitignore}"
            changed=true
        fi
    done

    if [[ "${changed}" == "true" ]]; then
        log_pass "Updated .gitignore with automation state entries"
    fi
}

# --- Windows notification helper (WSL-aware) ---

install_notification_helper() {
    local project_root="$1"
    local helper="${SCRIPT_DIR}/notify.sh"

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_info "Notification helper available at: ${helper}"
        return
    fi

    chmod +x "${helper}" 2>/dev/null || true
    log_pass "Notification helper ready: ${helper}"
}

# --- Main ---

main() {
    local mode="install"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --check)    mode="check"; DRY_RUN=true; shift ;;
            --install)  mode="install"; shift ;;
            --uninstall) mode="uninstall"; shift ;;
            --help)     usage ;;
            *)          echo "Unknown option: $1"; usage ;;
        esac
    done

    echo "HF-0018 — Portable Local Agent Bootstrap"
    echo "Mode: ${mode}"
    echo "Repository root: ${REPO_ROOT}"
    echo ""

    local project_root
    project_root="$(discover_project_root)"

    # Always run prerequisite checks
    check_dependencies
    verify_opencode_config "${project_root}"

    case "${mode}" in
        check)
            echo "=== Dry-Run Summary ==="
            ensure_state_dirs "${project_root}"
            install_systemd_units "${project_root}"
            ensure_gitignore_entries "${project_root}"
            install_notification_helper "${project_root}"
            echo ""
            echo "Prerequisites: ${PASS} passed, ${FAIL} failed, ${WARN} warnings"
            if [[ ${FAIL} -gt 0 ]]; then
                echo "Some prerequisites are missing. Install them before proceeding."
                exit 1
            fi
            echo "Ready to install. Run: $(basename "$0") --install"
            ;;
        install)
            echo "=== Installing Automation ==="
            ensure_state_dirs "${project_root}"
            install_systemd_units "${project_root}"
            ensure_gitignore_entries "${project_root}"
            install_notification_helper "${project_root}"
            echo ""
            echo "=== Installation Summary ==="
            echo "Prerequisites: ${PASS} passed, ${FAIL} failed, ${WARN} warnings"
            if [[ ${FAIL} -gt 0 ]]; then
                echo "Some prerequisites are missing. Install them before running services."
            fi
            echo ""
            echo "Next steps:"
            echo "  1. Ensure missing prerequisites are installed"
            echo "  2. Configure SSH alias 'ai-nas' if NAS access is needed"
            echo "  3. Run 'systemctl --user daemon-reload' to load new units"
            echo "  4. Start services: systemctl --user start opencode-worker opencode-supervisor"
            ;;
        uninstall)
            echo "=== Uninstalling Automation ==="
            local systemd_dir="${HOME}/.config/systemd/user"
            if [[ -d "${systemd_dir}" ]]; then
                for unit in opencode-worker opencode-supervisor opencode-watchdog; do
                    systemctl --user stop "${unit}.service" 2>/dev/null && log_pass "Stopped ${unit}.service" || true
                    systemctl --user disable "${unit}.service" 2>/dev/null && log_pass "Disabled ${unit}.service" || true
                    rm -f "${systemd_dir}/${unit}.service" "${systemd_dir}/${unit}.timer" && log_pass "Removed ${unit} units"
                done
                systemctl --user daemon-reload 2>/dev/null || true
            fi
            echo ""
            echo "=== Uninstall Complete ==="
            ;;
    esac
}

main "$@"
