---
title: "Understanding the myqueries.json file"
date: 2025-01-10
tags: ["myqueries"]
draft: false
---

**myqueries.json** file is used to store your helpfull queries. 

Each querie you add to the json file can be searched and executed by pgAssistant.

The JSON format is very simple :
```json
        {
            "id": "db_version",
            "description": "Database version",
            "category": "Database",        
            "sql": "SHOW server_version;",
            "type": "select"
            "reference": "https://www.postgresql.org/docs/current/sql-show.html"
        }
```

- **id** A unique ID of the query
- **description** The description of your SQL query
- **categorie** A SQL category like Database, Issue, Table, Index or whatever you want
- **sql** The SQL query ended with a ";"
- **reference** An URL on the query documentation or your project documentation
- **type** 2 sql types are alowed 
   - select : performing a select
   - param_query : a select query with parameters. Each parameter must be in the format $1, $2, etc.
