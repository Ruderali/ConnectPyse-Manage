"""Utility classes and functions for ConnectWise integration."""

from datetime import datetime
from typing import Optional


def parse_cw_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse a ConnectWise API datetime string into a datetime object."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


class SecretString:
    """
    Wrapper for sensitive string values that prevents accidental exposure.

    When printed, logged, or inspected, the actual value is hidden.
    The real value must be explicitly retrieved via get_secret_value().
    """

    __slots__ = ('_value',)

    def __init__(self, value: str):
        """
        Initialize with a secret value.

        Args:
            value: The secret string to protect
        """
        self._value = value

    def get_secret_value(self) -> str:
        """
        Explicitly retrieve the secret value.

        Returns:
            str: The actual secret value
        """
        return self._value

    def __repr__(self) -> str:
        """Return obfuscated representation."""
        return "SecretString('**********')"

    def __str__(self) -> str:
        """Return obfuscated string."""
        return "**********"

    def __eq__(self, other) -> bool:
        """Allow equality comparison with other SecretString instances."""
        if isinstance(other, SecretString):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        """Make SecretString hashable."""
        return hash(self._value)
