# OpsDesk

Internal company operations portal built with Django.

## Features

- Role-based dashboards (Employee, Manager, Ops, Admin)
- Employee requests with categories, priorities, and status workflow
- Multi-step approval workflows (Manager, HR, Ops)
- In-app notifications and email via Celery
- Immutable audit logging
- Asset management and equipment fulfillment
- Reports with Chart.js
- Dockerized local development stack

## Tech Stack

- Python 3.12+, Django 5.x
- PostgreSQL 16, Redis 7, Celery
- pytest, factory_boy, coverage, ruff
- Bootstrap 5, Alpine.js, Chart.js
- Docker & Docker Compose
- GitHub Actions CI

## Architecture

OpsDesk uses a Django monolith with a **service layer** for business workflows and **selectors** for query logic. Views stay thin; permissions are enforced in services and `permissions.py`.

See [docs/architecture.md](docs/architecture.md) for details.

## Business Workflows

See [docs/workflows.md](docs/workflows.md) for vacation, equipment, software access, approval, fulfillment, and cancellation flows.

## Local Development

```bash
cp .env.example .env   # optional; compose uses .env.example by default
make build
make up
make migrate
make seed
```

- App: http://localhost:8000
- Mailhog UI: http://localhost:8025

## Demo Users

| Email | Password | Role |
|-------|----------|------|
| admin@opsdesk.local | password123 | Admin |
| ops@opsdesk.local | password123 | Ops |
| manager@opsdesk.local | password123 | Manager |
| employee@opsdesk.local | password123 | Employee |

## Running Tests

```bash
make test
make coverage
make lint
```

## Background Jobs

Celery workers handle:

- `send_notification_email` — on notification create
- `mark_overdue_requests` — daily (3+ business days pending)
- `generate_weekly_report` — weekly
- `cleanup_old_notifications` — daily

## Project Structure

```
apps/           # Domain apps (accounts, requests, approvals, ...)
config/         # Settings, URLs, Celery
templates/      # Django templates
static/         # CSS/JS
tests/          # Factories and integration tests
docs/           # Architecture and ADRs
docker/         # Entrypoint scripts
```

## Design Decisions

- [0001 — Why Django monolith](docs/decisions/0001-why-django-monolith.md)
- [0002 — Service layer](docs/decisions/0002-service-layer.md)
- [0003 — Approval workflow](docs/decisions/0003-approval-workflow.md)

## Future Improvements

- SSO / OIDC authentication
- File virus scanning for attachments
- SLA policies per category
- Full-text search for requests
- API layer (DRF) for mobile clients
