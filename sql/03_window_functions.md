# 3. Window Functions

A `GROUP BY` **collapses** rows. A window function **keeps every row** and adds a value computed from neighbouring rows.

```sql
-- GROUP BY: 3 rows out
SELECT dept, avg(salary) FROM practice.employees GROUP BY dept;

-- window: 12 rows out, each carrying its dept average
SELECT emp_name, dept, salary,
       avg(salary) OVER (PARTITION BY dept) AS dept_avg
FROM practice.employees;
```

That is the whole idea: *same rows, extra context*.

## Anatomy of OVER

```sql
function() OVER (
    PARTITION BY   -- split into independent groups
    ORDER BY       -- order rows inside each group
    ROWS / RANGE   -- which neighbours count
)
```

- No `PARTITION BY` → the whole result is one window
- No `ORDER BY` → the frame is the entire partition
- `OVER ()` → a grand total across everything

## ROW_NUMBER vs RANK vs DENSE_RANK

`practice.employees` has deliberate salary ties. Note that **Jia, the Engineering manager on 140000, is in the Engineering department too** — managers are rows like anyone else, which is itself a thing people forget when partitioning.

```sql
SELECT emp_name, salary,
       row_number() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn,
       rank()       OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk,
       dense_rank() OVER (PARTITION BY dept ORDER BY salary DESC) AS dns
FROM practice.employees
WHERE dept = 'Engineering';
```

Verified output:

| salary | row_number | rank | dense_rank |
|--------|-----------|------|------------|
| 140000 | 1 | 1 | 1 |
| 95000 | 2 | **2** | **2** |
| 95000 | 3 | **2** | **2** |
| 88000 | 4 | **4** | **3** |
| 88000 | 5 | 4 | 3 |
| 72000 | 6 | **6** | **4** |

- **`row_number`** — always 1,2,3… and **breaks ties arbitrarily**. Asha and Bala earn the same, yet one gets 2 and the other 3, decided by nothing. The winner can change between runs. Never use it when ties matter.
- **`rank`** — ties share a number, then it **skips**: 1, 2, 2, **4**, 4, **6**. The gap is the count of rows that tied above.
- **`dense_rank`** — ties share a number, **no gaps**: 1, 2, 2, 3, 3, 4. Use it when you want "the Nth distinct value".

### Top N is where this bites

Across all three departments:

```
row_number() <= 2   ->  5 rows
rank()       <= 2   ->  7 rows
```

`rank` returns more because every tied row at position 2 qualifies. **Neither is correct in the abstract** — "top 2 employees" and "everyone in the top 2 salary bands" are different business questions. Interviewers ask this precisely because most people never notice there is a choice.

## NULLs rank FIRST on DESC — the trap

Hugo has `salary IS NULL`. Watch where he lands:

```sql
SELECT emp_name, salary,
       rank() OVER (PARTITION BY dept ORDER BY salary DESC) AS rank_default
FROM practice.employees WHERE dept = 'Sales' ORDER BY rank_default;
```

| emp_name | salary | rank |
|---|---|---|
| **Hugo** | **(null)** | **1** |
| Kemal | 135000 | 2 |
| Farid | 67000 | 3 |
| Gita | 67000 | 3 |
| Ivy | 59000 | 5 |

**The employee with no salary is ranked the top earner in Sales.** In Postgres, `ORDER BY ... DESC` defaults to `NULLS FIRST`, because NULL sorts as larger than any value. A "top 5 by revenue" dashboard silently led by rows with missing data is this bug.

Fix it explicitly:

```sql
rank() OVER (PARTITION BY dept ORDER BY salary DESC NULLS LAST)
```

Make `NULLS LAST` a habit on every descending window `ORDER BY`.

## Running totals and frames

```sql
SELECT sale_date, region, amount,
       sum(amount) OVER (PARTITION BY region ORDER BY sale_date) AS running
FROM practice.sales_daily
ORDER BY region, sale_date;
```

An `ORDER BY` inside `OVER` silently adds a default frame: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — everything up to and including this row. **That default is the only reason this is a running total** rather than a partition-wide sum.

### ROWS vs RANGE — why the gap matters

`practice.sales_daily` is **missing 2024-01-05** on purpose.

```sql
SELECT sale_date, amount,
       sum(amount) OVER (ORDER BY sale_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS by_rows,
       sum(amount) OVER (ORDER BY sale_date
            RANGE BETWEEN INTERVAL '2 days' PRECEDING
                      AND CURRENT ROW)                AS by_range
FROM practice.sales_daily
WHERE region = 'North'
ORDER BY sale_date;
```

Verified output:

| sale_date | amount | by_rows | by_range |
|---|---|---|---|
| 2024-01-01 | 100 | 100 | 100 |
| 2024-01-02 | 120 | 220 | 220 |
| 2024-01-03 | 90 | 310 | 310 |
| 2024-01-04 | 150 | 360 | 360 |
| 2024-01-06 | 130 | **370** | **280** |
| 2024-01-07 | 60 | **340** | **190** |
| 2024-01-08 | 200 | 390 | 390 |

- **`ROWS`** counts *rows*: "the 2 rows above this one", whatever their dates
- **`RANGE`** counts *values*: "rows whose date is within 2 days of this one"

They agree until the gap, diverge for two rows, then re-converge. On 2024-01-06, `ROWS` reaches back to the 3rd and 4th (370) because those are the two preceding **rows**; `RANGE` only accepts the 4th (280) because the 3rd is three days away.

**A "7-day moving average" written as `ROWS 6 PRECEDING` is wrong the moment a day has no data.** It never errors — it just quietly reports the wrong number, which is why this survives in production for years.

## LAG and LEAD

```sql
SELECT sale_date, region, amount,
       lag(amount) OVER (PARTITION BY region ORDER BY sale_date) AS prev_day,
       amount - lag(amount) OVER (PARTITION BY region ORDER BY sale_date)
           AS change
FROM practice.sales_daily;
```

`lag` looks backwards, `lead` forwards. The first row of each partition has no previous row, so `prev_day` is NULL and `change` is NULL — arithmetic with NULL is always NULL. Supply a default with `lag(amount, 1, 0)` if you want 0 instead.

## Where windows run

From lesson 1: **windows are stage 5** — after `WHERE` and `GROUP BY`, before `SELECT` and `DISTINCT`. Two consequences:

- `WHERE` cannot see a window result, so you wrap it in a CTE
- Windows see **post-aggregation** rows, so `rank() OVER (ORDER BY count(*) DESC)` alongside a `GROUP BY` is legal and genuinely useful

---

## Questions

Answers in [solutions.md](solutions.md).

**Q3.1** Return every employee with their salary and their department average on the same row. Why can `GROUP BY` not do this?

**Q3.2** Hugo has a NULL salary. What do `rank()`, `avg()` and `count()` each do with him? Run it and explain each result — they are not consistent with each other.

**Q3.3** Top 2 earners per department — once with `row_number`, once with `rank`. You should get 5 and 7 rows. Explain the difference and which you would ship.

**Q3.4** For each region in `practice.sales_daily`, show the day-over-day change and flag days where sales dropped.

**Q3.5** Harder. In `public.order_items`, rank products by total revenue **within each `order_status`** from `public.orders`. Needs a join, a `GROUP BY`, and a window over the aggregated result.

**Q3.6** Harder. Write a 3-day moving average for region North two ways — `ROWS` and `RANGE` — and explain every row where they disagree.
