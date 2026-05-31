from apps.audit.models import AuditLog


def audit_log(actor, action, entity=None, metadata=None, request=None):
    """Create an immutable audit log entry."""
    entity_type = ""
    entity_id = ""
    if entity is not None:
        entity_type = entity.__class__.__name__
        entity_id = str(getattr(entity, "pk", getattr(entity, "id", "")))

    ip_address = None
    user_agent = ""
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
