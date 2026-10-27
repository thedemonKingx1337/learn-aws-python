# SQL progress

Course material: [sql/](../sql/). Rules for writing it: [docs/sql/sql-rules.md](../docs/sql/sql-rules.md). How this file is used, including re-teaching: [docs/progress-tracking-rules.md](../docs/progress-tracking-rules.md).

## Topics

In the recommended reading order. Joins is lesson 05 but comes second.

| Topic | Status | Where | First covered |
|---|---|---|---|
| Execution order: the 9 stages, aliases, WHERE vs HAVING, the GROUP BY rule | Practised | [01_execution_order.md](../sql/01_execution_order.md) | 2026-10-27 |
| Joins: INNER vs LEFT, fan-out, `ON` vs `WHERE`, self-join | Not started | [05_joins.md](../sql/05_joins.md) | - |
| Counting: `count(*)` vs `count(col)` vs `count(DISTINCT col)` | Walked through | [02_distinct.md](../sql/02_distinct.md) | 2026-10-27 |
| DISTINCT: whole-row semantics, NULLs, `DISTINCT ON` | Not started | [02_distinct.md](../sql/02_distinct.md) | - |
| Window functions: `OVER (PARTITION BY)`, ranking, the NULLS FIRST trap | Walked through | [03_window_functions.md](../sql/03_window_functions.md) | 2026-10-27 |
| Window functions: frames (`ROWS` vs `RANGE`), running totals, `LAG` / `LEAD` | Not started | [03_window_functions.md](../sql/03_window_functions.md) | - |
| CTEs: single, multiple, recursive | Mentioned | [04_ctes.md](../sql/04_ctes.md) | 2026-10-27 |
| Foreign keys and self-referencing tables (`REFERENCES`) | Walked through | [00_practice_schema.sql](../sql/00_practice_schema.sql) | 2026-10-27 |

## Questions

| Lesson | Questions | Answered |
|---|---|---|
| 01 Execution order | Q1.1 to Q1.5 | 0 / 5 |
| 05 Joins | Q5.1 to Q5.7 | 0 / 7 |
| 02 DISTINCT | Q2.1 to Q2.5 | 0 / 5 |
| 03 Window functions | Q3.1 to Q3.6 | 0 / 6 |
| 04 CTEs | Q4.1 to Q4.7 | 0 / 7 |
| **Total** | | **0 / 30** |

A question counts as answered only when the author wrote the query before opening [solutions.md](../sql/solutions.md).

## Re-teach notes

### Execution order: the 9 stages, aliases, WHERE vs HAVING, the GROUP BY rule
- **Idea:** SQL runs FROM, WHERE, GROUP BY, HAVING, window functions, SELECT, DISTINCT, ORDER BY, LIMIT, in that order, and a stage can't see anything a later stage creates. After `GROUP BY`, every column in `SELECT` must be grouped or inside an aggregate.
- **What worked:** the [figure](../sql/01_execution_order_figure.md) open in split view. WHERE as a bouncer at the door, who checks one person at a time and never sees the crowd, so it can't count a group. For GROUP BY, the Malayalam class example: ഒരു ഡിവിഷനിൽ 6 കുട്ടികൾ ഉണ്ടെങ്കിൽ, ആ ഒരു വരിയിൽ ആരുടെ പേര് എഴുതും?
- **Did:** ran the failing queries in pgAdmin and asked why each one failed: an alias in `HAVING` (42703), `count(*)` in `WHERE`, `SELECT *` with `GROUP BY dept` (42803).
- **Shaky:** asked those three as separate questions, but they are one idea; worth re-deriving without notes. Also thought `dept` "is created after GROUP BY": columns exist from `FROM`, and only aliases are born at `SELECT`. Postgres lets `GROUP BY` and `ORDER BY` see aliases, as an extension.
- **Check:** (1) Why can `ORDER BY` use an alias when `WHERE` can't? (2) Fix `SELECT * FROM practice.employees GROUP BY dept` two ways. (3) Where does `count(*) > 4` go, and why?
- **Not yet:** rule 4 (`DISTINCT` runs before `ORDER BY`), and questions Q1.1 to Q1.5.

### Counting: `count(*)` vs `count(col)` vs `count(DISTINCT col)`
- **Idea:** `count(*)` counts rows, `count(col)` counts non-NULL values, `count(DISTINCT col)` counts different non-NULL values.
- **What worked:** Sales in `practice.employees`: 5 rows, 4 salaries (Hugo's is NULL), 3 distinct (Farid and Gita both earn 67000).
- **Check:** after a `LEFT JOIN` from orders to order_items, why count items with `count(oi.order_item_id)` and not `count(*)`?

### Window functions: `OVER (PARTITION BY)`, ranking, the NULLS FIRST trap
- **Idea:** a window function keeps every row and adds a group-level value, while `GROUP BY` collapses rows. `rank()` is the number of people ahead plus one, so ties share a rank and the next rank skips. `dense_rank()` never skips. `row_number()` breaks ties arbitrarily.
- **What worked:** a `people_ahead` column next to `rank()`. The race: two runners tie for silver, nobody gets bronze, and the next runner is 4th.
- **Did:** ran their own `rank()` query partitioned by department in pgAdmin.
- **Shaky:** expected 4, 4, 5 instead of 4, 4, 6. Hugo (NULL salary) came out 1st in Sales because `ORDER BY salary DESC` puts NULLs first; Claude pointed it out. Fix with `NULLS LAST`.
- **Check:** for salaries 100, 90, 90, 80, give `rank`, `dense_rank` and `row_number`. Why was Hugo ranked first?

### CTEs: single, multiple, recursive
- **Idea:** CTE stands for Common Table Expression: a named query written as `WITH name AS (...)` and used like a table for one statement. Nothing is stored.
- **Came up:** wrapping `count(*) OVER (PARTITION BY dept)` in a CTE so the outer `WHERE` could filter it, because windows run after `WHERE`.
- **Start with:** lesson 04 from the start. Multiple CTEs were the author's original request.

### Foreign keys and self-referencing tables (`REFERENCES`)
- **Idea:** `manager_id int REFERENCES practice.employees(emp_id)` makes every `manager_id` point at a real employee in the same table. NULL is allowed (Lena, the top), rows go in manager first, and a referenced row can't be deleted.
- **What worked:** the small table figure, Lena (NULL) above Jia (12) above Asha (10).
- **Check:** why does `00_practice_schema.sql` insert Lena before everyone else? What would an insert with `manager_id = 777` do?
