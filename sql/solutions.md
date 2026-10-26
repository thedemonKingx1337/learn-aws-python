# Solutions

Every query here was run against the live database before being written down. Where a result is quoted, it is the real output.

---

# Lesson 1 — Execution Order

### Q1.1

Returns one row per department that has **at least 2 employees with a non-NULL salary**, ordered by headcount descending.

The pipeline: `FROM` builds 12 rows → `WHERE` drops Hugo (NULL salary) leaving 11 → `GROUP BY` collapses to 3 departments → `HAVING` keeps groups with ≥2 → `SELECT` creates the alias `n` → `ORDER BY n` works because stage 8 runs after stage 6.

Executive has only Lena, so it is dropped by `HAVING`. Verified result: **Engineering 6, Sales 4** (Sales keeps Kemal, Farid, Gita and Ivy; only Hugo is removed by the NULL filter).

### Q1.2

**Stage 2 breaks it.** `WHERE` runs before `SELECT`, so the alias `k` does not exist yet.

```sql
-- fix 1: repeat the expression
SELECT emp_name, salary / 1000 AS k
FROM   practice.employees
WHERE  salary / 1000 > 100;

-- fix 2: let a subquery/CTE create the alias first
WITH t AS (SELECT emp_name, salary / 1000 AS k FROM practice.employees)
SELECT * FROM t WHERE k > 100;
```

Fix 1 is usually better — the optimiser handles the repetition, and it avoids an extra scope.

### Q1.3

```sql
SELECT order_status, count(*) AS n
FROM   public.orders
GROUP  BY order_status
HAVING count(*) > 5000
ORDER  BY n DESC;
```

The filter must be in **`HAVING`**, not `WHERE`. `WHERE` runs at stage 2, before `GROUP BY` at stage 3 — the groups do not exist yet, so there is nothing to count. `WHERE` filters rows; `HAVING` filters groups.

### Q1.4

`SELECT DISTINCT dept` returns **3** rows — there are only 3 distinct department values across the 12 employees.

Adding `, salary` gives **9** rows, not 12. `DISTINCT` operates on the **whole output row**, so two employees collapse only if *both* dept and salary match. Exactly three pairs do:

- Asha / Bala — Engineering, 95000
- Chen / Dmitri — Engineering, 88000
- Farid / Gita — Sales, 67000

12 rows minus 3 collapsed duplicates = **9**. Hugo survives as his own row: his NULL salary is distinct from every number, and he is the only NULL.

**More columns can only ever increase the row count** — 3 becomes 9, never fewer.

### Q1.5

You cannot write `WHERE rank() OVER (...) <= 3` because windows are stage 5 and `WHERE` is stage 2. Wrap it:

```sql
WITH revenue AS (
    SELECT order_item_product_id AS product_id,
           sum(order_item_subtotal) AS total_revenue
    FROM   public.order_items
    GROUP  BY order_item_product_id
),
ranked AS (
    SELECT product_id, total_revenue,
           rank() OVER (ORDER BY total_revenue DESC) AS r
    FROM   revenue
)
SELECT r.r, p.product_name, round(r.total_revenue::numeric, 2) AS revenue
FROM   ranked r
JOIN   public.products p ON p.product_id = r.product_id
WHERE  r.r <= 3
ORDER  BY r.r;
```

---

# Lesson 2 — DISTINCT

### Q2.1

- `SELECT DISTINCT plan` → **2** rows (`free`, `pro`)
- `SELECT DISTINCT email, plan` → **5** rows

The second is larger because `DISTINCT` de-duplicates the **pair**. The 7 rows contain 5 distinct pairs: `(a@x.com, free)`, `(a@x.com, pro)`, `(b@x.com, pro)`, `(NULL, free)`, `(NULL, pro)`.

### Q2.2

`count(DISTINCT email)` ignores NULLs entirely, while `SELECT DISTINCT email` keeps all NULLs collapsed into one surviving row — so the row count includes a NULL that the count does not.

### Q2.3

```sql
SELECT count(DISTINCT order_customer_id)                    AS customers,
       count(DISTINCT (order_customer_id, order_status))    AS pairs
FROM   public.orders;
```

Pairs is larger because a single customer can place orders in several different statuses — each combination is a distinct pair, so one customer can contribute many.

### Q2.4

```sql
-- Postgres shortcut
SELECT DISTINCT ON (order_customer_id)
       order_customer_id, order_id, order_date, order_status
FROM   public.orders
ORDER  BY order_customer_id, order_date DESC
LIMIT  10;

-- portable window-function form
WITH ranked AS (
    SELECT order_customer_id, order_id, order_date, order_status,
           row_number() OVER (PARTITION BY order_customer_id
                              ORDER BY order_date DESC) AS rn
    FROM   public.orders
)
SELECT order_customer_id, order_id, order_date, order_status
FROM   ranked WHERE rn = 1
ORDER  BY order_customer_id
LIMIT  10;
```

`DISTINCT ON` requires `ORDER BY` to begin with the same expression. The window form is longer but works on Athena, Spark SQL and every other engine.

### Q2.5

The `DISTINCT` is **useless and misleading**. `GROUP BY customer_state` has already produced exactly one row per state, so there are no duplicates left for `DISTINCT` to remove — it runs at stage 7, long after the grouping at stage 3.

It is not changing the numbers; it is advertising that the author did not know why the numbers looked wrong. If the counts are genuinely wrong, the cause is elsewhere (usually a join fanning out rows before the grouping). Delete the `DISTINCT` and investigate the real cause.

```sql
SELECT customer_state, count(*) AS n
FROM   public.customers
GROUP  BY customer_state
ORDER  BY n DESC;
```

---

# Lesson 3 — Window Functions

### Q3.1

```sql
SELECT emp_name, dept, salary,
       avg(salary) OVER (PARTITION BY dept) AS dept_avg
FROM   practice.employees;
```

`GROUP BY` cannot do it because it **collapses** rows — you would get 3 rows, one per department, and lose every individual name. A window keeps all 12 rows and attaches the group value to each. That is the defining difference.

### Q3.2

```sql
SELECT emp_name, salary,
       rank()  OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_default,
       rank()  OVER (PARTITION BY dept ORDER BY salary DESC NULLS LAST) AS rank_fixed,
       avg(salary)   OVER (PARTITION BY dept) AS dept_avg,
       count(salary) OVER (PARTITION BY dept) AS n_with_salary,
       count(*)      OVER (PARTITION BY dept) AS n_rows
FROM   practice.employees
WHERE  dept = 'Sales';
```

Three different behaviours, and they are **not consistent with each other**:

- **`rank()`** — Hugo ranks **1**, because `DESC` defaults to `NULLS FIRST` and NULL sorts above every value. `NULLS LAST` moves him to the bottom.
- **`avg(salary)`** — Hugo is **skipped**. The average is over 3 values, not 4. Aggregates ignore NULL inputs.
- **`count(salary)`** = 3 but **`count(*)`** = 4. The first counts non-NULL values, the second counts rows.

So the same NULL is simultaneously ranked first, excluded from the mean, and counted-or-not depending on which `count` you wrote.

### Q3.3

```sql
WITH r AS (
    SELECT emp_name, dept, salary,
           row_number() OVER (PARTITION BY dept ORDER BY salary DESC NULLS LAST) AS rn,
           rank()       OVER (PARTITION BY dept ORDER BY salary DESC NULLS LAST) AS rk
    FROM practice.employees
)
SELECT * FROM r WHERE rn <= 2;   -- 5 rows
SELECT * FROM r WHERE rk <= 2;   -- 7 rows
```

`rank` returns 7 because tied rows all share position 2 and all qualify. `row_number` returns exactly 2 per department by inventing an arbitrary tiebreak.

**Ship `rank` (or `dense_rank`)** unless there is a documented rule for breaking ties. `row_number` silently picks a winner, and the winner can change between runs — which is indefensible if the result drives pay, promotion or a leaderboard.

### Q3.4

```sql
SELECT sale_date, region, amount,
       lag(amount) OVER (PARTITION BY region ORDER BY sale_date) AS prev_day,
       amount - lag(amount) OVER (PARTITION BY region ORDER BY sale_date) AS change,
       CASE
           WHEN amount < lag(amount) OVER (PARTITION BY region ORDER BY sale_date)
           THEN 'DROP' ELSE ''
       END AS flag
FROM   practice.sales_daily
ORDER  BY region, sale_date;
```

The first day of each region has no previous row, so `change` is NULL and the `CASE` yields `''` — a NULL comparison is never true.

### Q3.5

```sql
WITH product_revenue AS (
    SELECT o.order_status,
           oi.order_item_product_id AS product_id,
           sum(oi.order_item_subtotal) AS revenue
    FROM   public.order_items oi
    JOIN   public.orders o ON o.order_id = oi.order_item_order_id
    GROUP  BY o.order_status, oi.order_item_product_id
),
ranked AS (
    SELECT order_status, product_id, revenue,
           rank() OVER (PARTITION BY order_status
                        ORDER BY revenue DESC NULLS LAST) AS r
    FROM   product_revenue
)
SELECT rk.order_status, rk.r, p.product_name,
       round(rk.revenue::numeric, 2) AS revenue
FROM   ranked rk
JOIN   public.products p ON p.product_id = rk.product_id
WHERE  rk.r <= 3
ORDER  BY rk.order_status, rk.r;
```

Note the window runs **over the aggregated rows** — `product_revenue` has already collapsed to one row per (status, product), and the window ranks within those.

### Q3.6

```sql
SELECT sale_date, amount,
       round(avg(amount) OVER (ORDER BY sale_date
             ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS avg_rows,
       round(avg(amount) OVER (ORDER BY sale_date
             RANGE BETWEEN INTERVAL '2 days' PRECEDING
                       AND CURRENT ROW), 2)                AS avg_range
FROM   practice.sales_daily
WHERE  region = 'North'
ORDER  BY sale_date;
```

They agree through 2024-01-04, then diverge on **01-06** and **01-07**, then re-converge on **01-08**.

Cause: 2024-01-05 is missing. On 01-06, `ROWS` averages the 01-03/01-04/01-06 rows (three rows, ignoring that one is three days old), while `RANGE` averages only 01-04 and 01-06 (two rows, because 01-03 falls outside the 2-day window). By 01-08 the preceding two rows are 01-06 and 01-07, which are also within 2 days, so both agree again.

**`RANGE` is the honest answer for anything time-based.**

---

# Lesson 4 — CTEs

### Q4.1

```sql
WITH dept_avg AS (
    SELECT dept, avg(salary) AS a
    FROM   practice.employees
    GROUP  BY dept
)
SELECT * FROM dept_avg WHERE a > 80000;
```

The CTE reads top-to-bottom: compute averages, then filter. The nested form reads inside-out, and the alias `x` tells the reader nothing. With one level the difference is cosmetic; at three levels it decides whether the query is maintainable.

### Q4.2

```sql
WITH
dept_counts AS (
    SELECT dept, count(*) AS headcount
    FROM   practice.employees
    GROUP  BY dept
),
company AS (
    SELECT sum(headcount) AS total FROM dept_counts
)
SELECT d.dept, d.headcount,
       round(100.0 * d.headcount / c.total, 1) AS pct
FROM   dept_counts d
CROSS  JOIN company c
ORDER  BY pct DESC;
```

`company` reads `dept_counts` — a later CTE may reference an earlier one. `CROSS JOIN` is right because `company` is a single row that every department row needs.

### Q4.3

```sql
WITH
order_revenue AS (
    SELECT oi.order_item_order_id AS order_id,
           sum(oi.order_item_subtotal) AS revenue
    FROM   public.order_items oi
    GROUP  BY oi.order_item_order_id
),
customer_revenue AS (
    SELECT o.order_customer_id AS customer_id,
           sum(r.revenue) AS revenue,
           count(*)       AS orders
    FROM   order_revenue r
    JOIN   public.orders o ON o.order_id = r.order_id
    GROUP  BY o.order_customer_id
),
top_customers AS (
    SELECT customer_id, revenue, orders,
           rank() OVER (ORDER BY revenue DESC NULLS LAST) AS r
    FROM   customer_revenue
)
SELECT t.r, c.customer_fname || ' ' || c.customer_lname AS customer,
       t.orders, round(t.revenue::numeric, 2) AS revenue
FROM   top_customers t
JOIN   public.customers c ON c.customer_id = t.customer_id
WHERE  t.r <= 10
ORDER  BY t.r;
```

Each CTE does exactly one job: aggregate per order, aggregate per customer, rank. The final `SELECT` only joins for names and filters.

### Q4.4

Two errors:

1. **`WITH` is written twice.** It appears once; subsequent CTEs are comma-separated.
2. **`SELECT *` with a join on `a.c = b.m` is ambiguous** once both are selected, and more importantly the query lists `a` and `b` without aliasing the count column cleanly.

```sql
WITH
a AS (SELECT dept, count(*) AS c FROM practice.employees GROUP BY dept),
b AS (SELECT max(c) AS m FROM a)
SELECT a.dept, a.c
FROM   a
JOIN   b ON a.c = b.m;
```

This returns the department(s) with the largest headcount.

### Q4.5

```sql
WITH RECURSIVE chain AS (
    SELECT emp_id, emp_name, manager_id,
           emp_name::text AS path,
           1 AS level
    FROM   practice.employees
    WHERE  manager_id IS NULL

    UNION ALL

    SELECT e.emp_id, e.emp_name, e.manager_id,
           c.path || ' > ' || e.emp_name,
           c.level + 1
    FROM   practice.employees e
    JOIN   chain c ON e.manager_id = c.emp_id
)
SELECT level, emp_name, path
FROM   chain
ORDER  BY path;
```

The anchor starts at Lena (`manager_id IS NULL`) with her own name as the path. Each recursive pass appends a name. `::text` on the anchor matters — without it Postgres infers `varchar` and the concatenation can fail to match types.

### Q4.6

```sql
WITH
dept_avg AS (
    SELECT dept, avg(salary) AS avg_sal
    FROM   practice.employees
    WHERE  salary IS NOT NULL
    GROUP  BY dept
),
distances AS (
    SELECT e.emp_name, e.dept, e.salary, d.avg_sal,
           abs(e.salary - d.avg_sal) AS gap,
           row_number() OVER (PARTITION BY e.dept
                              ORDER BY abs(e.salary - d.avg_sal)) AS rn
    FROM   practice.employees e
    JOIN   dept_avg d ON d.dept = e.dept
    WHERE  e.salary IS NOT NULL
)
SELECT dept, emp_name, salary, round(avg_sal, 2) AS dept_avg, round(gap, 2) AS gap
FROM   distances
WHERE  rn = 1
ORDER  BY dept;
```

Hugo is excluded twice over — once from the average, once from the candidates — because `abs(NULL - x)` is NULL and would sort first under `ASC NULLS LAST`… actually it sorts **last** on `ASC`, but excluding him explicitly states the intent rather than relying on NULL ordering.

### Q4.7

The recursive form, as asked:

```sql
WITH RECURSIVE bounds AS (
    SELECT min(order_date)::date AS d_min, max(order_date)::date AS d_max
    FROM   public.orders
),
calendar AS (
    SELECT d_min AS d, d_max FROM bounds
    UNION ALL
    SELECT (d + 1)::date, d_max FROM calendar WHERE d < d_max
),
daily AS (
    SELECT order_date::date AS d, count(*) AS orders
    FROM   public.orders
    GROUP  BY order_date::date
)
SELECT c.d, coalesce(dl.orders, 0) AS orders
FROM   calendar c
LEFT   JOIN daily dl ON dl.d = c.d
ORDER  BY c.d;
```

In practice you would use `generate_series`, which is shorter and faster:

```sql
SELECT g.d::date, coalesce(dl.orders, 0) AS orders
FROM   generate_series(
           (SELECT min(order_date)::date FROM public.orders),
           (SELECT max(order_date)::date FROM public.orders),
           interval '1 day') AS g(d)
LEFT   JOIN (
           SELECT order_date::date AS d, count(*) AS orders
           FROM public.orders GROUP BY order_date::date
       ) dl ON dl.d = g.d::date
ORDER  BY 1;
```

The recursive version is worth writing once to understand the pattern, because engines without `generate_series` need it. The `LEFT JOIN` plus `coalesce(..., 0)` is the part that actually fills the gaps — and it is the correct fix for the `ROWS` vs `RANGE` problem from lesson 3: with no gaps in the data, `ROWS` and `RANGE` agree.

---

# Lesson 5 — JOINs

### Q5.1

```sql
SELECT c.customer_id, c.customer_fname, c.customer_lname
FROM   public.customers c
LEFT   JOIN public.orders o ON o.order_customer_id = c.customer_id
WHERE  o.order_id IS NULL;
```

**30 customers.** An inner join can never answer this: it returns only rows that matched, and these customers matched nothing. You have to keep the unmatched rows first (`LEFT JOIN`), then filter for the NULLs the join produced. The `IS NULL` test is reading the join's own failure.

### Q5.2

```sql
SELECT o.order_id, o.order_date, o.order_status,
       c.customer_fname || ' ' || c.customer_lname AS customer,
       c.customer_city
FROM   public.orders o
JOIN   public.customers c ON c.customer_id = o.order_customer_id;
```

**68,883 rows** — unchanged, so every order matched exactly one customer. A *lower* count would mean orders referencing a `customer_id` that does not exist in `customers` (orphans, silently deleted by the inner join). A *higher* count would mean `customers.customer_id` is not unique, duplicating orders.

Checking the count after a join is the cheapest bug detector in SQL.

### Q5.3

```sql
WITH order_totals AS (
    SELECT order_item_order_id AS order_id,
           sum(order_item_subtotal) AS revenue
    FROM   public.order_items
    GROUP  BY order_item_order_id
)
SELECT o.order_status,
       count(*)                                AS orders,
       round(coalesce(sum(t.revenue),0)::numeric, 2) AS revenue
FROM   public.orders o
LEFT   JOIN order_totals t ON t.order_id = o.order_id
GROUP  BY o.order_status
ORDER  BY orders DESC;
```

The order counts sum to **68,883**. Aggregating `order_items` *first* means the right side has one row per order, so there is no fan-out and `count(*)` is honestly counting orders. `LEFT JOIN` keeps the 11,452 empty orders, and `coalesce` turns their NULL revenue into 0.

### Q5.4

- First: **172,198** — counts rows *after* fan-out, i.e. line items.
- Second: **57,431** — counts distinct orders that have at least one item.

Neither is right for "revenue per customer". The first double-counts; the second silently excludes the 11,452 orders with no items. The correct approach aggregates before joining (see Q5.3 and Q4.3) rather than patching the symptom with `DISTINCT`.

Sanity check: 68,883 − 11,452 = **57,431**. The numbers agree.

### Q5.5

```sql
SELECT e.emp_name AS employee, e.dept,
       m.emp_name AS manager, m.salary AS manager_salary
FROM   practice.employees e
LEFT   JOIN practice.employees m ON m.emp_id = e.manager_id
ORDER  BY m.emp_name NULLS FIRST, e.emp_name;
```

`LEFT JOIN` returns **12** rows; `INNER JOIN` returns **11**. The missing one is **Lena**, whose `manager_id` is NULL — the CEO vanishes from her own org chart under an inner join. Any hierarchy query that must include the root needs a left join (or the recursive CTE from lesson 4).

### Q5.6

```sql
WITH
product_revenue AS (
    SELECT oi.order_item_product_id AS product_id,
           sum(oi.order_item_subtotal) AS revenue
    FROM   public.order_items oi
    GROUP  BY oi.order_item_product_id
),
by_department AS (
    SELECT d.department_name, p.product_name, pr.revenue
    FROM   product_revenue pr
    JOIN   public.products   p ON p.product_id = pr.product_id
    JOIN   public.categories c ON c.category_id = p.product_category_id
    JOIN   public.departments d ON d.department_id = c.category_department_id
),
ranked AS (
    SELECT department_name, product_name, revenue,
           rank() OVER (PARTITION BY department_name
                        ORDER BY revenue DESC NULLS LAST) AS r
    FROM   by_department
)
SELECT department_name, r, product_name, round(revenue::numeric, 2) AS revenue
FROM   ranked
WHERE  r <= 3
ORDER  BY department_name, r;
```

Order matters: aggregate first (one row per product), then join for names, then rank. Joining before aggregating would fan out and inflate every revenue figure.

### Q5.7

```sql
SELECT o.order_id, o.order_date, o.order_status,
       c.customer_fname || ' ' || c.customer_lname AS customer
FROM   public.orders o
LEFT   JOIN public.order_items oi ON oi.order_item_order_id = o.order_id
JOIN   public.customers c ON c.customer_id = o.order_customer_id
WHERE  oi.order_item_id IS NULL;
```

**11,452 rows.** The join to `order_items` must be a `LEFT JOIN`, because the rows you want are precisely the ones that *failed* to match — an inner join deletes them before you can test for them. (The join to `customers` can stay inner, since every order has a customer.)

In one sentence: you cannot filter for a non-match using a join type that only returns matches.

