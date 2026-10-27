# SQL Track Rules

These apply to everything in [sql/](../../sql/).

## Verify before writing

Every query, and every number quoted in a lesson or a solution, must be run against the live database first. In the first draft a rank table and two row counts were wrong, and only running them caught it. Use the read-only `postgres` MCP tool or `psql`. Quote real output; never invent it.

## Two datasets

- **`public`** - the retail_db dataset (172k `order_items`). The main practice ground. Never modify it.
- **`practice`** - small tables built only for what `public` cannot show: salary ties, a NULL, a manager hierarchy, a gap in a date series. `sql/00_practice_schema.sql` drops and recreates only this schema, so it is always safe to re-run.

## Connecting

- `psql` is not on PATH. Call `C:\Program Files\PostgreSQL\18\bin\psql.exe` by its full path.
- The `postgres` MCP server is read-only. Its connection string comes from the `POSTGRES_CONNECTION_STRING` user environment variable, so no password may ever appear in a repo file.

## Shape of a lesson

- Teach with a worked example first, then end with questions graded easy to hard, numbered `Q<lesson>.<n>`.
- Answers go in `sql/solutions.md` with the reasoning, not just the query.
- When a query fails, show the real error text and say which stage of the execution order caused it.
- Prefer examples that expose a trap: NULL handling, ties, fan-out, empty groups.
- A descending window `ORDER BY` uses `NULLS LAST`, unless the point of the example is that NULLs sort first.

## Dialects

Postgres-only features (such as `DISTINCT ON`) are flagged as Postgres-only, with the portable form beside them. The same SQL will later run on Athena and Spark SQL.

## Figures

Any ASCII figure goes inside a fenced `text` block. See [note-writing-rules.md](../note-writing-rules.md).
