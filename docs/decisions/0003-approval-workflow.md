# ADR 0003: Approval Workflow

Approval logic is separated from request CRUD. Requests own the core data and status, while approvals manage approval steps and decisions. This makes workflows extensible for manager, HR, and Ops approval chains.
