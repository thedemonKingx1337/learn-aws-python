# 4. CTEs — including multiple and recursive

A CTE (Common Table Expression) is a **named subquery written before the query that uses it**.

```sql
WITH eng AS (
    SELECT * FROM practice.employees WHERE dept = 'Engineering'
)
SELECT emp_name, salary FROM eng ORDER BY salary DESC;
```

`eng` exists only for the duration of this one statement. Nothing is stored, nothing is created, nothing to clean up.

## Why CTEs actually matter

Readability is the advertised reason. The real reason is **lesson 1**: window functions run at stage 5, so `WHERE` can never see them. A CTE gives the window somewhere to finish before you filter it.

```sql
-- FAILS: window functions are not allowed in WHERE
SELECT emp_name, dept, salary
FROM   practice.employees
WHERE  rank() OVER (PARTITION BY dept ORDER BY salary DESC) <= 2;

-- works: the CTE finishes the window, the outer query filters a plain column
WITH ranked AS (
    SELECT emp_name, dept, salary,
           rank() OVER (PARTITION BY dept ORDER BY salary DESC) AS r
    FROM practice.employees
)
SELECT emp_name, dept, salary
FROM   ranked
WHERE  r <= 2;
```

Inside the CTE, `r` is a window result. Outside it, `r` is just a column. **Every "top N per group" query is this shape.**

## Multiple CTEs — the part you asked for

One `WITH`, then **comma-separated** names. You do **not** repeat the `WITH` keyword:

```sql
WITH
dept_totals AS (
    SELECT dept, sum(salary) AS total_salary, count(*) AS headcount
    FROM   practice.employees
    GROUP  BY dept
),
company AS (
    SELECT sum(total_salary) AS grand_total FROM dept_totals
)
SELECT d.dept,
       d.total_salary,
       d.headcount,
       round(100.0 * d.total_salary / c.grand_total, 1) AS pct_of_payroll
FROM   dept_totals d
CROSS  JOIN company c
ORDER  BY pct_of_payroll DESC;
```

Three rules that cover almost everything:

1. **`WITH` appears once.** Separate the names with commas. A second `WITH` is a syntax error — the single most common beginner mistake here.
2. **A later CTE can read an earlier one.** `company` reads `dept_totals`. The reverse is not allowed — they resolve top to bottom.
3. **The final `SELECT` can read any of them**, and can join them to each other and to real tables.

### Think of it as a pipeline

```
   ┌─────────────┐
   │  base_sales │  reads the raw tables
   └─────────────┘
          │
          ▼
   ┌─────────────┐
   │  ranked     │  reads base_sales
   └─────────────┘
          │
          ▼
   ┌─────────────┐
   │ final SELECT│  reads ranked
   └─────────────┘
```

Each step does **one** transformation and gets a name saying what it holds. This is why CTEs beat nested subqueries for anything non-trivial: a 4-level nested subquery has to be read inside-out, while four CTEs read top-to-bottom like steps in a recipe.

Here is that pipeline on the real data:

```sql
WITH
base_sales AS (
    SELECT oi.order_item_product_id AS product_id,
           sum(oi.order_item_subtotal) AS revenue
    FROM   public.order_items oi
    GROUP  BY oi.order_item_product_id
),
ranked AS (
    SELECT product_id, revenue,
           rank() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM   base_sales
)
SELECT r.revenue_rank, p.product_name, round(r.revenue::numeric, 2) AS revenue
FROM   ranked r
JOIN   public.products p ON p.product_id = r.product_id
WHERE  r.revenue_rank <= 10
ORDER  BY r.revenue_rank;
```

Note the division of labour: `base_sales` aggregates, `ranked` ranks, the final `SELECT` joins for names and filters. No step does two jobs.

## A CTE can be used more than once

```sql
WITH dept_avg AS (
    SELECT dept, avg(salary) AS avg_sal
    FROM   practice.employees
    GROUP  BY dept
)
SELECT e.emp_name, e.dept, e.salary, d.avg_sal
FROM   practice.employees e
JOIN   dept_avg d ON d.dept = e.dept
WHERE  e.salary > d.avg_sal;
```

Written as a subquery, `dept_avg` would have to be repeated or correlated. Named once, it is referenced wherever needed.

## Recursive CTEs

For hierarchies — org charts, category trees, bills of materials. `practice.employees` has `manager_id` precisely for this.

```sql
WITH RECURSIVE org AS (
    -- anchor: start at the top (no manager)
    SELECT emp_id, emp_name, manager_id, 1 AS level
    FROM   practice.employees
    WHERE  manager_id IS NULL

    UNION ALL

    -- recursive part: everyone reporting to someone already found
    SELECT e.emp_id, e.emp_name, e.manager_id, o.level + 1
    FROM   practice.employees e
    JOIN   org o ON e.manager_id = o.emp_id
)
SELECT level, repeat('  ', level - 1) || emp_name AS chart
FROM   org
ORDER  BY level, emp_name;
```

The shape is always the same:

1. **Anchor** — the starting rows (`manager_id IS NULL`, i.e. Lena)
2. **`UNION ALL`**
3. **Recursive part** — joins the table back to the CTE's *own name*, finding the next level each pass
4. Stops automatically when a pass returns no rows

`WITH RECURSIVE` is required even if only one CTE in the list is recursive.

**The classic failure is an infinite loop.** If your data has a cycle (A manages B, B manages A), this never terminates. Guard it by carrying a depth column and adding `WHERE level < 10`.

## One Postgres-specific gotcha

Before Postgres 12, a CTE was always an **optimisation fence** — materialised separately, never merged into the outer query. People used `WITH` deliberately to force that.

From Postgres 12 on, a CTE used **once** and not recursive is **inlined** by default, like a subquery. To get the old behaviour back:

```sql
WITH ranked AS MATERIALIZED ( ... )
WITH ranked AS NOT MATERIALIZED ( ... )
```

Worth knowing because old StackOverflow answers about "CTEs are always slower" predate Postgres 12 and are now wrong.

---

## Questions

Answers in [solutions.md](solutions.md).

**Q4.1** Rewrite this nested subquery as a CTE. Which reads more easily, and why?

```sql
SELECT * FROM (
    SELECT dept, avg(salary) AS a FROM practice.employees GROUP BY dept
) x WHERE x.a > 80000;
```

**Q4.2** Write **two** CTEs: one giving each department's headcount, one giving company headcount. Return each department's share of total headcount as a percentage.

**Q4.3** Using `public.orders` and `public.order_items`, write a 3-CTE pipeline: revenue per order → revenue per customer → the top 10 customers by revenue, with names from `public.customers`.

**Q4.4** Fix this. There are **two** separate errors:

```sql
WITH a AS (SELECT dept, count(*) c FROM practice.employees GROUP BY dept)
WITH b AS (SELECT max(c) m FROM a)
SELECT * FROM a JOIN b ON a.c = b.m;
```

**Q4.5** Recursive. Return every employee with their **full management chain** as text, e.g. `Lena > Jia > Asha`.

**Q4.6** Harder. For each department, return the employee earning closest to that department's average salary. Needs a CTE for the average, a window for the distance, and a filter on the window result.

**Q4.7** Harder. Using `public.orders`, write a recursive CTE that generates **every date** between the first and last order date, then left-join the real order counts so days with zero orders show as 0. (This is the standard "fill the calendar gaps" pattern — and it is why `RANGE` beats `ROWS` from lesson 3.)
