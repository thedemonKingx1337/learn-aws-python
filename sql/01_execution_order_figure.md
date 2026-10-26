# SQL execution order

Keep this open in a split view while writing queries.
Full explanation: [01_execution_order.md](01_execution_order.md).

```text
   ┌────────────────────────────────────────────────┐
   │ 1. FROM / JOIN       build the row set         │
   ├────────────────────────────────────────────────┤
   │ 2. WHERE             filter individual rows    │
   ├────────────────────────────────────────────────┤
   │ 3. GROUP BY          collapse rows into groups │
   ├────────────────────────────────────────────────┤
   │ 4. HAVING            filter the groups         │
   ├────────────────────────────────────────────────┤
   │ 5. WINDOW FUNCTIONS  computed HERE             │
   ├────────────────────────────────────────────────┤
   │ 6. SELECT            aliases are born HERE     │
   ├────────────────────────────────────────────────┤
   │ 7. DISTINCT          de-duplicate the output   │
   ├────────────────────────────────────────────────┤
   │ 8. ORDER BY          sort                      │
   ├────────────────────────────────────────────────┤
   │ 9. LIMIT / OFFSET    cut                       │
   └────────────────────────────────────────────────┘
```
