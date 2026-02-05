"""Default value configuration classes for ConnectWise API."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TicketDefaults:
    """
    Default values for ticket creation.

    These defaults are used when creating tickets if specific values
    are not provided in the create_ticket call.

    Example:
        defaults = TicketDefaults(
            company_id=19184,
            board_id=12,
            priority_id=8,
            status_id=1,
            type_id=5,
            source_id=42
        )

        client = ConnectWiseClient(
            base_url="https://...",
            client="MyCompany",
            username="apiuser",
            password="secret",
            client_id="uuid",
            ticket_defaults=defaults
        )
    """

    company_id: Optional[int] = None
    board_id: Optional[int] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    type_id: Optional[int] = None
    source_id: Optional[int] = None

    def __repr__(self) -> str:
        """Custom repr to show only non-None values."""
        fields = []
        for field_name in ['company_id', 'board_id', 'priority_id', 'status_id', 'type_id', 'source_id']:
            value = getattr(self, field_name)
            if value is not None:
                fields.append(f"{field_name}={value}")

        return f"TicketDefaults({', '.join(fields)})"
