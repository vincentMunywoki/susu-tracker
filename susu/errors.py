class SusuError(Exception):
    """Base class for all expected, user-facing errors."""

class ValidationError(SusuError):
    pass

class UnknownMemberError(SusuError):
    pass

class DuplicateMemberError(SusuError):
    pass

class StateError(SusuError):
    """Action not allowed in the group's current state."""