# Database Schema

## Accounts

- **User** — email login, groups for roles
- **EmployeeProfile** — department, team, manager, employment type

## Organization

- **Department** → **Team** (hierarchy)
- **Location** — offices for assets

## Requests

- **RequestCategory** — approval flags per category
- **Request** — public_id, status, priority, current_approver, metadata
- **RequestComment**, **RequestAttachment**, **RequestStatusHistory**

## Approvals

- **ApprovalPolicy** — optional per-category overrides
- **ApprovalStep** — ordered steps per request
- **ApprovalAction** — immutable decision log

## Notifications

- **Notification** — recipient, type, related_request, read state

## Assets

- **AssetCategory**, **Asset**, **AssetAssignment**

## Audit

- **AuditLog** — actor, action, entity_type/id, metadata (read-only in admin)
