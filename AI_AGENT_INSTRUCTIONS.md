# AI_AGENT_INSTRUCTIONS.md

# AI Archive Server — Local Agent Operating Rules

## 1. Initialization

Before any engineering work:

1. Read:
   - docs/06_Project_Documentation/AI_CHAT_START.md
2. Follow its required documentation order.
3. Treat CURRENT_STATUS.md as the single source of current project state.
4. Work only within the active HF milestone.

## 2. Agent Responsibilities

The local agent should perform routine engineering work directly:

- inspect project documentation and code;
- make scoped code changes;
- create or update tests;
- run focused tests;
- run broader tests when shared behavior changes;
- run `git diff --check`;
- review `git diff`;
- inspect `git status --short`;
- create safe commits;
- perform normal fast-forward push after successful checks;
- use NAS runtime through SSH when Docker integration testing is required.

The human should not be used as a command relay.

## 3. NAS Runtime Access

Preferred SSH alias:

    ai-nas

Runtime repository:

    /volume3/AI_Infrastructure/01_Runtime/AI-Archive-Server

Docker Compose is authoritative.

For Docker commands on NAS use:

    sudo -n /var/packages/ContainerManager/target/usr/bin/docker compose ...

Container Manager is for observation only.

Do not change runtime configuration through Container Manager GUI.

## 4. Git Rules

Allowed without extra confirmation:

- git status
- git diff
- git diff --check
- git log
- git pull --ff-only
- git add scoped files
- git commit
- normal git push

Require explicit human confirmation before:

- force push
- reset --hard
- rewriting published history
- rebase of published commits
- deleting branches
- deleting tags
- deleting backups
- destructive cleanup of NAS runtime data
- destructive Registry operations
- unrelated tracked-file deletion

## 5. Safety Rules

Never:

- expose passwords, tokens, private SSH keys, or secrets;
- modify unrelated files;
- introduce machine-specific Windows absolute paths into project code;
- silently delete partial downloads;
- silently delete Registry data;
- change architecture without necessity;
- mark data VALIDATED unless validation actually occurred;
- perform destructive NAS operations without confirmation.

Preserve originals.
Automate everything.
Extend, never replace.

## 6. Path Rules

Project code must use portable computed paths.

Do not hard-code paths such as:

    C:\Users\...
    D:\OneDrive\...
    E:\Projects\...

Machine-specific absolute paths are allowed only in intentionally platform-bound deployment configuration already approved by project architecture.

## 7. Testing Rules

Before commit:

1. Run the most focused relevant tests.
2. Run broader tests if shared behavior changed.
3. Run:

    git diff --check

4. Review:

    git diff

5. Confirm:

    git status --short

If Docker runtime behavior is affected, verify through NAS Docker Compose.

## 8. HF Discipline

Do not broaden the active HF scope.

If technical debt is discovered outside the active HF:

- report it;
- do not fix it unless required for the active task.

Do not invent a new HF without documentation approval.

## 9. Reporting Format

After each completed task, return exactly:

TASK
- What was requested.

RESULT
- PASS / PARTIAL / BLOCKED
- Short outcome.

CHANGED FILES
- List changed files.

TESTS
- Commands run.
- Results.

GIT STATUS
- Clean / dirty.
- Untracked files if any.

COMMIT
- Commit SHA and message, or "not committed".

CI
- Result if pushed.
- Otherwise "not run".

NAS RUNTIME
- Runtime checks performed and result.
- Otherwise "not required".

RISKS / TECHNICAL DEBT
- Remaining issues.
- "None" if none.

NEXT RECOMMENDED STEP
- One concrete next step only.

End of Document
