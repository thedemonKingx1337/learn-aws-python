# 5. JOINs

> **Numbered 05 because it was added later. Read it second** — right after [01_execution_order.md](01_execution_order.md) and before DISTINCT. Joins are stage 1 of the pipeline; almost everything else operates on what a join produced.

Every number in this lesson was measured against your `public` retail_db.

## The problem

`public.orders` does not contain a customer's name. It contains `order_customer_id` — a number:

```sql
SELECT order_id, order_date, order_customer_id, order_status
FROM   public.orders LIMIT 3;
```

The name lives in `public.customers`. Six tables, each holding one kind of thing, linked by id columns. A **join** is how you put them back together for one query.

## INNER JOIN — only rows that match both sides

```sql
SELECT o.order_id, o.order_date,
       c.customer_fname || ' ' || c.customer_lname AS customer
FROM   public.orders o
JOIN   public.customers c ON c.customer_id = o.order_customer_id
LIMIT  5;
```

`JOIN` with no qualifier means `INNER JOIN`. Verified: this returns **68,883** rows — exactly the number of orders, so every order has a matching customer. No data was lost here.

That is luck, not a guarantee. **Always check.**

## LEFT JOIN — and the 11,452 rows INNER JOIN deletes

```sql
-- INNER: 172,198 rows
SELECT count(*) FROM public.orders o
JOIN public.order_items oi ON oi.order_item_order_id = o.order_id;

-- how many orders have NO items at all?
SELECT count(*) FROM public.orders o
LEFT JOIN public.order_items oi ON oi.order_item_order_id = o.order_id
WHERE oi.order_item_id IS NULL;        -- 11,452
```

**11,452 of your 68,883 orders have no line items** — 17% of them. An `INNER JOIN` drops every one, silently, with no error. If you wrote "orders per customer" using an inner join to `order_items`, you would be reporting a number that is wrong by a sixth and never know.

`LEFT JOIN` keeps every row from the left table and fills the right side with NULL where nothing matched:

```sql
SELECT o.order_id, o.order_status,
       count(oi.order_item_id) AS items          -- 0 for empty orders
FROM   public.orders o
LEFT   JOIN public.order_items oi ON oi.order_item_order_id = o.order_id
GROUP  BY o.order_id, o.order_status;
```

Note `count(oi.order_item_id)`, **not** `count(*)`. An empty order still produces one row (with NULLs), so `count(*)` would report 1 item where there are none. `count(col)` skips NULLs — the same rule from [02_distinct.md](02_distinct.md).

### The trap that turns LEFT back into INNER

```sql
-- looks like a LEFT JOIN, behaves like an INNER JOIN
SELECT o.order_id, oi.order_item_subtotal
FROM   public.orders o
LEFT   JOIN public.order_items oi ON oi.order_item_order_id = o.order_id
WHERE  oi.order_item_subtotal > 100;
```

The `LEFT JOIN` dutifully produces NULL rows for the 11,452 empty orders — then `WHERE` removes them, because `NULL > 100` is not true. You have written an inner join with extra steps.

**The rule:** conditions on the *left* table go in `WHERE`. Conditions on the *right* table of a `LEFT JOIN` go in the `ON` clause:

```sql
LEFT JOIN public.order_items oi
       ON oi.order_item_order_id = o.order_id
      AND oi.order_item_subtotal > 100      -- filters the join, keeps empty orders
```

`ON` decides what matches. `WHERE` deletes rows after the join. Different stages — exactly the pipeline from lesson 1.

## Fan-out — the real reason people misuse DISTINCT

```text
   orders (68,883 rows)
          │
          │  JOIN order_items ON order_id
          ▼
   result (172,198 rows)

   order 1 has 3 items  --->  order 1 appears 3 TIMES
   order 2 has 0 items  --->  order 2 DISAPPEARS
```

A join does not "add columns". It produces **one row per matching pair**. Your orders table has 68,883 rows; after joining `order_items` it has **172,198** — each order repeated once per line item.

This breaks every aggregate you then write:

```sql
-- WRONG: counts order_items rows, not orders
SELECT count(*) FROM public.orders o
JOIN public.order_items oi ON oi.order_item_order_id = o.order_id;   -- 172,198

-- right
SELECT count(DISTINCT o.order_id) FROM public.orders o
JOIN public.order_items oi ON oi.order_item_order_id = o.order_id;   -- 57,431
```

**This is the bug [02_distinct.md](02_distinct.md) warns about.** Someone sees duplicated rows, sprinkles `SELECT DISTINCT` on top, and the row count looks plausible again. But `DISTINCT` is hiding the fan-out, not fixing it — add one more column and the duplicates return.

The real fix is to **aggregate before joining**, which is what a CTE is for:

```sql
WITH order_totals AS (
    SELECT order_item_order_id AS order_id,
           sum(order_item_subtotal) AS revenue,
           count(*) AS items
    FROM   public.order_items
    GROUP  BY order_item_order_id          -- collapse to ONE row per order
)
SELECT o.order_id, o.order_status, t.revenue, t.items
FROM   public.orders o
LEFT   JOIN order_totals t ON t.order_id = o.order_id;
```

Now the right side has one row per order, so no fan-out, so no `DISTINCT` needed, and the `LEFT JOIN` keeps the 11,452 empty orders. One query, all three problems solved.

## Self-join — a table joined to itself

The `manager_id REFERENCES practice.employees(emp_id)` in `00_practice_schema.sql` makes this possible:

```sql
SELECT e.emp_name AS employee,
       m.emp_name AS manager
FROM   practice.employees e
LEFT   JOIN practice.employees m ON m.emp_id = e.manager_id;
```

Same table twice, different aliases — `e` for the employee, `m` for the manager. The aliases are **mandatory**: without them Postgres cannot tell which `emp_name` you mean.

`LEFT JOIN` matters here: Lena has `manager_id IS NULL`, so an inner join would drop the CEO from her own org chart.

A self-join gets you **one level**. For the whole chain, you need the recursive CTE in [04_ctes.md](04_ctes.md).

## The other join types, briefly

| Type | Keeps |
|---|---|
| `INNER JOIN` | only matching pairs |
| `LEFT JOIN` | all of the left, NULLs where no match |
| `RIGHT JOIN` | all of the right — rare; flip the tables and use LEFT |
| `FULL OUTER JOIN` | all of both, NULLs on either side |
| `CROSS JOIN` | every combination. Deliberate in [04_ctes.md](04_ctes.md) to attach one total row to every department |

An accidental `CROSS JOIN` — a join with a missing or wrong `ON` — turns 68,883 × 172,198 into twelve billion rows. If a query suddenly hangs, check the `ON` clause first.

## Where joins sit in the pipeline

From lesson 1: `FROM / JOIN` is **stage 1**. Everything downstream — `WHERE`, `GROUP BY`, window functions, `DISTINCT` — operates on the joined row set, fan-out and all. That is why a join bug corrupts every number in the query, and why you check row counts immediately after joining, before building anything on top.

---

## Questions

Answers in [solutions.md](solutions.md).

**Q5.1** How many customers in `public.customers` have never placed an order? Which join type finds them, and why can an inner join never answer this?

**Q5.2** Write a query returning every order with its customer's full name and city. Confirm the row count is still 68,883 and explain what it would mean if it were lower.

**Q5.3** Return each `order_status` with the number of **orders** (not line items) and total revenue. Watch the fan-out — verify your order count against 68,883.

**Q5.4** Explain why these two give different answers, and which is correct for "revenue per customer":

```sql
SELECT count(*) FROM public.orders o
JOIN public.order_items oi ON oi.order_item_order_id = o.order_id;

SELECT count(DISTINCT o.order_id) FROM public.orders o
JOIN public.order_items oi ON oi.order_item_order_id = o.order_id;
```

**Q5.5** Using `practice.employees`, list every employee beside their manager's name and the manager's salary. Why must it be a `LEFT JOIN`?

**Q5.6** Harder. Find the top 3 products by revenue **within each department**. Needs `order_items` → `products` → `categories` → `departments`, a `GROUP BY`, and a window — in that order, as separate CTEs.

**Q5.7** Harder. For every one of the 11,452 orders with no line items, return the order and its customer's name. Then explain in one sentence why this query cannot be written with an inner join anywhere in it.
