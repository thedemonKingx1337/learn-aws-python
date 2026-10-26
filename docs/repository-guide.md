# Repository Layout & Conventions

## Format: plain Python modules, not notebooks

The author has decided this course is written as **`.py` files**, not Jupyter notebooks. This matters, because the author's companion repo (`D:\pbcode\learn_Python\learn_PySpark\chapter1`) *is* notebook-based, and several of its conventions assume markdown cells. Do **not** carry those over literally:

- Explanation lives in **comments and docstrings**, not markdown cells.
- There are no `---` cell separators, no `#### (emoji)` markdown headings, and no `## (emoji) N.` markdown sections.
- Do not create `.ipynb` files here, and do not propose converting a chapter into one unless the author asks.

What *does* carry over from that repo is the teaching approach, the README index discipline, the SQL-first code style, and the ASCII figure constraints — all restated for `.py` in the other docs.

## Directory naming quirk

The project root is **`chapter1/`**, not `learn__AWS/`. The parent `learn__AWS/` contains nothing but this folder. All modules, the `README.md` and the git root belong **inside `learn__AWS\chapter1\`**. The companion PySpark repo is laid out the same confusing way — `learn_PySpark/` is empty and `learn_PySpark/chapter1/` is the real repo — so don't "fix" the nesting.

## Layout

- **`chapterN.py`** — one module per chapter, at the repo root, numbered sequentially. Each is **self-contained**: it builds its own clients/session and its own sample data, so any chapter can be read and run on its own without having run an earlier one.
- Each chapter is **directly runnable** — real work guarded by `if __name__ == "__main__":` so the module can also be imported without side effects (important here: an import that fires AWS calls can cost money).
- **`README.md`** — the course index, styled like a textbook table of contents: one table row per chapter with a relative link, a descriptive title, and the concrete APIs taught.
- **`data/`** — sample datasets.
- **`docs/`** — these rule files, indexed from `CLAUDE.md`.
- **`.venv/`** — project-local virtual environment built from pyenv 3.12.6; **never index or modify it**.
- **`.python-version`** — pyenv's version pin; commit it.

## Code style: SQL first, then code

For anything that genuinely translates to SQL (Spark/Glue DataFrame work, Athena queries), write the SQL equivalent above the code so a reader coming from SQL recognises the operation instantly:

```python
# how to see the DISTINCT values of a dataframe
'''SELECT DISTINCT * FROM emp'''
emp_unique = emp.distinct()
emp_unique.show()
```

Pattern: a short `#` comment naming the concept, then a `'''...'''` string holding the SQL, then the code.

**Skip the SQL line when there is no SQL equivalent** — `printSchema()`, `explain()`, a `boto3` client call. Never invent one, and never put the SQL of a *different* approach there.
