---
title: "The issue - Missing index on foreign key"
date: 2025-01-10
tags: ["Python"]
draft: false
---

# What is all about

When you create a foreign key, you should always create an index on it (and NO, postgres do not create automaticly an index for you).

## Should You Always Index Foreign Keys in PostgreSQL?

Foreign keys are an essential part of relational database design. They ensure referential integrity by linking rows between tables. But when it comes to **performance**, many developers wonder:

> "Should I always add an index to a foreign key column?"

## Short Answer: **Almost always, yes.**

Creating an index on a foreign key **is not required** by PostgreSQL to enforce the constraint. However, **it’s highly recommended in most real-world use cases**, especially when the parent table is subject to:

- **DELETE** operations  
- **UPDATEs** to the primary/unique key  
- Frequent **JOINs** using the foreign key

Without an index, PostgreSQL may have to perform **sequential scans** on the child table, leading to major performance issues as data grows.

---

## When Indexing is Critical

### On Delete / Update
PostgreSQL must check for dependent rows in the child table. Without an index, this check results in a full table scan.

### Frequent Joins
If your queries often join the parent and child tables on the foreign key, an index helps PostgreSQL use **nested loop joins** or **hash joins** efficiently.

---

## 🧘 When You Might *Not* Need an Index

- The child table is **very small**
- The foreign key column is **rarely filtered or joined**
- The foreign key is **almost never updated or deleted**
- You're doing bulk loads and want to delay index creation for performance

Even then, you may want to add it later once data grows.

---

## Example

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id)
);

-- Index to improve FK lookups
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

## References

- [Cybertec – Foreign Key Indexing and Performance in PostgreSQL](https://www.cybertec-postgresql.com/en/index-your-foreign-key/)
- [PostgreSQL Documentation – Foreign Key Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK)

# How pgAssistant can help you ?

On the main Dashboard, you may see in the "Issues on schema" a line with a red icon : **Missing index on foreign keys**

![Result](/pgassistant-blog/images/issues.png)

Just click on it !

pgAssistant will show you the list of missing indexes on foreign keys and gives you a SQL command to create the missing index.

You should notice that pgAssistant always use the SQL command : create index **CONCURRENTLY** myindex.

If you wonder why, please take a look at 