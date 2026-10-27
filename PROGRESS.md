# Learning Progress

**Status as of 2026-10-27 (Tuesday):** Learning AWS through the console, in `ap-southeast-2` as the IAM user `learning-cli`; the code chapters in `aws/` exist but have not been studied yet. The Udemy Glue course files are adapted to this account in `Glue-MasterClass/` but not uploaded yet (`bucket101pb` is still empty); `role101` still needs the KMS key before any Glue job can run. The SQL track has five lessons; 0 of the 30 questions answered.

This is the dashboard. Each subject has its own file in [progress/](progress/) that lists every topic, covered or not, with short re-teach notes for the covered ones. How these files are used, including re-teaching a topic studied before: [docs/progress-tracking-rules.md](docs/progress-tracking-rules.md). Updated by the `/update-progress` command.

---

## At a glance

| Subject | Practised | Walked through | Mentioned | Unknown | Not started | Detail |
|---|---|---|---|---|---|---|
| AWS | 4 | 4 | 5 | 2 | 18 | [progress/aws.md](progress/aws.md) |
| SQL | 1 | 3 | 1 | 0 | 3 | [progress/sql.md](progress/sql.md) |
| Tools & environment | 1 | 4 | 1 | 0 | 0 | [progress/tools.md](progress/tools.md) |

SQL questions answered: **0 / 30**.

**Practised**: did it unaided. **Walked through**: Claude explained or built it while the author read along. **Mentioned**: came up in passing, not covered. **Unknown**: studied in the Udemy Glue course, depth not yet known. **Not started**: on the roadmap.

## Revise first

Topics the author found hard or asked about more than once. The detail is in the subject files.

- **SQL: the GROUP BY family of errors.** An alias in `HAVING`, `count(*)` in `WHERE`, and `SELECT *` with `GROUP BY` were asked as three questions; they are one idea. [progress/sql.md](progress/sql.md)
- **SQL: rank gaps and NULLS FIRST.** Expected 4, 4, 5 from `rank()`. [progress/sql.md](progress/sql.md)
- **AWS: copying a role ARN from an error message.** The error drops the role's path, and it locked the console out once. [progress/aws.md](progress/aws.md)
- **Tools: reading PATH unaided.** The wrong-interpreter problem was diagnosed by Claude, not the author. [progress/tools.md](progress/tools.md)

---

## Next up

1. **Set a budget alarm.** Still the only urgent item. $100 of credits makes overspend invisible until they are gone - nothing errors, the balance just drains. Billing -> Budgets -> zero-spend or $5 monthly alert.
2. **Get `bucket101pb` ready for the Glue labs.** The author chose to reuse it, with prefixes in place of the course's four buckets. First reload `bucket101pb` -> Permissions to confirm the corrected policy lets the console in; then give `role101` the KMS key, create the database `database101`, and upload the course files, following [Glue-MasterClass/README.md](Glue-MasterClass/README.md). Without the KMS step every Glue job fails before it starts.
3. **Work the SQL questions, lesson 1 first.** 30 questions across [sql/](sql/), answered before opening [sql/solutions.md](sql/solutions.md). Joins is lesson 5 but read it second.
4. **When moving to code, start with `aws/chapter1.py`.** Its four topics are only Mentioned, because the author has been learning through the console. Read it, run it and re-type it, then Chapter 2 (S3 with `boto3`) on a separate practice bucket: `bucket101pb` is a poor fit, being KMS-encrypted and restricted to a short exemption list.

## Blocked / open questions

- **No budget alarm configured.** Free-plan credits hide overspend entirely.
- **Glue: partly answered.** The author is working through a Udemy course, *AWS Glue: The Complete Masterclass*, and was at the GlueJob2 assignment on 2026-10-27 (create an SSE-KMS encrypted S3 source bucket with a deny bucket policy, using a KMS key made in an earlier lecture). Confirmed: the earlier work lives in this account (bucket `bucket101pb`, KMS key `alias/s3101-KMS`, IAM users `user101` and `demouser101`, Glue role `role101`). Still unknown: how many lectures are done.
- **Old access key deletion unconfirmed.** The local credentials file now holds a new key (`...COHR`, not the leaked `...LDVS`), so rotation happened — but whether the old key was *deleted* in IAM rather than just deactivated has not been verified.
- **Region constraint (inferred).** The account is governed by an AWS Organizations service control policy that explicitly denies KMS calls in every enabled region except `ap-southeast-2`, `us-east-1` and `us-west-2`. Stay in `ap-southeast-2`. Other services were not tested.
- **Kinesis is denied by the SCP** in every region tested (ap-southeast-2, us-east-1, us-west-2), so the Udemy course's streaming lab (`gluejob345`) can't run in this account.
- **Unused admin access keys.** `user101` (AdministratorAccess) and `demouser101` each have an active access key that has never been used. Deactivate both once the Glue course no longer needs them.

Resolved 2026-10-26: AWS account confirmed, credentials configured, region settled, real AWS chosen over LocalStack. Resolved 2026-10-27: leaked key rotated; `postgres` MCP connected; `bucket101pb` lock-out recovered and a corrected policy applied; GlueJob2 bucket settled (reuse `bucket101pb` with prefixes).

---

## Session log

- **2026-10-25** — Set up the project from an empty folder: pyenv 3.12.6 + `.venv`, boto3, `.gitignore`, README index, and a `docs/` rule system with a thin `CLAUDE.md` index. Wrote and ran `chapter1.py`. Detoured into why the VS Code dev container feature list looked different from a YouTube tutorial (answer: that video was in GitHub Codespaces, and the AWS CLI entry is a *Feature*, shown one step later than the *Template* picker). No AWS account touched.
- **2026-10-26** — Tooling, not AWS: installed `uv`/`uvx` (winget) and registered the **aws-docs MCP server** in `.mcp.json` at project scope, so AWS documentation can be looked up live instead of from recall. Still no AWS account touched. Incidental lessons: a running shell holds a stale `PATH` copy and cannot see a just-installed tool until restarted; `uvx` runs a tool in a throwaway environment so it never pollutes `.venv`; and the sandbox blocks auto-executing packages fetched from PyPI, so the first `uvx` launch must be approved interactively.
- **2026-10-26 (later)** — Went live on AWS. Created IAM user `learning-cli` with `ReadOnlyAccess` + `AmazonS3FullAccess` (after starting in the wrong wizard — Roles instead of Users — which taught the User vs Role split), generated CLI keys, stored them in KeePass, ran `aws configure`, and watched `chapter1.py` flip from `NONE FOUND` to a real account and ARN with no code change. Also learned why this account has no root "Security credentials" page: it is AWS's new project-scoped Free Plan, not a classic account. Marred by pasting the secret key in plaintext — rotation pending.
- **2026-10-27** — Added a SQL track. Found an existing fully populated **retail_db** in local PostgreSQL 18 (172,198 order_items / 68,883 orders / 12,435 customers) and built the course on it rather than inventing toy data; added a small `practice` schema only for what retail_db cannot show - a manager hierarchy, deliberate salary ties, a NULL salary, and a gap in a date series. Wrote 4 lessons + 23 verified solutions. Registered a `postgres` MCP server; after two wrong turns (local scope made it invisible in the VS Code MCP panel, and a missing `@latest` resolved a stale 0.1.0 that rejects `--access-mode`) it now sits in the committed `.mcp.json` reading `${PG_LEARN_URI}` from a user environment variable, so the password is in neither file. Still needs its first `uvx` download before it will start. `aws-mcp` connected; `aws-docs` pending approval. Nothing in the SQL material is practised yet - it was written, not learned.
- **2026-10-27 (later)** — Got the `postgres` MCP server connected after five separate failures, each a different cause: a missing `@latest` resolving a stale 0.1.0 that rejected `--access-mode`; `local` scope making the server invisible in the VS Code MCP panel; a new env var never reaching the already-running VS Code process; Git Bash rewriting `cmd /c` into `cmd C:/` via MSYS path conversion; and a first-run package download exceeding the 30s startup timeout. Settled on the **npm** `@modelcontextprotocol/server-postgres` at **user** scope reading `${POSTGRES_CONNECTION_STRING}` - the same server and variable the `insurance-etl-platform` project already used successfully, which should have been the starting point rather than the destination.
- **2026-10-27 (end)** — Little new learning; mostly finishing what was already started. Confirmed the leaked AWS key had been rotated. Got the `postgres` MCP fully working and ran the first query through it (the RANK vs DENSE_RANK example), matching the lesson's verified table. The author caught a real defect Claude missed: the execution-order figure rendered as collapsed garbage because it was not inside a fenced code block — Markdown reflows unfenced text in a proportional font. Fixed, scanned every `.md` for the same mistake, and added the rule plus a scanner to `docs/note-writing-rules.md`.
- **2026-10-27 (night)** — Worked the GlueJob2 assignment (SSE-KMS source bucket with a deny policy). Found the existing `bucket101pb` already carried a deny policy that locked out every principal except the exempt user, including the full-access console role. Recovered it via IAM Root access management (a privileged root session), which the author found and ran. Learned the three flavours of explicit deny, the User vs Role vs Policy split, and that the account sits under an organisation guardrail limiting regions. The deny policy is now deleted from `bucket101pb`; whether to re-add it, or reuse the bucket for GlueJob2, is still open.
- **2026-10-27 (late)** — Finished the bucket lock-out: the first deny-except policy used a role ARN without its `/managed/` path, so it locked the console out again; the author recovered with a second privileged root session and applied the corrected policy (verified attached, console access not yet confirmed). Also ran and questioned several SQL examples by hand (WHERE vs HAVING, GROUP BY, rank gaps, `count(*)`), and asked for explanations in Malayalam with each command broken down, now saved as a rule in `docs/teaching-rules.md`.
- **2026-10-27 (housekeeping)** — No new learning. Since the last entry, moved `chapter1.py` into `aws/` and the AWS rule files into `docs/aws/`, and wrote `docs/sql/sql-rules.md`. Then, at the author's request, split this tracker per subject (`progress/aws.md`, `progress/sql.md`, `progress/tools.md`), each listing every topic with its status and re-teach notes, and added `docs/progress-tracking-rules.md` so a topic studied before is re-taught from what worked instead of from scratch.
- **2026-10-27 (correction)** — The author pointed out they had never looked at `aws/chapter1.py`: they are learning AWS through the console and have not moved to code. Its four topics were downgraded from Walked through to Mentioned. The same check (did the author ask about it, or do it?) also downgraded the SCP topic to Mentioned and Windows shells to Walked through, and fixed *Did* notes that credited the author with commands Claude ran. The rule is now written into `docs/progress-tracking-rules.md` and the `/update-progress` command, whose old wording (Claude-written code counts as walked through) caused the over-claim.
- **2026-10-27 (Glue course files)** — The author added the Udemy course folder `Glue-MasterClass/`. Adapted it to this account: the course's four buckets became prefixes in `bucket101pb` (the author's choice), `gluejobrole1` became `role101`, and `us-east-1` became `ap-southeast-2`. Fixed bugs in the course files (job 2 template pointed at a wrong script name and passed a wrongly-cased argument; jobs 1 and 6 defined their lookup table after the UDF ran; job 6 overwrote job 1's output) and cut workers from 15 G.2X to 2 G.1X. Found that Kinesis is denied by the SCP in every region, so the streaming lab can't run, and that `role101` has no KMS permission yet. The 140 MB `city_temperature.csv` goes into Git LFS.
- **2026-10-27 (one bucket)** — Asked how many buckets the Glue course needs: none new, because `bucket101pb` holds the course's four as prefixes. Explained that S3 folders are only key prefixes (`aws s3 ls` prints `PRE`) and the catch: point each crawler at an exact prefix, never the bucket root. Claude checked: the account has one bucket, still empty.
