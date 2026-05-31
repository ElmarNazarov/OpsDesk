# Architecture

OpsDesk is a Django monolith designed for internal operations teams.

## Layers

```
+-------------------+
| Browser           |
| Django Templates  |
+---------+---------+
          |
          v
+-------------------+
| Django Views      |
+---------+---------+
          |
          v
+-------------------+
| Forms / Services  |
+---------+---------+
          |
          v
+-------------------+
| Models / ORM      |
+---------+---------+
          |
          v
+-------------------+
| PostgreSQL        |
+-------------------+

+-------------------+       +-------------------+
| Celery Worker     | <---  | Redis Broker      |
+-------------------+       +-------------------+
```

## MVT + Service Layer

- **Views**: HTTP, auth, call services/selectors, render templates
- **Forms**: validation only
- **Services**: transactions, approvals, notifications, audit
- **Selectors**: reusable read queries and aggregates
- **Permissions**: `user_can_*` helpers shared by views and services

## Cross-cutting

- **Audit**: `audit_log()` on state changes
- **Notifications**: in-app + Celery email to Mailhog locally
- **Celery Beat**: overdue requests, weekly report, notification cleanup

## Infrastructure

| Component | Role |
|-----------|------|
| PostgreSQL | Primary data store |
| Redis | Cache, Celery broker/result |
| Mailhog | Local SMTP capture |

See also [permissions.md](permissions.md), [database-schema.md](database-schema.md), [workflows.md](workflows.md).
