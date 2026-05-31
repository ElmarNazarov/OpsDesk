# Local Development

## Prerequisites

- Docker & Docker Compose
- Make (optional)

## Quick Start

```bash
make build
make up
make migrate
make seed
```

Open http://localhost:8000 and log in with `employee@opsdesk.local` / `password123`.

## Services

| Service | Port |
|---------|------|
| Django | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| Mailhog SMTP | 1025 |
| Mailhog UI | 8025 |

## Common Commands

```bash
make shell
make makemigrations
make test
make lint
make logs
```

## Settings

- Local: `config.settings.local` (debug toolbar, Mailhog)
- Test: `config.settings.test` (eager Celery, fast hashes)
- Production: `config.settings.production`

Environment variables are documented in `.env.example`.
