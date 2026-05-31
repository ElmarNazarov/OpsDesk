# Permissions

Roles are implemented with Django Groups: Admin, Manager, Employee, Ops, HR.

## Employee

- Create, view, edit own draft requests
- Submit and cancel own requests (before final states)
- Comment on own requests
- View own notifications
- Cannot approve, fulfill, assign assets, or view internal comments

## Manager

- View team/department requests
- Approve/reject team requests (not own)
- Internal comments
- Manager dashboard and pending approvals

## Ops

- View approved/ops-processing requests
- Assign and return assets
- Fulfill equipment/software requests
- Ops dashboard and fulfillment queue

## HR

- HR approval steps when category requires HR
- Internal comments
- Uses manager-style approval views for HR steps

## Admin

- Full visibility and Django admin
- Admin dashboard
- Can manage all entities
