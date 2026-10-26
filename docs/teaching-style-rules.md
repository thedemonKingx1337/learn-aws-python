# Rule: Teaching Style — Beginner Start, Advanced Finish

Written for a **self-learner** who may be a beginner at chapter 1 but should finish feeling like an advanced practitioner. Explain like a teacher, not a textbook. Every new concept, in this order:

1. **Connect to what they already know** — basic Python (dicts, lists, functions, loops), concepts from earlier chapters, or a real-world analogy if nothing else fits.
2. **If the concept is brand new, teach it from scratch.** Don't assume terms like "serialization", "closure", "IAM role", "cold start".
3. **Show the problem first**, with concrete numbers, so they *feel* why the solution is needed.
4. **Describe the solution in plain English** before naming it.
5. **Then give the technical term** — the mental model now exists, so the jargon sticks.
6. **Explain the real mechanics.** This is what levels them up; don't shy away from detail.
7. **Close with the why** — when to use it, when not to, what to watch out for.

## Language rules

- **Never use jargon before defining it** in plain English; afterwards, use it freely.
- **Concrete over abstract** — "200 partitions means 200 separate tasks" beats "a task per partition".
- **Always name the actual thing.** Say which table, bucket or variable — never an unexplained "the smaller side".
- **Don't dumb it down — build it up.** Reveal complexity layer by layer; the reader should end up with the *real* mechanism.
- **If a figure looks confusing, explain the confusion head-on** instead of silently editing it away. The surprise is the teaching moment.
- **Use question-driven headings in the student's own voice** ("So if we repartition, `department_id` is still the same — won't they land in the same task?") rather than cold abstract titles.

## What "advanced level" means

After reading a chapter, the author should be able to use the correct terminology in an interview, explain *why* the mechanism works rather than only *what* it does, know when **not** to use it, and predict what breaks if they get it wrong.
