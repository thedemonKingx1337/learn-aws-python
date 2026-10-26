# Learning Progress

**Status as of 2026-10-27 (Tuesday):** Live on AWS — account `<redacted>`, region `ap-southeast-2`, IAM user `learning-cli`, key rotated after the plaintext leak. Chapter 1 runs green. SQL track written and verified against the live 172k-row retail_db, with the `postgres` MCP now connected and queryable. Nothing in the SQL material has been attempted yet.

Maintained by the `/update-progress` command. Levels mean exactly what they say:

- **Practised** — wrote, ran, broke or debugged it unaided
- **Walked through** — Claude built or explained it, read along, not yet done solo

---

## Covered so far

| Topic | Level | Where | Date | Specifics |
|---|---|---|---|---|
| Python environment management | Walked through | — | 2026-10-25 | `pyenv local`, why a bare `python` resolved to the wrong interpreter (PATH precedence), building a `.venv` from a pinned pyenv version, `python -m pip` vs `pip` and why `-m` matters on Windows |
| boto3 clients & sessions | Walked through | [chapter1.py](chapter1.py) | 2026-10-25 | `boto3.client()` makes no network call; the client class is generated at runtime from botocore's JSON model; `boto3.Session()` owns identity, clients are made from it |
| The credential chain | Walked through | [chapter1.py](chapter1.py) | 2026-10-25 | All 5 steps in order, "first one wins", `session.get_credentials()` and reading `credentials.method` to see which link supplied the keys |
| Reading AWS errors | Walked through | [chapter1.py](chapter1.py) | 2026-10-25 | `NoCredentialsError` (local, nothing sent) vs `ClientError` (remote, AWS refused); `InvalidClientTokenId` vs `SignatureDoesNotMatch` |
| Windows shells & process environment | **Practised** | - | 2026-10-27 | Why a running process never sees a newly-set PATH or env var (it reads them once, at startup); `%VAR%` vs `$env:VAR` vs `$VAR` across cmd / PowerShell / Git Bash; MSYS path conversion silently rewriting `cmd /c` to `cmd C:/`; and why a first-run `npx`/`uvx` download exceeds a 30s startup timeout. All learned by debugging one MCP server through five distinct failures. |
| IAM user, access keys & CLI config | **Practised** | console + terminal | 2026-10-26 | Created a scoped IAM user (`ReadOnlyAccess` + `AmazonS3FullAccess`), generated a CLI access key, ran `aws configure`, and read the `LOCATION` column of `aws configure list` to confirm which file supplied each value. Learned User vs Role: roles have no access keys because something must assume them. |
| `sts:GetCallerIdentity` | Walked through | [chapter1.py](chapter1.py) | 2026-10-25 | The "whoami" of AWS — free, needs no IAM permission, the right first call to prove a setup works |

---

## Next up

1. **Set a budget alarm.** Still the only urgent item. $100 of credits makes overspend invisible until they are gone — nothing errors, the balance just drains. Billing -> Budgets -> zero-spend or $5 monthly alert.
2. **Work [sql/01_execution_order.md](sql/01_execution_order.md).** Everything else in the SQL track is a consequence of it, and the `postgres` MCP is now connected so queries can be checked instantly. 23 questions are written and unanswered.
3. **Chapter 2 - S3.** `AmazonS3FullAccess` is already attached, so writes will work. Buckets, `put_object` / `get_object`, paginators, and why `list_objects_v2` truncates at 1000.
4. **Chapter 3 - IAM in depth.** Once S3 gives something to grant access *to*, policies and `AssumeRole` stop being abstract. User vs Role is already half-learned from creating `learning-cli`.

## Roadmap

Proposed order — reorder freely. Grouped so each tier unlocks the next.

**SQL** (local PostgreSQL 18, material ready in [sql/](sql/))
- [ ] Execution order - the clause pipeline and the four rules that follow
- [ ] DISTINCT - whole-row semantics, NULL handling, `DISTINCT ON`
- [ ] Window functions - RANK family, frames, LAG/LEAD, the NULLS FIRST trap
- [ ] CTEs - multiple, chained and recursive

**Foundations**
- [ ] IAM — users, access keys, policies, roles, `AssumeRole`
- [ ] S3 — objects, prefixes, paginators, presigned URLs
- [ ] CloudWatch Logs — how to see what anything did

**Compute**
- [ ] Lambda — `invoke()`, payloads, cold starts, env vars, layers
- [ ] API Gateway + Lambda — turning a function into an HTTP endpoint
- [ ] EC2 — launch, describe, tags, instance lifecycle, teardown discipline
- [ ] ECR — pushing a container image
- [ ] ECS / Fargate — task definitions, services, running a container without a server

**Data**
- [ ] DynamoDB — tables, partition vs sort key, `query` vs `scan`
- [ ] Glue Data Catalog — crawlers, databases, tables
- [ ] Glue ETL jobs — PySpark on AWS, `DynamicFrame` vs Spark `DataFrame`
- [ ] Athena — querying S3 with SQL

**Glue it together**
- [ ] SQS / SNS — queues, topics, fan-out
- [ ] Step Functions — orchestrating the above
- [ ] VPC basics — subnets, security groups, why a Lambda loses internet in a VPC
- [ ] IaC — CloudFormation or CDK

---

## Blocked / open questions

- **No budget alarm configured.** Free-plan credits hide overspend entirely.
- **Prior Glue experience unknown.** KeePass holds older IAM users labelled "for glue trial" and "aws glue demo study", suggesting earlier hands-on work with Glue. If so the Glue chapters should start further along. Asked twice, still unanswered.
- **Old access key deletion unconfirmed.** The local credentials file now holds a new key (`...COHR`, not the leaked `...LDVS`), so rotation happened — but whether the old key was *deleted* in IAM rather than just deactivated has not been verified.

Resolved 2026-10-26: AWS account confirmed, credentials configured, region settled, real AWS chosen over LocalStack. Resolved 2026-10-27: leaked key rotated; `postgres` MCP connected.

## Worth revisiting

- Everything in `chapter1.py` is **walked through, not practised.** Re-type it from scratch without looking to promote it.
- **Credential hygiene.** The secret access key was pasted in plaintext on 2026-10-26. The rule: the Access Key ID (`AKIA...`) is an identifier and safe to share; the Secret Access Key is typed only into the `aws configure` prompt and nowhere else. To show someone your setup, send `aws sts get-caller-identity` output, never the configure transcript.
- **The whole SQL track is unpractised.** 4 lessons and 23 questions in [sql/](sql/) were written and verified by Claude, not worked by the author. None of it counts as covered until the questions are attempted without looking at [sql/solutions.md](sql/solutions.md).
- The PATH precedence problem (standalone Python 3.12.4 beating pyenv's shims) was diagnosed by Claude, not the author. Worth being able to run `pyenv which python` and read `$PATH` unaided — it will recur on every new machine.

---

## Session log

- **2026-10-25** — Set up the project from an empty folder: pyenv 3.12.6 + `.venv`, boto3, `.gitignore`, README index, and a `docs/` rule system with a thin `CLAUDE.md` index. Wrote and ran `chapter1.py`. Detoured into why the VS Code dev container feature list looked different from a YouTube tutorial (answer: that video was in GitHub Codespaces, and the AWS CLI entry is a *Feature*, shown one step later than the *Template* picker). No AWS account touched.
- **2026-10-26** — Tooling, not AWS: installed `uv`/`uvx` (winget) and registered the **aws-docs MCP server** in `.mcp.json` at project scope, so AWS documentation can be looked up live instead of from recall. Still no AWS account touched. Incidental lessons: a running shell holds a stale `PATH` copy and cannot see a just-installed tool until restarted; `uvx` runs a tool in a throwaway environment so it never pollutes `.venv`; and the sandbox blocks auto-executing packages fetched from PyPI, so the first `uvx` launch must be approved interactively.
- **2026-10-26 (later)** — Went live on AWS. Created IAM user `learning-cli` with `ReadOnlyAccess` + `AmazonS3FullAccess` (after starting in the wrong wizard — Roles instead of Users — which taught the User vs Role split), generated CLI keys, stored them in KeePass, ran `aws configure`, and watched `chapter1.py` flip from `NONE FOUND` to a real account and ARN with no code change. Also learned why this account has no root "Security credentials" page: it is AWS's new project-scoped Free Plan, not a classic account. Marred by pasting the secret key in plaintext — rotation pending.
- **2026-10-27** — Added a SQL track. Found an existing fully populated **retail_db** in local PostgreSQL 18 (172,198 order_items / 68,883 orders / 12,435 customers) and built the course on it rather than inventing toy data; added a small `practice` schema only for what retail_db cannot show - a manager hierarchy, deliberate salary ties, a NULL salary, and a gap in a date series. Wrote 4 lessons + 23 verified solutions. Registered a `postgres` MCP server; after two wrong turns (local scope made it invisible in the VS Code MCP panel, and a missing `@latest` resolved a stale 0.1.0 that rejects `--access-mode`) it now sits in the committed `.mcp.json` reading `${PG_LEARN_URI}` from a user environment variable, so the password is in neither file. Still needs its first `uvx` download before it will start. `aws-mcp` connected; `aws-docs` pending approval. Nothing in the SQL material is practised yet - it was written, not learned.
- **2026-10-27 (later)** — Got the `postgres` MCP server connected after five separate failures, each a different cause: a missing `@latest` resolving a stale 0.1.0 that rejected `--access-mode`; `local` scope making the server invisible in the VS Code MCP panel; a new env var never reaching the already-running VS Code process; Git Bash rewriting `cmd /c` into `cmd C:/` via MSYS path conversion; and a first-run package download exceeding the 30s startup timeout. Settled on the **npm** `@modelcontextprotocol/server-postgres` at **user** scope reading `${POSTGRES_CONNECTION_STRING}` - the same server and variable the `insurance-etl-platform` project already used successfully, which should have been the starting point rather than the destination.
- **2026-10-27 (end)** — Little new learning; mostly finishing what was already started. Confirmed the leaked AWS key had been rotated. Got the `postgres` MCP fully working and ran the first query through it (the RANK vs DENSE_RANK example), matching the lesson's verified table. The author caught a real defect Claude missed: the execution-order figure rendered as collapsed garbage because it was not inside a fenced code block — Markdown reflows unfenced text in a proportional font. Fixed, scanned every `.md` for the same mistake, and added the rule plus a scanner to `docs/note-writing-rules.md`.
