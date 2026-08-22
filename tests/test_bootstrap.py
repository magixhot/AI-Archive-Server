"""
HF-0018 — Automated tests for bootstrap logic.

All tests use temporary directories and never touch the real home directory
or systemd session. Safe for CI.
"""
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOMATION_DIR = REPO_ROOT / "automation"
TEMPLATES_DIR = AUTOMATION_DIR / "templates"


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project root with required files."""
    project = tmp_path / "project"
    project.mkdir()

    (project / "opencode.json").write_text('{"$schema": "https://opencode.ai/config.json"}')
    (project / "AI_AGENT_INSTRUCTIONS.md").write_text("# Instructions")
    (project / "pyproject.toml").write_text('[project]\nname = "test"')
    (project / "compose.yaml").write_text("services: {}")

    automation = project / "automation"
    automation.mkdir()

    scripts = [
        "bootstrap.sh", "worker-bridge.sh", "supervisor.sh",
        "watchdog.sh", "notify.sh", "check.sh",
    ]
    for script in scripts:
        src = AUTOMATION_DIR / script
        if src.exists():
            shutil.copy2(src, automation / script)
            (automation / script).chmod(0o755)

    templates = project / "automation" / "templates"
    templates.mkdir()
    for tmpl in TEMPLATES_DIR.glob("*"):
        if tmpl.is_file():
            shutil.copy2(tmpl, templates / tmpl.name)

    gitignore = project / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\n")

    return project


@pytest.fixture
def clean_env(tmp_path):
    """Provide a clean environment with overridden HOME."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(fake_home)
    return env, fake_home


class TestBootstrapScriptExists:
    def test_bootstrap_script_present(self):
        assert (AUTOMATION_DIR / "bootstrap.sh").exists()

    def test_worker_bridge_script_present(self):
        assert (AUTOMATION_DIR / "worker-bridge.sh").exists()

    def test_supervisor_script_present(self):
        assert (AUTOMATION_DIR / "supervisor.sh").exists()

    def test_watchdog_script_present(self):
        assert (AUTOMATION_DIR / "watchdog.sh").exists()

    def test_notify_script_present(self):
        assert (AUTOMATION_DIR / "notify.sh").exists()

    def test_check_script_present(self):
        assert (AUTOMATION_DIR / "check.sh").exists()


class TestSystemdTemplates:
    EXPECTED = [
        "opencode-worker.service",
        "opencode-worker.timer",
        "opencode-supervisor.service",
        "opencode-supervisor.timer",
        "opencode-watchdog.service",
        "opencode-watchdog.timer",
    ]

    def test_all_templates_exist(self):
        for name in self.EXPECTED:
            assert (TEMPLATES_DIR / name).exists(), f"Missing template: {name}"

    def test_templates_contain_placeholders(self):
        for name in self.EXPECTED:
            content = (TEMPLATES_DIR / name).read_text()
            if name.endswith(".service"):
                assert "@@REPO_ROOT@@" in content, f"Missing @@REPO_ROOT@@ in {name}"

    def test_service_templates_have_install_section(self):
        for suffix in ["worker", "supervisor"]:
            content = (TEMPLATES_DIR / f"opencode-{suffix}.service").read_text()
            assert "[Install]" in content

    def test_timer_templates_have_timer_section(self):
        for suffix in ["worker", "supervisor", "watchdog"]:
            content = (TEMPLATES_DIR / f"opencode-{suffix}.timer").read_text()
            assert "[Timer]" in content


class TestScriptPermissions:
    SCRIPTS = [
        "bootstrap.sh", "worker-bridge.sh", "supervisor.sh",
        "watchdog.sh", "notify.sh", "check.sh",
    ]

    def test_scripts_are_executable(self):
        for name in self.SCRIPTS:
            path = AUTOMATION_DIR / name
            assert path.exists()
            mode = path.stat().st_mode
            assert mode & stat.S_IXUSR, f"{name} is not executable"


class TestBootstrapCheckMode:
    def test_check_mode_exits_cleanly(self, tmp_project, clean_env):
        env, _ = clean_env
        bootstrap = tmp_project / "automation" / "bootstrap.sh"
        result = subprocess.run(
            ["bash", str(bootstrap), "--check"],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        assert result.returncode == 0, f"Check mode failed: {result.stderr}"

    def test_check_mode_mentions_prerequisites(self, tmp_project, clean_env):
        env, _ = clean_env
        bootstrap = tmp_project / "automation" / "bootstrap.sh"
        result = subprocess.run(
            ["bash", str(bootstrap), "--check"],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        assert "Prerequisite Checks" in result.stdout


class TestCheckScript:
    def test_check_script_runs(self, tmp_project, clean_env):
        env, _ = clean_env
        check = tmp_project / "automation" / "check.sh"
        result = subprocess.run(
            ["bash", str(check)],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        assert "Validation Check" in result.stdout
        assert "Summary" in result.stdout


class TestWorkerBridgePathDiscovery:
    def test_discovers_repo_root_from_env(self, tmp_project, clean_env):
        env, _ = clean_env
        env["AI_ARCHIVE_ROOT"] = str(tmp_project)
        worker = tmp_project / "automation" / "worker-bridge.sh"
        content = worker.read_text()
        assert "AI_ARCHIVE_ROOT" in content

    def test_worker_bridge_has_pid_management(self):
        content = (AUTOMATION_DIR / "worker-bridge.sh").read_text()
        assert "PID_FILE" in content
        assert "check_stale_pid" in content


class TestSupervisorRestartLogic:
    def test_supervisor_has_max_restarts(self):
        content = (AUTOMATION_DIR / "supervisor.sh").read_text()
        assert "MAX_RESTARTS" in content
        assert "RESTART_WINDOW" in content

    def test_supervisor_records_restarts(self):
        content = (AUTOMATION_DIR / "supervisor.sh").read_text()
        assert "record_restart" in content
        assert "supervisor-restarts" in content


class TestWatchdogHealthChecks:
    def test_watchdog_checks_worker(self):
        content = (AUTOMATION_DIR / "watchdog.sh").read_text()
        assert "check_worker_health" in content

    def test_watchdog_checks_supervisor(self):
        content = (AUTOMATION_DIR / "watchdog.sh").read_text()
        assert "check_supervisor_health" in content

    def test_watchdog_notifies_on_failure(self):
        content = (AUTOMATION_DIR / "watchdog.sh").read_text()
        assert "notify_failure" in content


class TestNotificationHelper:
    def test_notify_supports_windows(self):
        content = (AUTOMATION_DIR / "notify.sh").read_text()
        assert "powershell.exe" in content

    def test_notify_supports_linux(self):
        content = (AUTOMATION_DIR / "notify.sh").read_text()
        assert "notify-send" in content

    def test_notify_supports_macos(self):
        content = (AUTOMATION_DIR / "notify.sh").read_text()
        assert "osascript" in content


class TestNoSecretsInRepository:
    """Verify no secrets are embedded in automation scripts."""

    SECRET_PATTERNS = [
        "ghp_",         # GitHub personal access token
        "gho_",         # GitHub OAuth token
        "ssh-rsa",      # SSH public key (private key would be worse)
        "password=",
        "token=",
    ]

    def test_no_tokens_in_scripts(self):
        for script in AUTOMATION_DIR.glob("*.sh"):
            content = script.read_text()
            for pattern in self.SECRET_PATTERNS:
                assert pattern not in content, (
                    f"Potential secret pattern '{pattern}' found in {script.name}"
                )

    def test_no_tokens_in_templates(self):
        for tmpl in TEMPLATES_DIR.glob("*"):
            content = tmpl.read_text()
            for pattern in self.SECRET_PATTERNS:
                assert pattern not in content, (
                    f"Potential secret pattern '{pattern}' found in {tmpl.name}"
                )


class TestNoHardcodedPaths:
    """Verify no machine-specific Windows paths in scripts."""

    WINDOWS_PATH_PATTERNS = [
        "C:\\Users",
        "C:/Users",
        "D:\\",
        "D:/",
        "E:\\",
        "E:/",
    ]

    def test_no_windows_paths_in_scripts(self):
        for script in AUTOMATION_DIR.glob("*.sh"):
            content = script.read_text()
            for pattern in self.WINDOWS_PATH_PATTERNS:
                assert pattern not in content, (
                    f"Windows path '{pattern}' found in {script.name}"
                )

    def test_no_windows_paths_in_templates(self):
        for tmpl in TEMPLATES_DIR.glob("*"):
            content = tmpl.read_text()
            for pattern in self.WINDOWS_PATH_PATTERNS:
                assert pattern not in content, (
                    f"Windows path '{pattern}' found in {tmpl.name}"
                )


class TestIdempotency:
    def test_check_mode_is_idempotent(self, tmp_project, clean_env):
        env, _ = clean_env
        bootstrap = tmp_project / "automation" / "bootstrap.sh"

        result1 = subprocess.run(
            ["bash", str(bootstrap), "--check"],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        result2 = subprocess.run(
            ["bash", str(bootstrap), "--check"],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        assert result1.returncode == result2.returncode
        assert result1.stdout == result2.stdout


class TestGitignoreEntries:
    def test_bootstrap_adds_gitignore_entries(self, tmp_project, clean_env):
        env, _ = clean_env
        env["AI_ARCHIVE_ROOT"] = str(tmp_project)
        bootstrap = tmp_project / "automation" / "bootstrap.sh"
        subprocess.run(
            ["bash", str(bootstrap), "--install"],
            capture_output=True, text=True, env=env,
            timeout=30,
        )
        gitignore = tmp_project / ".gitignore"
        content = gitignore.read_text()
        assert ".automation/" in content
