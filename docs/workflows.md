# Workflows

## Vacation Request

1. Employee creates draft request (category: Vacation)
2. Employee submits → status `IN_REVIEW`, approval steps created (Manager, HR)
3. Manager approves → advances to HR or completes
4. HR approves → status `APPROVED`
5. Requester notified at each decision

## Equipment Request

1. Employee submits equipment request
2. Manager approves
3. Ops approves (if configured) → `OPS_PROCESSING`
4. Ops assigns available asset → request `FULFILLED`
5. Audit log and notification created

## Software Access

Similar to equipment: manager approval, then ops fulfillment for licenses/access.

## Approval State Transitions

```
DRAFT → SUBMITTED / IN_REVIEW
IN_REVIEW → APPROVED | REJECTED | OPS_PROCESSING
OPS_PROCESSING → FULFILLED
Any (pre-final) → CANCELLED (requester/admin)
```

## Fulfillment

Ops users assign `AVAILABLE` assets to requesters. Equipment requests linked to assignment become `FULFILLED`.

## Cancellation

Requester or admin can cancel draft, submitted, or in-review requests. Final states (rejected, fulfilled, cancelled) cannot be cancelled.
