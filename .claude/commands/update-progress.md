---
description: Analyse this session and update PROGRESS.md - what was learned, what is next. Needs no input.
argument-hint: [optional focus note, e.g. "mark Lambda done"]
---

# Update the learning tracker

Update `PROGRESS.md` at the repo root so it reflects where the author now stands.

**Work this out yourself from the conversation and the repo. Do NOT ask the author to summarise what they did.** Having to narrate their own progress is the exact chore this command exists to remove. If `$ARGUMENTS` is present, treat it as a steer, not as the whole answer.

## 1. Gather evidence

Look at all of these before writing anything:

- **This conversation** - what was actually explained, demonstrated, run, debugged, and what the author asked about. Their questions reveal what they did not know, which is as informative as what got covered.
- **The repo** - which `chapterN.py` files exist, what APIs they import and call, and what `README.md` claims they teach.
- **The current `PROGRESS.md`** - never rewrite it wholesale. Amend it, so history survives.
- **`git log`** if this is a git repo - commit messages since the last tracker entry.
- **Whether the work is actually safe** - see step 2b. Check this every time, not only when it looks wrong.

## 2. Classify honestly - this is the important part

A learning tracker that overstates what the author knows is worse than no tracker. Use three levels, and do not inflate:

- **Practised** - the author wrote it, ran it, broke it, or debugged it themselves. Strongest signal.
- **Walked through** - Claude built or explained it while the author read along. They have seen it; they have not yet done it.
- **Mentioned** - it came up in passing and was not really taught. Does not count as covered.

If Claude wrote all the code, it is **walked through**, not practised. Say so. The author can promote an item themselves once they have redone it unaided.

Also capture what the author **struggled with or asked twice about** - that belongs under "Worth revisiting", because it is the most valuable section in the file.

## 2b. Check the work is actually safe

Progress recorded on work that could vanish is worthless. Before writing anything, check and report:

1. **Is it a git repo at all?** `git rev-parse --is-inside-work-tree`. If not, say so plainly and offer `git init` plus a first commit. Do not let this slide quietly from session to session.
2. **Is anything uncommitted?** `git status --porcelain`. Lesson files, chapters and the tracker itself are the work - uncommitted means unrecoverable.
3. **Is there a remote?** `git remote -v`. Commits on one disk are not a backup. A dead drive takes the history with it.
4. **Does anything outside the repo need rebuilding?** Database schemas, seeded data, environment variables, MCP config. If a teardown would lose it, there must be a script in the repo that recreates it - name the script, or flag that none exists.

Report the answer in the summary **every time**, even when everything is fine ("23 files, all committed, pushed"). A tracker that only mentions backup when it is already too late is not doing its job.

## 3. Update these sections

- **Status line** - today's date, and the one-sentence state of play.
- **Covered so far** - add new rows with: topic, level (practised / walked through), where it lives (`chapterN.py`), date, and the specific APIs or concepts. Name real functions, not vague topics: "`sts.get_caller_identity()`, the 5-step credential chain, `NoCredentialsError` vs `ClientError`" beats "AWS basics".
- **Next up** - the ordered shortlist, 2 to 4 items. Re-derive it each time from what was just finished and what it unlocks. Say in one line *why* each is next.
- **Roadmap** - the longer backlog. Tick off what moved, and reorder if the session changed the plan.
- **Blocked / open questions** - anything that cannot proceed yet (e.g. credentials not configured, no IAM user, a decision the author has not made). Remove items that got resolved.
- **Worth revisiting** - concepts that were shaky, or that were walked through but never practised.
- **Session log** - append ONE dated entry, 1 to 3 lines, in the author's terms. Never delete older entries.

## 4. Rules

- **Amend, never regenerate.** Prior entries and dates are the record; keep them.
- **Be specific.** "Learned Lambda" is useless six weeks later. "Invoked a function with `lambda_client.invoke()`, read the `Payload` bytes, hit a cold start" is useful.
- **If nothing meaningful was learned this session** (pure setup, refactoring, config), say exactly that in the session log and leave the covered table alone. Do not pad it.
- **Keep the whole file under ~150 lines.** When the session log grows past ~20 entries, condense the oldest into a single summary line per month.

## 5. Report back

Afterwards, tell the author in 3 to 5 lines: what moved to covered, what is next and why, and anything now unblocked. **Always include one line on whether the work is committed and backed up** (step 2b). Do not paste the whole file back.
