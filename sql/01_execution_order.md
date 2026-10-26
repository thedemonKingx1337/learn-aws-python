# 1. Execution Order - the one idea everything else rests on

SQL is written in one order and **executed in another**. Almost every
"why doesn't this work?" in SQL is this mismatch.

You write `SELECT` first. The database runs it sixth.

## The real order

**The figure is in its own file:** [01_execution_order_figure.md](01_execution_order_figure.md). Open it in a split view and keep it beside this lesson and beside your queries.

Read it as a **pipeline**: each stage receives the rows the stage above
produced. A stage cannot see anything a later stage creates.

That single sentence explains all four rules below.

---

## Rule 1 - WHERE cannot see a SELECT alias

```sql
-- FAILS: "column lucky does not exist"
SELECT salary * 2 AS lucky
FROM   practice.employees
WHERE  lucky > 150000;
```

`WHERE` is stage 2. `lucky` is created at stage 6. At the moment `WHERE`
runs, the alias simply does not exist yet.

```sql
-- works: repeat the expression
SELECT salary * 2 AS lucky
FROM   practice.employees
WHERE  salary * 2 > 150000;
```

But `ORDER BY` (stage 8) **can** see it, because by then stage 6 has run:

```sql
SELECT salary * 2 AS lucky
FROM   practice.employees
ORDER BY lucky DESC;          -- fine
```

---

## Rule 2 - WHERE cannot filter aggregates, HAVING can

```sql
-- FAILS: "aggregate functions are not allowed in WHERE"
SELECT dept, count(*)
FROM   practice.employees
WHERE  count(*) > 4
GROUP BY dept;
```

`WHERE` runs at stage 2, before `GROUP BY` at stage 3 - the groups do not
exist yet, so there is nothing to count.

```sql
SELECT dept, count(*) AS headcount
FROM   practice.employees
GROUP BY dept
HAVING count(*) > 4;          -- stage 4, after the groups exist
```

**WHERE filters rows. HAVING filters groups.** Not a style choice - a
consequence of when each runs.

---

## Rule 3 - window functions cannot go in WHERE or HAVING

This is the important one, and it is **why CTEs matter**.

```sql
-- FAILS: "window functions are not allowed in WHERE"
SELECT emp_name, dept, salary
FROM   practice.employees
WHERE  rank() OVER (PARTITION BY dept ORDER BY salary DESC) <= 2;
```

Windows are stage 5. `WHERE` is stage 2. The rank does not exist yet.

The fix is to run the window in one query, then filter its **output** in
another - which is exactly what a CTE is for:

```sql
WITH ranked AS (
    SELECT emp_name, dept, salary,
           rank() OVER (PARTITION BY dept ORDER BY salary DESC) AS r
    FROM practice.employees
)
SELECT emp_name, dept, salary
FROM   ranked
WHERE  r <= 2;                -- now r is a plain column
```

Inside the CTE the window is computed. Outside it, `r` is just a column
like any other, so `WHERE` is happy. **Every "top N per group" query you
will ever write is this shape.**

---

## Rule 4 - DISTINCT runs after SELECT, before ORDER BY

```sql
-- FAILS: "for SELECT DISTINCT, ORDER BY expressions must appear in select list"
SELECT DISTINCT dept
FROM   practice.employees
ORDER BY salary;
```

`DISTINCT` (stage 7) has already collapsed the rows down to one column.
By the time `ORDER BY` (stage 8) runs, `salary` is gone - there would be
several salaries per surviving row and no way to choose.

---

## Questions

Answers and full explanations are in [solutions.md](solutions.md).
Try each one in psql or pgAdmin **before** looking.

**Q1.1** Without running it, say what this returns and why:

```sql
SELECT dept, count(*) AS n
FROM   practice.employees
WHERE  salary IS NOT NULL
GROUP BY dept
HAVING count(*) >= 2
ORDER BY n DESC;
```

**Q1.2** This fails. Name the stage that breaks it, then fix it two
different ways:

```sql
SELECT emp_name, salary / 1000 AS k
FROM   practice.employees
WHERE  k > 100;
```

**Q1.3** In `public.orders`, find every `order_status` that appears more
than 5000 times. Which clause must the count filter live in, and why not
the other one?

**Q1.4** Harder. Explain why this returns 3 rows, not 12:

```sql
SELECT DISTINCT dept FROM practice.employees;
```

...and why adding `, salary` to the select list changes the count.

**Q1.5** Harder. Using `public.order_items`, write a query returning the
**top 3 products by total revenue** (`sum(order_item_subtotal)`).
You cannot filter on the rank directly - explain why, then write it.
