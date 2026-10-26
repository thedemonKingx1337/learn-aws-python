# Environment, Interpreter and How to Run

This project uses **pyenv-win** to pin the interpreter, and a project-local **`.venv`** built from it.

- pyenv-win 3.1.1 is installed; available versions are 3.10.11, 3.12.0, 3.12.6
- `.python-version` pins this project to **3.12.6** (written by `pyenv local 3.12.6`) — **commit this file**
- `.venv/` is built from that interpreter and is gitignored
- **AWS CLI v2.38.5** is installed natively on Windows, outside the venv. That is correct — it is a standalone binary, not a pip package, so it does not belong in `requirements.txt`.

## The PATH quirk that will bite you

A standalone **Python 3.12.4** install sits ahead of pyenv's shims on PATH (position 11 vs 31), and **no `pyenv global` is set**. So a bare `python` resolves to 3.12.4 — *not* a pyenv version, and not the venv.

Never assume `python` is the right interpreter. Either activate the venv first, or call `.venv\Scripts\python.exe` explicitly. When verifying something, print `sys.executable` rather than trusting `python --version`.

## Setup from scratch

```powershell
pyenv local 3.12.6
& "$env:USERPROFILE\.pyenv\pyenv-win\versions\3.12.6\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The explicit interpreter path is deliberate: `pyenv local` alone does not make `python` resolve to 3.12.6, because of the PATH quirk above.

## Day to day

```powershell
.\.venv\Scripts\Activate.ps1
python chapterN.py
```

If PowerShell refuses to run the activate script, unblock it for that session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

There is no test suite and no linter configured. Do not invent commands for either.

## Windows console encoding gotcha

The author's console is **cp1252**, not UTF-8. Printing box-drawing characters to stdout raises `UnicodeEncodeError` and kills the script. Therefore:

- ASCII figures belong in **comments and docstrings**, which the editor reads as UTF-8. Never `print()` them.
- If a script genuinely must emit them, run it with `PYTHONIOENCODING=utf-8`.

## Credentials are not configured yet

`~/.aws` contains only `amazonq` and `sso` subfolders — there is no `credentials` or `config` file, so `aws configure` has never been run, and `boto3.Session().get_credentials()` returns `None`.

Chapters must therefore **degrade gracefully when the credential chain comes up empty**, the way `chapter1.py` does: report the situation in plain English and exit, rather than assuming a live account and raising a traceback.
