# Rule: Track Progress, and Re-teach from It

The author's progress lives in two layers:

- [PROGRESS.md](../PROGRESS.md) is the **dashboard**: status, per-subject counts, what to revise first, next up, blocked items and the session log.
- [progress/](../progress/) has **one file per subject**: [aws.md](../progress/aws.md), [sql.md](../progress/sql.md), [tools.md](../progress/tools.md). Each lists every topic, covered or not, with re-teach notes for the covered ones.

A new subject gets its own file there and its own row on the dashboard.

## Status levels

| Status | Means |
|---|---|
| Not started | on the roadmap, not taught yet |
| Mentioned | came up in passing; does not count as covered |
| Walked through | Claude explained or built it while the author read along |
| Practised | the author did it themselves: ran it, broke it, fixed it |
| Unknown | studied outside this repo, such as the Udemy Glue course; ask before teaching |

Never promote a topic on the strength of Claude's work. A walked-through topic becomes practised when the author redoes it without help.

**Walked through needs the author's attention, not just Claude's work.** If Claude wrote or ran something and the author never read it or asked about it, it is Mentioned. For example, Claude wrote and ran `aws/chapter1.py` on 2026-10-25, but the author was learning through the console and had not opened it, so its topics are Mentioned. When unsure whether the author engaged, choose the lower status; the author can correct it upward.

## When the author asks about a topic

Look the topic up in its subject file **before answering**.

1. **Not listed, or Not started:** it is new. Teach it from scratch following [teaching-style-rules.md](teaching-style-rules.md), then add a row and a note.
2. **Unknown:** ask what they remember from the course first, then fill the gaps.
3. **Mentioned, Walked through or Practised:** it is a **revisit**. Do not teach it as if it were new.
   - Open with a line or two recalling what was covered, reusing the *What worked* explanation.
   - Spend the time on the *Shaky* part, not on what they already got.
   - Point to the lesson file.
   - Finish with the *Check* questions, and let the author answer before moving on.
   - Afterwards add a *Revisited* line: the date, and what was still shaky.

Asking again about a practised topic means it did not stick. Say so under *Shaky*, and consider adding it to *Revise first* on the dashboard.

## The re-teach note

Every covered topic has one note, headed with the exact topic name from its table row:

- **Idea:** the core point in one or two sentences
- **What worked:** the analogy, example or figure that made it land, in the language it was given
- **Did:** what the author did themselves, never a command Claude ran (leave it out if nothing)
- **Shaky:** what they got wrong or asked more than once
- **Check:** one to three questions that test recall
- **Revisited:** dates, added each time the topic is taught again

Keep notes short. A note is a prompt for re-teaching, not a copy of the lesson.

A **Mentioned** topic gets a short note instead: *Idea*, *Came up* (where it surfaced), *Start with* (where to begin when it is studied), and a *Check* if useful.

## Keeping it current

- Update at the end of any session where something was learned, following [.claude/commands/update-progress.md](../.claude/commands/update-progress.md).
- Change a topic's status in its row only. The dashboard counts are recounted from the rows, never typed by hand.
- The repo is public: no account IDs, passwords or secret keys in these files.
