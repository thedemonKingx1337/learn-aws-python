---
description: Analyse this session and update the tracker (PROGRESS.md and progress/) - what was learned, what is next. Needs no input.
argument-hint: [optional focus note, e.g. "mark Lambda done"]
---

# Update the learning tracker

Update the tracker so it reflects where the author now stands: the dashboard `PROGRESS.md`, and the subject files in `progress/` (`aws.md`, `sql.md`, `tools.md`). The layout, status levels and re-teach note format are defined in `docs/progress-tracking-rules.md`; follow them.

**Work this out yourself from the conversation and the repo. Do NOT ask the author to summarise what they did.** Having to narrate their own progress is the exact chore this command exists to remove. If `$ARGUMENTS` is present, treat it as a steer, not as the whole answer.

## 1. Gather evidence

Look at all of these before writing anything:

- **This conversation** - what was actually explained, demonstrated, run, debugged, and what the author asked about. Their questions reveal what they did not know, which is as informative as what got covered.
- **The repo** - which `aws/chapterN.py` files exist, what APIs they import and call, and what `README.md` claims they teach.
- **The current tracker** (`PROGRESS.md` and the files in `progress/`) - never rewrite it wholesale. Amend it, so history survives.
- **`git log`** if this is a git repo - commit messages since the last tracker entry.
- **Whether the work is actually safe** - see step 2b. Check this every time, not only when it looks wrong.

## 2. Classify honestly - this is the important part

A learning tracker that overstates what the author knows is worse than no tracker. Use three levels, and do not inflate:

- **Practised** - the author wrote it, ran it, broke it, or debugged it themselves. Strongest signal.
- **Walked through** - Claude built or explained it while the author read along. They have seen it; they have not yet done it.
- **Mentioned** - it came up in passing and was not really taught. Does not count as covered.

If Claude wrote all the code, it is **walked through** at most, and only if the author actually read it or asked about it. Code Claude wrote or ran without the author engaging is **Mentioned**. When unsure, choose the lower status and say so; the author can correct it upward. In a *Did* note, write only what the author did; when Claude ran a command, say so. The author can promote an item themselves once they have redone it unaided.

The topic tables use two more statuses: **Not started** (on the roadmap) and **Unknown** (studied outside this repo, such as the Udemy Glue course, depth not known).

Also capture what the author **struggled with or asked twice about** - that goes in the topic's *Shaky* note, and the worst ones in *Revise first* on the dashboard, because it is the most valuable thing the tracker records.

## 2b. Check the work is actually safe

Progress recorded on work that could vanish is worthless. Before writing anything, check and report:

1. **Is it a git repo at all?** `git rev-parse --is-inside-work-tree`. If not, say so plainly and offer `git init` plus a first commit. Do not let this slide quietly from session to session.
2. **Is anything uncommitted?** `git status --porcelain`. Lesson files, chapters and the tracker itself are the work - uncommitted means unrecoverable.
3. **Is there a remote?** `git remote -v`. Commits on one disk are not a backup. A dead drive takes the history with it.
4. **Does anything outside the repo need rebuilding?** Database schemas, seeded data, environment variables, MCP config. If a teardown would lose it, there must be a script in the repo that recreates it - name the script, or flag that none exists.

Report the answer in the summary **every time**, even when everything is fine ("23 files, all committed, pushed"). A tracker that only mentions backup when it is already too late is not doing its job.

## 3. Update the subject files, then the dashboard

**Subject files** (`progress/aws.md`, `progress/sql.md`, `progress/tools.md`):

- **Topic rows** - set the status of every topic touched this session, and add a row for anything new. A status is changed here and nowhere else.
- **Re-teach notes** - for every covered topic: *Idea*, *What worked* (the analogy or example that landed, in the language it was given), *Did*, *Shaky*, *Check*. If a topic was taught again, add a *Revisited* line with the date and what was still shaky. Name real functions, not vague topics: "`sts.get_caller_identity()`, the 5-step credential chain, `NoCredentialsError` vs `ClientError`" beats "AWS basics".
- **SQL questions** - update the answered counts in `progress/sql.md`. A question counts only if the author answered it before opening the solutions.

**Dashboard** (`PROGRESS.md`):

- **Status line** - today's date, and the one-sentence state of play.
- **At a glance** - recount the statuses from the subject files' topic rows. Never type the numbers by hand.
- **Revise first** - two to four pointers to the shakiest topics.
- **Next up** - the ordered shortlist, 2 to 4 items. Re-derive it each time from what was just finished and what it unlocks. Say in one line *why* each is next.
- **Blocked / open questions** - anything that cannot proceed yet (e.g. a decision the author has not made). Remove items that got resolved.
- **Session log** - append ONE dated entry, 1 to 3 lines, in the author's terms. Never delete older entries.

## 4. Rules

- **Amend, never regenerate.** Prior entries and dates are the record; keep them.
- **Be specific.** "Learned Lambda" is useless six weeks later. "Invoked a function with `lambda_client.invoke()`, read the `Payload` bytes, hit a cold start" is useful.
- **If nothing meaningful was learned this session** (pure setup, refactoring, config), say exactly that in the session log and leave the topic rows alone. Do not pad them.
- **Keep the dashboard under ~150 lines and the notes short.** When the session log grows past ~20 entries, condense the oldest into one line per month; when a re-teach note grows past ~8 lines, tighten it.

## 5. Report back

Afterwards, tell the author in 3 to 5 lines: which topics changed status, what is next and why, and anything now unblocked. **Always include one line on whether the work is committed and backed up** (step 2b). Do not paste the whole file back.
