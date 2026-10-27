# Rule: Where Explanation Goes in a `.py` Chapter

**Code first, then a short note on the code just read.** Never stack screens of theory at the top of a module above a long run of code — the reader forgets it before reaching the code, and has nothing concrete to attach it to.

So a chapter module reads as alternating blocks:

```python
lambda_client = boto3.client("lambda")

# ----------------------------------------------------------------------
# That created a client, not a connection. boto3 builds a local object
# holding your credentials and the endpoint URL; no network call has
# happened yet, which is why a typo'd region fails later, not here.
# ----------------------------------------------------------------------

response = lambda_client.invoke(
    FunctionName="hello-world",
    Payload=json.dumps({"name": "aravind"}).encode(),
)
```

- Each inline note is **short (~5-15 lines)** and explains **only the block above it**.
- **Long-form material** — the mechanism, the costs, the alternatives — goes in the **module-level docstring** at the top, or in a clearly marked numbered section at the **bottom** of the file, for reading once the code already makes sense. Not interleaved mid-flow.
- **A figure comes before the prose that explains it.** Number the figure's steps and then reuse exactly those numbers, in order and with the same labels, in the explanation beneath. Lead with a pointer at the picture ("Now the same seven numbers, in words:").
- **One figure per idea.** A sequence figure ("what happens, in order") and a structural map ("which box lives on which machine") are two different figures with a cross-reference each way — never the same figure twice.
- **Never rewrite the author's own code.** Write notes around *their* variable names, their data and their output.

## ASCII figure constraints

Figures go in docstrings or comment blocks, and the same hard limits apply:

- **Max ~70 characters per line.** Prefer **vertical, stacked** layouts over side-by-side boxes.
- **Only this character set:** `┌ ┐ └ ┘ ├ ┤ ┬ ┴ ─ │ ▼ ←`. Never use `▶ ◀ ↑ ↓ × •` or emoji inside a figure — they are not single-width in the author's font, so every box edge after them misaligns. Use ASCII `--->`, `<---`, `x` instead.
- **Verify before showing the user:** every line 70 chars or fewer, and all box-edge lines sharing an indent share the same length.
- **For transformations and optimisation techniques, always draw 3 parts:** Before (raw data and the problem), Transformation (how the keys/tables are altered), After (the parallel result).

### In Markdown, a figure MUST be inside a fenced code block

A figure that is correctly built can still render as garbage. Markdown treats
unfenced text as a paragraph: it collapses runs of whitespace, ignores the line
breaks and reflows the result in a proportional font. Every box edge is
destroyed, and the preview looks nothing like the file.

So in any `.md` file, wrap the figure:

    ```text
    (figure here)
    ```

`text` rather than a language name, so no syntax highlighter tries to colour it.

This does not apply to `.py` files, where figures live in comments or docstrings
and are already monospaced.

Scan for the mistake across the repo - it is invisible until someone opens the
preview:

```bash
PYTHONIOENCODING=utf-8 python - <<'PY'
import glob, io
BOX = set("┌┐└┘├┤┬┴─│▼←")
for path in glob.glob("**/*.md", recursive=True):
    fenced = False
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced; continue
        if not fenced and sum(c in BOX for c in line) > 3:
            print(f"UNFENCED {path}:{n}")
PY
```

The `> 3` threshold ignores prose that merely mentions a box character inline.

### Verifying a figure

Do not eyeball it. Run a check — this is the script used on `chapter1.py`:

```bash
PYTHONIOENCODING=utf-8 python - <<'PY'
lines = open("aws/chapter1.py", encoding="utf-8").read().split("\n")
fig = [l for l in lines if any(c in l for c in "┌┐└┘├┤│▼")]
edges = {len(l) for l in fig if "─" in l}
print("box-edge widths:", sorted(edges), "->",
      "ALIGNED" if len(edges) == 1 else "MISALIGNED")
print("max width:", max(len(l) for l in fig), "(limit 70)")
PY
```

`PYTHONIOENCODING=utf-8` is required because the author's console is cp1252 and will otherwise raise `UnicodeEncodeError` on the box characters.
