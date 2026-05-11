---
title: "Designing the Right PostgreSQL Index Using Query Plans and Statistics"
date: 2026-05-11
tags: ["postgresql", "performance", "indexes"]
draft: false
---


PostgreSQL index design is often misunderstood.

Many developers think that creating a good index simply means:

> “Create an index containing the columns from the WHERE clause.”

In reality, efficient index design is far more nuanced.

The order of columns inside a composite index matters enormously, and the best choice depends on:

- Predicate types (`=`, `>=`, `BETWEEN`, `LIKE`, etc.)
- Column selectivity
- Table size
- PostgreSQL planner statistics
- Actual execution plans

This article explains the core principles behind efficient PostgreSQL index design before showing how pgAssistant automates this process using execution plans and database statistics.

---

# Why Index Design Is Difficult

Consider the following query:

```sql
SELECT
    order_id,
    customer_id,
    employee_id,
    order_date,
    ship_country
FROM public.orders
WHERE customer_id = $1
  AND employee_id = $2
  AND order_date >= DATE $3;
```

At first glance, several index definitions may appear reasonable:

```sql
(customer_id, employee_id, order_date)
```

```sql
(order_date, customer_id, employee_id)
```

```sql
(employee_id, customer_id, order_date)
```

But these indexes do **not** behave the same way.

Choosing the correct ordering requires understanding how PostgreSQL traverses B-Tree indexes.

---

# The Fundamental Rule of B-Tree Indexes

For PostgreSQL B-Tree indexes:

1. Equality predicates should come first
2. Range predicates should come last

This is the single most important rule in multi-column index design.

---

# Equality Predicates Are Highly Selective

Predicates such as:

```sql
=
IN (...)
IS NULL
```

allow PostgreSQL to navigate directly to a very precise section of the index tree.

In our query:

```sql
customer_id = $1
employee_id = $2
```

are equality predicates.

If the index begins with these columns:

```sql
(customer_id, employee_id, ...)
```

PostgreSQL can rapidly narrow the search space.

Conceptually:

```text
customer_id = exact branch
employee_id = exact sub-branch
```

The planner can jump almost directly to the matching rows.

---

# Why Range Predicates Should Come Last

Now consider:

```sql
order_date >= DATE $3
```

This is a range predicate.

Once PostgreSQL enters a range scan inside a B-Tree index, the remaining columns become far less useful for navigation.

For example, with this index:

```sql
(order_date, customer_id, employee_id)
```

the planner must first scan all matching dates:

```text
order_date >= DATE $3
```

which may represent a very large portion of the table.

Only afterward can additional filtering occur.

This usually produces significantly more index scanning.

That is why range predicates are generally placed at the end of composite indexes.

---

# Column Order Among Equality Predicates

Once equality predicates are identified, the next challenge is:

> Which equality column should come first?

The answer depends on selectivity.

PostgreSQL exposes this information through planner statistics.

---

# PostgreSQL Statistics Drive Good Index Design

For our query, PostgreSQL statistics are:

```text
order_date [>=]:
    n_distinct=814
    null_frac=0.0000
    mcv_count=100
    histogram_bounds=101

customer_id [=]:
    n_distinct=89
    null_frac=0.0000
    mcv_count=89
    histogram_bounds=0

employee_id [=]:
    n_distinct=9
    null_frac=0.0000
    mcv_count=9
    histogram_bounds=0
```

The most important metric here is:

```text
n_distinct
```

---

# Understanding `n_distinct`

`n_distinct` estimates the number of distinct values in a column.

Higher `n_distinct` usually means:

- higher selectivity
- fewer matching rows
- better filtering efficiency

In our example:

| Column | n_distinct |
|---|---|
| customer_id | 89 |
| employee_id | 9 |

`customer_id` is significantly more selective.

Therefore, PostgreSQL benefits more from filtering by `customer_id` first.

---

# Why Selectivity Matters

Imagine the table contains 1 million rows.

Filtering by:

```text
employee_id
```

may still leave:

```text
1,000,000 / 9 ≈ 111,111 rows
```

Filtering by:

```text
customer_id
```

may reduce the result to:

```text
1,000,000 / 89 ≈ 11,236 rows
```

Starting with the most selective equality predicate drastically reduces the search space.

This improves:

- index scan efficiency
- cache locality
- heap access reduction
- execution time

---

# The Correct Index Design

Applying these principles:

1. Equality predicates first
2. Most selective equality columns first
3. Range predicates last

produces:

```sql
CREATE INDEX CONCURRENTLY
    pga_idx_orders_customer_id_employee_id_order_date
ON public.orders
    (customer_id, employee_id, order_date);
```

This ordering allows PostgreSQL to:

1. Navigate efficiently using exact matches
2. Reduce scanned rows as early as possible
3. Apply the range scan only after narrowing the search space

---

# Good Index Design Also Depends on Table Size

One of the biggest misconceptions about PostgreSQL optimization is:

> “Indexes are always faster.”

This is false.

For small tables, PostgreSQL often prefers a Sequential Scan (`Seq Scan`) even when an index exists.

Why?

Because using an index has overhead:

- traversing the B-Tree
- reading index pages
- performing heap lookups
- random I/O access

For sufficiently small tables, scanning the entire table sequentially is cheaper.

---

# Query Plans Matter More Than Theory

A theoretically perfect index is useless if PostgreSQL never uses it.

That is why index recommendation engines should never rely only on SQL syntax.

They must also inspect:

- execution plans
- estimated costs
- table statistics
- row estimates
- planner decisions

---

# The Importance of Execution Plans

The execution plan reveals how PostgreSQL actually executes a query.

For example:

```sql
EXPLAIN ANALYZE
SELECT ...
```

may show:

```text
Seq Scan on orders
```

or:

```text
Index Scan using ...
```

This distinction is critical.

A query may contain filter predicates that look index-friendly, but PostgreSQL may correctly determine that:

- the table is too small
- selectivity is too low
- too many rows would still be scanned

and therefore prefer a sequential scan.

---

# How pgAssistant Recommends Indexes

![Index Advisor](/pgassistant-blog/images/index_advisor.png)

pgAssistant does not simply parse SQL queries.

It combines multiple sources of information:

## 1. Query Plan

pgAssistant analyzes nodes in the query plan to identify candidate index columns.

---

## 2. Predicate Types

It classifies predicates into categories:

### Equality predicates

```sql
=
IN
IS NULL
```

### Range predicates

```sql
>
>=
<
<=
BETWEEN
LIKE 'prefix%'
```

Equality predicates are prioritized before range predicates.

---

## 3. Column Statistics

pgAssistant uses PostgreSQL planner statistics such as:

- `n_distinct`
- `null_frac`
- `most_common_vals`
- `most_common_freqs`
- `histogram_bounds`

to estimate column selectivity.

Columns with higher selectivity are prioritized earlier in the index definition.

---

## 4. Table Statistics

pgAssistant also evaluates table-level statistics, including:

- estimated row counts
- table size
- planner cost estimates

This is extremely important because some tables are simply too small to justify an index.

In these cases, recommending an index would create unnecessary maintenance overhead without improving performance.

---


# How pgAssistant Recommends PostgreSQL Indexes

## Why Query Syntax Alone Is Not Enough

A good recommendation depends on:

* predicate types
* column selectivity
* table statistics
* planner estimates
* execution plans
* existing indexes already used by PostgreSQL

This is precisely the approach implemented by pgAssistant.

---

# pgAssistant Uses Execution Plans First

pgAssistant starts from the PostgreSQL execution plan.

It analyzes:

```sql
EXPLAIN (ANALYZE, FORMAT JSON)
```


This is extremely important because the execution plan reveals:

* whether PostgreSQL uses a `Seq Scan`
* whether an `Index Scan` already exists
* whether residual filtering still occurs after index access
* whether planner row estimations are inaccurate
* whether a composite index could reduce heap filtering

This avoids many false-positive recommendations.

A query may look index-friendly while PostgreSQL is already using the optimal access path.

---

# pgAssistant Analyzes Existing Access Paths

The advisor first determines how PostgreSQL currently accesses the table.

Examples:

```text
Seq Scan
Index Scan
Index Only Scan
Bitmap Heap Scan
```

This distinction is critical.

## Sequential Scan Case

If PostgreSQL performs a `Seq Scan`, pgAssistant evaluates whether an index could realistically improve performance.

## Indexed Access Case

If PostgreSQL already uses an index, pgAssistant does not stop there.

It also analyzes:

* `Index Cond`
* `Filter`
* `Recheck Cond`
* `Rows Removed by Filter`

This allows pgAssistant to detect situations such as:

```text
Index Scan using idx_customer on orders
  Index Cond: (customer_id = 42)
  Filter: (employee_id = 5)
```

In this case, PostgreSQL uses an index, but still visits many rows that are later discarded by the executor.

pgAssistant can therefore recommend a more selective composite index such as:

```sql
(customer_id, employee_id)
```

instead of considering the existing index “good enough”.

---

# Predicate Classification

Once predicates are extracted from the execution plan, pgAssistant classifies them by operator type.

Internally, predicates are ranked according to B-Tree efficiency.

## Equality Predicates

Highest priority:

```sql
=
IN
IS NULL
```

These predicates allow PostgreSQL to navigate directly to a very small portion of the index tree.

---

## Prefix Search Predicates

Second priority:

```sql
LIKE 'abc%'
```

Prefix searches can still benefit efficiently from B-Tree traversal.

---

## Range Predicates

Lowest priority:

```sql
>
>=
<
<=
BETWEEN
```

Once PostgreSQL enters a range scan, subsequent columns become far less effective for index navigation.

That is why range predicates are typically placed last in composite indexes.

---

# How pgAssistant Orders Index Columns

After classifying predicates, pgAssistant computes candidate index ordering.

The internal ordering logic is:

```text
1. Equality predicates first
2. Prefix predicates second
3. Range predicates last
4. Inside each category:
   highest cardinality first
```

This logic is implemented directly inside:

```python
reorder_index_candidate_columns()
```

The advisor therefore builds indexes that align with PostgreSQL B-Tree traversal behavior.

---

# Why Column Cardinality Matters

pgAssistant uses PostgreSQL statistics to estimate selectivity.

The most important metric is:

```text
n_distinct
```

which estimates the number of distinct values in a column.

Higher cardinality usually means:

* fewer matching rows
* better filtering
* smaller index scan ranges

For our example:

```text
customer_id [=]: n_distinct=89
employee_id [=]: n_distinct=9
order_date [>=]: n_distinct=814
```

Although `order_date` has the highest cardinality, it is a range predicate and therefore placed last.

Among equality predicates:

```text
customer_id > employee_id
```

because:

```text
89 > 9
```

The final ordering becomes:

```sql
(customer_id, employee_id, order_date)
```

---

# pgAssistant Uses PostgreSQL Statistics

pgAssistant enriches every recommendation using planner statistics extracted from PostgreSQL.

Examples include:

* `n_distinct`
* `null_frac`
* `most_common_vals`
* `most_common_freqs`
* `histogram_bounds`

The advisor even exposes these statistics in its recommendation reasoning.

Example:

```text
customer_id [=]: n_distinct=89, null_frac=0.0000
employee_id [=]: n_distinct=9, null_frac=0.0000
order_date [>=]: n_distinct=814
```

This makes the recommendation transparent and explainable.

---

# pgAssistant Also Uses Table Statistics

An index is not always beneficial.

This is one of the most important concepts in PostgreSQL optimization.

For small tables, PostgreSQL often correctly prefers:

```text
Seq Scan
```

instead of:

```text
Index Scan
```

because:

* sequential reads are cheap
* index traversal has overhead
* heap fetches introduce random I/O
* scanning the entire table may cost less

This is why pgAssistant also evaluates:

* estimated row counts
* table size
* planner costs
* execution frequency
* workload intensity

The advisor does not blindly recommend indexes whenever a sequential scan appears.

---

# Detecting Inefficient Indexed Access

One particularly powerful aspect of pgAssistant is its ability to analyze residual filtering.

For indexed scans, the advisor evaluates:

```text
Rows Removed by Filter
```

If PostgreSQL retrieves many tuples from the index only to discard them afterward, pgAssistant detects that the current index may be incomplete.

Internally, the advisor computes:

```text
Residual filter kept X% of tuples visited
```

This helps identify situations where adding an additional column to a composite index could drastically reduce heap filtering.

---

# Detecting Planner Estimation Problems

pgAssistant also compares:

```text
plan_rows
vs
actual_rows
```

Large estimation gaps may indicate:

* stale statistics
* data skew
* correlation issues
* missing extended statistics

This additional analysis improves the reliability of recommendations.

---

# The pgAssistant Recommendation Algorithm

Conceptually, pgAssistant follows this workflow:

```text
1. Analyze EXPLAIN ANALYZE JSON plan
2. Detect access paths
3. Extract predicates from:
   - Index Cond
   - Filter
   - Recheck Cond
4. Classify predicates by operator type
5. Rank predicates for B-Tree efficiency
6. Use PostgreSQL statistics to estimate selectivity
7. Order columns by:
   - predicate class
   - cardinality
8. Evaluate table statistics
9. Evaluate execution costs
10. Detect residual filtering
11. Compare against existing indexes
12. Recommend index only if beneficial
```

---

# Example: Final Recommendation

Given:

```sql
SELECT
    order_id,
    customer_id,
    employee_id,
    order_date,
    ship_country
FROM public.orders
WHERE customer_id = $1
  AND employee_id = $2
  AND order_date >= DATE $3;
```

pgAssistant evaluates:

| Column      | Predicate | Priority | n_distinct |
| ----------- | --------- | -------- | ---------- |
| customer_id | `=`       | Equality | 89         |
| employee_id | `=`       | Equality | 9          |
| order_date  | `>=`      | Range    | 814        |

The advisor therefore generates:

```sql
CREATE INDEX CONCURRENTLY
    "pga_idx_orders_customer_id_employee_id_order_date"
ON "public"."orders"
    ("customer_id", "employee_id", "order_date");
```

This ordering follows PostgreSQL B-Tree optimization principles while also considering:

* planner statistics
* table characteristics
* execution plan behavior
* residual filtering
* existing indexes already in use
