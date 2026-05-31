# ADR 0002: Service Layer

Business workflows are implemented in service functions instead of views. This keeps views thin, makes domain logic testable, and avoids duplicating approval, notification, and audit behavior.
