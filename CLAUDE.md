# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Keep this file a **short index, not a rulebook**. It is loaded into context on every session, so detail belongs in [docs/](docs/) where it is read only when relevant.

## What this repository is

A personal course for learning **AWS and Python** together — `boto3`, AWS Glue, EC2, Lambda, and the Python needed to drive them. PySpark is in scope since Glue runs on it, and **SQL practice lives in [sql/](sql/)** (PostgreSQL 18 on localhost) because Athena and Glue are both SQL engines. The AWS chapters are runnable `.py` modules in [aws/](aws/) (`aws/chapterN.py`), **not** notebooks, with a textbook-style index in [README.md](README.md).

## The rule that outranks the others

**Teach; do not just do things.** The repo exists so the author learns, not so tasks get finished. Never run a command without saying why you ran it, what it does, and whether it was actually necessary — diagnostics included. Show real errors and decode them instead of silently working around them.

Full rules, with a worked example: **[docs/teaching-rules.md](docs/teaching-rules.md)** — read it before replying to anything.

## Where the author currently stands

**Read [PROGRESS.md](PROGRESS.md) before teaching anything**, plus the subject file in [progress/](progress/) for whatever the author is working on (`aws.md`, `sql.md`, `tools.md`). Together they list every topic, covered or not, at what depth, and how it was taught. **When the author asks about a topic, look it up there first:** a topic already covered is re-taught from its notes, starting from what worked and spending the time on what was shaky, never as if it were new. Rules: [docs/progress-tracking-rules.md](docs/progress-tracking-rules.md).

**Keep it current without being asked.** At the end of any session where something was learned, built or decided, update it by following `.claude/commands/update-progress.md` — the same work the `/update-progress` command does. The author should never have to say "update the tracker" or narrate their own progress; work it out from the conversation and the repo.

## Three things to know before you touch anything

1. **A bare `python` is the wrong interpreter.** It resolves to a standalone Python 3.12.4 that sits ahead of pyenv on PATH — not the pyenv 3.12.6 this project pins, and not the venv. Activate `.venv` first, or call `.venv\Scripts\python.exe` explicitly.
2. **Ask before provisioning anything billable.** Reading and listing are fine; creating EC2 instances, Glue jobs or crawlers is not.
3. **The project root is `chapter1/`, not `learn__AWS/`.** The parent folder holds nothing else. Don't "fix" the nesting.

## Doc index

| Doc | When to read it |
|-----|-----------------|
| [docs/teaching-rules.md](docs/teaching-rules.md) | **Always, before replying.** How to narrate commands, explain reasoning, decode errors, and hand work over so the author learns it. |
| [docs/teaching-style-rules.md](docs/teaching-style-rules.md) | **Always, when explaining any concept.** Beginner start, advanced finish: problem first, plain English before jargon, then the real mechanics. |
| [docs/progress-tracking-rules.md](docs/progress-tracking-rules.md) | **Always, at the start of a session and whenever the author asks about a topic.** Where progress lives, the status levels, and how to re-teach a topic studied before. |
| [docs/aws/environment-setup.md](docs/aws/environment-setup.md) | Before running Python, pip or pyenv — the interpreter trap, venv setup, the cp1252 console limitation, and current credential state. |
| [docs/repository-guide.md](docs/repository-guide.md) | Before exploring or adding files — layout, why `.py` and not notebooks, the directory quirk, and the SQL-first code style. |
| [docs/note-writing-rules.md](docs/note-writing-rules.md) | Before writing any explanatory note or figure in a chapter — where notes go, and the hard ASCII figure constraints plus how to verify them. |
| [docs/readme-index-rules.md](docs/readme-index-rules.md) | **Always follow.** Whenever a chapter is added or changes significantly, sync the README table of contents. |
| [docs/aws/aws-safety-rules.md](docs/aws/aws-safety-rules.md) | Before any call that creates, modifies or costs money; and whenever credentials, region or target environment come up. |
| [docs/sql/sql-rules.md](docs/sql/sql-rules.md) | Before writing or editing anything in `sql/` - verify every query against the live database, the two datasets, the shape of a lesson, and dialect notes. |

## Adding new rules

When a new instruction is needed, add it as a **new file in [docs/](docs/)** and list it in the table above with a "when to read it" trigger. Do not grow this file.
