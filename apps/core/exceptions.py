class OpsDeskError(Exception):
    """Base exception for OpsDesk domain errors."""


class PermissionDeniedError(OpsDeskError):
    """Raised when a user lacks permission for an action."""


class InvalidStateError(OpsDeskError):
    """Raised when an operation is invalid for the current entity state."""
