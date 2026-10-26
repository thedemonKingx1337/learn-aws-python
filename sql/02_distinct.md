# 2. DISTINCT - subtler than it looks

Most people read `DISTINCT` as "remove duplicates from this column." It is not. **`DISTINCT` de-duplicates the whole output row.**

## It applies to the entire select list

```sql
SELECT DISTINCT email FROM practice.signups;        -- 3 rows
SELECT DISTINCT email, plan FROM practice.signups;  -- 5 rows
```

Adding a column can only ever **increase** the row count, because each row now has more ways to differ. `DISTINCT` is not attached to the column written next to it — it governs the full row.

This is the most common DISTINCT bug: someone writes `SELECT DISTINCT customer_id, order_date` expecting one row per customer, and gets one row per customer *per date*.

## NULLs: DISTINCT disagrees with `=`

`practice.signups` has three rows where `email IS NULL`. Yet `SELECT DISTINCT email` returns exactly **one** NULL.

That looks inconsistent, because `NULL = NULL` is **not true** — it is NULL. But `DISTINCT` does not use `=`; it uses *is not distinct from*, under which two NULLs **are** the same. So:

- `WHERE email = NULL` matches nothing, ever
- `SELECT DISTINCT email` collapses every NULL into one row

Both are correct. They are simply different comparisons.

## COUNT(DISTINCT x) silently drops NULLs

```sql
SELECT count(*)              AS all_rows,        -- 7
       count(email)          AS non_null_email,  -- 4
       count(DISTINCT email) AS distinct_email   -- 2
FROM practice.signups;
```

Three different numbers from one column:

- `count(*)` counts **rows**
- `count(col)` counts **non-NULL values**
- `count(DISTINCT col)` counts **distinct non-NULL values**

**The NULL that DISTINCT kept as a row is not counted here.** That is a genuine inconsistency in SQL, and worth memorising rather than reasoning about each time.

## DISTINCT vs GROUP BY

```sql
SELECT DISTINCT dept FROM practice.employees;
SELECT dept FROM practice.employees GROUP BY dept;
```

Identical results, and usually an identical plan on PostgreSQL. Use `GROUP BY` when you also want aggregates, `DISTINCT` when you only want unique rows.

Reaching for `DISTINCT` to "fix" a query that returns too many rows is almost always hiding a wrong join. Find the join instead — `DISTINCT` on a bad join is slow *and* still wrong the moment you add another column.

## DISTINCT ON — PostgreSQL only

"One row per group, specifically the newest one" normally needs a window function. Postgres has a shortcut:

```sql
SELECT DISTINCT ON (dept) dept, emp_name, hire_date
FROM   practice.employees
ORDER  BY dept, hire_date DESC;
```

It keeps the **first row per `dept`** after sorting. The rule that trips everyone: `ORDER BY` must **start with** the same expressions as `DISTINCT ON`, otherwise "first" is undefined and Postgres rejects the query.

Not portable — Athena and Spark SQL need the window-function form instead.

---

## Questions

Answers in [solutions.md](solutions.md). Try them first.

**Q2.1** Before running: how many rows does each return, and why?

```sql
SELECT DISTINCT plan FROM practice.signups;
SELECT DISTINCT email, plan FROM practice.signups;
```

**Q2.2** Explain in one sentence why `count(DISTINCT email)` is 2 while `SELECT DISTINCT email` returns 3 rows.

**Q2.3** In `public.orders`, how many distinct customers placed an order? Now how many distinct (customer, status) pairs? Why is the second larger?

**Q2.4** Using `DISTINCT ON`, return the most recent order for each of 10 customers in `public.orders`. Then write the same query with a window function.

**Q2.5** Harder. This is meant to count customers per state but gives wrong numbers. Diagnose it:

```sql
SELECT DISTINCT customer_state, count(*)
FROM   public.customers
GROUP BY customer_state;
```
