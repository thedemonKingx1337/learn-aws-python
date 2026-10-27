# Tools and environment progress

How this file is used, including re-teaching: [docs/progress-tracking-rules.md](../docs/progress-tracking-rules.md).

## Topics

| Topic | Status | Where | First covered |
|---|---|---|---|
| Python environments: pyenv, venv, PATH precedence, `python -m pip` | Walked through | [environment-setup.md](../docs/aws/environment-setup.md) | 2026-10-25 |
| Windows shells and the process environment | Walked through | - | 2026-10-27 |
| MCP servers: scopes, env-var placeholders, first-run downloads | Walked through | [.mcp.json](../.mcp.json) | 2026-10-26 |
| Git and GitHub: commit, push, public-repo safety | Practised | - | 2026-10-27 |
| Claude Code: `CLAUDE.md` as an index, rules in `docs/`, custom commands | Walked through | [CLAUDE.md](../CLAUDE.md) | 2026-10-25 |
| VS Code dev containers vs GitHub Codespaces | Mentioned | - | 2026-10-25 |

## Re-teach notes

### Python environments: pyenv, venv, PATH precedence, `python -m pip`
- **Idea:** a bare `python` here is a standalone 3.12.4 that sits ahead of pyenv's shims on PATH. The project pins 3.12.6 with `pyenv local`, builds `.venv` by calling that interpreter by its full path, and runs inside `.venv`. `python -m pip` guarantees pip belongs to that interpreter, and on Windows it is the form that can upgrade pip itself.
- **Shaky:** Claude diagnosed the PATH order, not the author. Practise `pyenv which python` and reading `$PATH` unaided; it recurs on every new machine.
- **Check:** how do you prove which interpreter is actually running?

### Windows shells and the process environment
- **Idea:** a process reads PATH and environment variables once, at startup, so a terminal or VS Code that is already running never sees a variable set afterwards; restart it. Variables are `%VAR%` in cmd, `$env:VAR` in PowerShell and `$VAR` in Git Bash. Git Bash rewrites anything shaped like `/c` into `C:/` (MSYS path conversion); `MSYS_NO_PATHCONV=1` stops it.
- **Did:** ran the `uvx` and `npx` warm-up commands in cmd, and hit the cmd-vs-PowerShell mistake (`$env:VAR` typed in cmd). Claude diagnosed the stale variable and the MSYS path problem.
- **Check:** you set an environment variable and VS Code still says it is missing. Why, and what fixes it?

### MCP servers: scopes, env-var placeholders, first-run downloads
- **Idea:** `project` scope writes `.mcp.json` in the repo (committed); `user` scope writes `~/.claude.json` and applies to every project; `local` scope also writes `~/.claude.json` but only for this project, and does not show in the VS Code MCP panel. Keep secrets in an environment variable and reference it as `${VAR}`. A server's first `uvx` or `npx` launch downloads the package and can exceed the 30-second startup timeout, so run it once by hand.
- **Good reasoning by the author:** proposed the environment-variable approach, and argued the postgres server belongs at user scope because every project uses the same local database.
- **Check:** why is the postgres server not in `.mcp.json`?

### Git and GitHub: commit, push, public-repo safety
- **Idea:** git history is permanent, so secrets (keys, passwords, account IDs) must be removed before the first commit, not after. `.gitignore` keeps `.venv` and credential files out. `git mv` records a move instead of a delete plus an add.
- **Did:** committed and pushed a change from VS Code themselves (commit `3df6009`).
- **Check:** you committed a password, then deleted the line in the next commit. Is it gone?

### Claude Code: `CLAUDE.md` as an index, rules in `docs/`, custom commands
- **Idea:** `CLAUDE.md` loads into every session, so it stays short and points to `docs/` files that are read only when relevant. `.claude/commands/` holds slash commands such as `/update-progress`. Loose files elsewhere in `.claude/` are not read automatically.
- **Check:** where would a new rule about the Lambda chapters go?

### VS Code dev containers vs GitHub Codespaces
- **Idea:** the tutorial's AWS CLI option is a dev container *Feature*, offered after picking a *Template*, and the video was running in GitHub Codespaces. Not needed here: the AWS CLI and Python run natively.
