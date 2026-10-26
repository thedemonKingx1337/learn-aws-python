# SQL Practice

Focused practice on the four things that actually come up: **execution order, DISTINCT, window functions, and CTEs (including multiple and recursive)**.

Every query in these files was **run against the live database** before being written down. Where a number or a table of output is quoted, it is real output, not an illustration.

## The two datasets

| Schema | What it is | Size |
|---|---|---|
| `public` | the **retail_db** dataset — categories, customers, departments, orders, order_items, products | 172,198 order_items across 68,883 orders, 12,435 customers |
| `practice` | small tables built for this course | 33 rows total |

**`public` is the main practice ground.** Real cardinality is the point — window functions on twenty toy rows teach you nothing about how they behave when a partition has thousands.

**`practice` exists only for what `public` cannot show:**

- `employees` — a 3-level manager hierarchy (recursive CTEs), deliberate salary **ties** (`RANK` vs `DENSE_RANK`), and one **NULL salary** (which, memorably, ranks *first*)
- `sales_daily` — a deliberate **gap** at 2024-01-05, so `ROWS` and `RANGE` window frames give different answers
- `signups` — duplicates and NULLs, so `DISTINCT` semantics are visible

## Connecting

`psql` is not on PATH. Call it by full path:

```powershell
$env:PGPASSWORD = "<your password>"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d postgres
```

Or use pgAdmin, which you already have connected.

To rebuild the practice tables from scratch at any time:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d postgres -f sql\00_practice_schema.sql
```

That file **drops and recreates only the `practice` schema**. It never touches `public`, so the retail data is safe no matter how badly you mangle the small tables.

## Order to work through

| File | Topic |
|---|---|
| [01_execution_order.md](01_execution_order.md) | The clause execution order, and the four rules that follow from it. **Start here** — the other three lessons are consequences of this one. |
| [05_joins.md](05_joins.md) | **Read this second**, despite the number — it was added later. INNER vs LEFT, the `ON`-vs-`WHERE` trap, **fan-out** (68,883 orders become 172,198 rows), self-joins, and why 11,452 of your orders vanish under an inner join. |
| [02_distinct.md](02_distinct.md) | DISTINCT applies to the whole row; NULL handling; `count(DISTINCT)`; `DISTINCT ON` |
| [03_window_functions.md](03_window_functions.md) | `OVER`, `PARTITION BY`, ROW_NUMBER vs RANK vs DENSE_RANK, NULLS FIRST trap, ROWS vs RANGE frames, LAG/LEAD |
| [04_ctes.md](04_ctes.md) | Single, **multiple**, chained and **recursive** CTEs; the Postgres 12 inlining change |
| [solutions.md](solutions.md) | Answers with explanations — all 23 questions |

Each lesson ends with questions graded easy → hard. **Attempt them before opening the solutions** — reading a correct query teaches far less than writing a wrong one and seeing the error.

## The one idea to take away

> SQL is written in one order and executed in another.

`SELECT` is written first and runs sixth. Window functions run at stage 5 — after `WHERE`, which is why `WHERE` can never filter a window result, which is why CTEs exist. Almost every SQL question anyone has is downstream of that single fact.

## Why this lives in an AWS repo

Glue runs PySpark SQL, and Athena is SQL over S3. The window functions and CTEs here are the same ones you will write against the Glue Data Catalog later — the engine changes, the semantics do not. `DISTINCT ON` is the one exception: Postgres-only, and [02_distinct.md](02_distinct.md) gives the portable form alongside it.
