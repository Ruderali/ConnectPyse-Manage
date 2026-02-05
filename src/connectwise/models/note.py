from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Note:
    """Represents a ConnectWise ticket note."""
    id: int
    ticketId: int
    text: str

    # Optional fields
    detailDescriptionFlag: bool = False
    internalAnalysisFlag: bool = False
    externalFlag: bool = False
    dateCreated: Optional[str] = None
    createdBy: Optional[str] = None
    member: Optional[dict] = None
    contact: Optional[dict] = None
    customerUpdatedFlag: bool = False
    processNotifications: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'Note':
        """
        Create a Note instance from a dictionary.
        Handles partial data from API when using 'fields' parameter.

        Args:
            data: Dictionary containing note data from API

        Returns:
            Note: Note object
        """
        # Extract only fields that exist in the dataclass
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }

        # Set required fields with defaults if missing (for partial data)
        if 'id' not in filtered_data:
            filtered_data['id'] = data.get('id', 0)
        if 'ticketId' not in filtered_data:
            filtered_data['ticketId'] = data.get('ticketId', 0)
        if 'text' not in filtered_data:
            filtered_data['text'] = data.get('text', '')

        return cls(**filtered_data)

    @property
    def is_internal(self) -> bool:
        """Check if note is internal."""
        return self.internalAnalysisFlag

    @property
    def is_external(self) -> bool:
        """Check if note is external/public."""
        return self.externalFlag

    @property
    def member_name(self) -> Optional[str]:
        """Get member name from nested dict."""
        return self.member.get("name") if self.member else None

    @property
    def member_id(self) -> Optional[int]:
        """Get member ID from nested dict."""
        return self.member.get("id") if self.member else None

    @property
    def contact_name(self) -> Optional[str]:
        """Get contact name from nested dict."""
        return self.contact.get("name") if self.contact else None

    @property
    def contact_id(self) -> Optional[int]:
        """Get contact ID from nested dict."""
        return self.contact.get("id") if self.contact else None

    @property
    def created_datetime(self) -> Optional[datetime]:
        """Parse dateCreated as a datetime object."""
        if not self.dateCreated:
            return None
        try:
            return datetime.fromisoformat(self.dateCreated.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def __str__(self) -> str:
        """String representation showing key note details."""
        note_type = "Internal" if self.is_internal else "External"
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Note #{self.id} [{note_type}]: {preview}"
