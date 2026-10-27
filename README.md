# Learn AWS with Python 🐍☁️

A hands-on course for learning **AWS and Python together** — `boto3`, AWS Glue, EC2, Lambda and the services around them — written as plain, runnable Python modules rather than notebooks. Each chapter stands on its own: open any `aws/chapterN.py`, read it top to bottom, and run it.

## 📖 Table of Contents

| Chapter | Module | What You Will Learn |
|---------|--------|---------------------|
| 1 | [Chapter 1 — boto3 Clients, Sessions & the Credential Chain](aws/chapter1.py) | What `boto3.client()` actually builds — a local object holding a region, an endpoint and your keys, with **no network call made** — and why that means a bad region fails later rather than immediately. Why the client's type is a class generated at runtime from botocore's JSON service model (hence no editor autocomplete). `boto3.Session()` and `session.get_credentials()`, with `credentials.method` naming **which link of the chain supplied the keys**. The five-step credential chain in order — inline keys → environment variables → `~/.aws/credentials` → `~/.aws/config` → EC2/ECS/Lambda instance metadata — and the "first one wins" rule that explains nearly every credential bug. Then `sts:GetCallerIdentity` as the "whoami" of AWS (free, needs no IAM permission), and why `NoCredentialsError` (local problem, nothing was sent) must be caught separately from `ClientError` (remote problem, AWS said no). Closes with `client` vs `resource` and why you should learn `client`. |

## 🛠️ Setup & Extras

| Resource | Description |
|----------|-------------|
| [requirements.txt](requirements.txt) | Python dependencies — currently `boto3` only. Installed into `.venv`, which is built from **pyenv-win 3.12.6**. The AWS CLI is not listed: it is a standalone Windows binary, not a pip package. |
| [.gitignore](.gitignore) | Ignores `__pycache__/`, editor folders, `data/`, and anything credential-shaped (`.aws/`, `credentials`, `*.pem`). |
| [.mcp.json](.mcp.json) | Project-scoped MCP servers, safe to commit - currently just **`aws-docs`** (official AWS documentation, read-only, no credentials). The **`postgres`** server used by [sql/](sql/) is deliberately **user-scoped** (`~/.claude.json`) because one local PostgreSQL serves every project on this machine. It runs the npm `@modelcontextprotocol/server-postgres` and reads `${POSTGRES_CONNECTION_STRING}` from a user environment variable, so no password exists in any config file. |
| [sql/](sql/) | **SQL practice** - execution order, joins, DISTINCT, window functions and CTEs (multiple + recursive), worked against the live PostgreSQL 18 retail_db (172k order_items) plus a small `practice` schema built for ties, NULLs, hierarchies and date gaps. 30 questions with verified solutions. |
| [PROGRESS.md](PROGRESS.md) + [progress/](progress/) | The learning tracker. `PROGRESS.md` is the dashboard: how far each subject has got, what to revise first, what is next, what is blocked, and a dated session log. `progress/` has one file per subject (AWS, SQL, tools) listing every topic with its status and short re-teach notes, so a topic studied earlier can be taught again from what worked. Updated by the `/update-progress` command. |
| [CLAUDE.md](CLAUDE.md) | Short index of the working rules for this repo. Deliberately thin — it loads into context every session, so the detail lives in `docs/`. |
| [docs/](docs/) | The rules themselves, read on demand. **General:** `teaching-rules.md` (narrate every command, explain the reasoning, Malayalam on request), `teaching-style-rules.md` (beginner start, advanced finish), `repository-guide.md` (layout and code style), `note-writing-rules.md` (where notes go, ASCII figure limits), `readme-index-rules.md` (keep this table in sync). **By subject:** `aws/` (`environment-setup.md` for pyenv/venv and the PATH trap, `aws-safety-rules.md` for confirm-before-spending and region), `sql/` (`sql-rules.md`). |

## ▶️ How to Use

```powershell
pyenv local 3.12.6
& "$env:USERPROFILE\.pyenv\pyenv-win\versions\3.12.6\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python aws/chapter1.py
```

After the first time, you only need:

```powershell
.\.venv\Scripts\Activate.ps1
python aws/chapter1.py
```

> A bare `python` on this machine resolves to a standalone Python 3.12.4, **not** the pyenv
> version and not the venv — so activate first, or call `.venv\Scripts\python.exe` directly.

Chapter 1 runs safely **with or without** an AWS account — it reports a missing credential chain in plain English instead of crashing.

To make real AWS calls in later chapters, configure credentials once:

```powershell
aws configure
```

Then set your region in each chapter's `REGION` constant (Chapter 1 defaults to `ap-south-1`).

---

*This index is kept in sync with the modules — every new chapter added to the repo gets analyzed and listed here. See [CLAUDE.md](CLAUDE.md) for the maintenance rule.*
