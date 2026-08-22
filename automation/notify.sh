#!/usr/bin/env bash
# HF-0018 — Windows Notification Helper
# Sends desktop notifications, supporting WSL -> Windows via powershell.exe.
# Safe to call from systemd or cron — never blocks on missing display.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AI_ARCHIVE_ROOT:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
STATE_DIR="${REPO_ROOT}/.automation/state"

TITLE="${1:-AI Archive}"
MESSAGE="${2:-No message provided}"
LOG_FILE="${STATE_DIR}/notifications.log"

mkdir -p "${STATE_DIR}"

log_notification() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${TITLE}: ${MESSAGE}" >> "${LOG_FILE}"
}

send_windows_notification() {
    if command -v powershell.exe &>/dev/null; then
        powershell.exe -Command "
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null
            \$template = '<toast><visual><binding template=\"ToastText02\"><text id=\"1\">${TITLE}</text><text id=\"2\">${MESSAGE}</text></binding></visual></toast>'
            \$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            \$xml.LoadXml(\$template)
            \$toast = [Windows.UI.Notifications.ToastNotification]::new(\$xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('AI Archive Server').Show(\$toast)
        " 2>/dev/null && return 0
    fi

    if command -v notify-send &>/dev/null; then
        notify-send "${TITLE}" "${MESSAGE}" 2>/dev/null && return 0
    fi

    if command -v osascript &>/dev/null; then
        osascript -e "display notification \"${MESSAGE}\" with title \"${TITLE}\"" 2>/dev/null && return 0
    fi

    log_notification
    return 0
}

main() {
    log_notification
    send_windows_notification
}

main "$@"
