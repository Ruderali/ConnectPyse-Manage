from dataclasses import dataclass
from typing import Optional


@dataclass
class Member:
    """Represents a ConnectWise system member (internal staff)."""
    id: int
    identifier: str
    firstName: str
    lastName: str
    email: Optional[str] = None
    officeEmail: Optional[str] = None
    mobileEmail: Optional[str] = None
    title: Optional[str] = None
    reportsTo: Optional[dict] = None
    location: Optional[dict] = None
    department: Optional[dict] = None
    defaultEmail: str = "Office"
    inactiveFlag: bool = False
    calendarId: Optional[int] = None
    type: Optional[dict] = None
    mobileGuid: Optional[str] = None
    photo: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Member':
        """Create a Member instance from an API response dictionary."""
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def full_name(self) -> str:
        """Get the member's full name."""
        return f"{self.firstName} {self.lastName}"

    @property
    def is_active(self) -> bool:
        """Check if the member is active."""
        return not self.inactiveFlag

    @property
    def department_name(self) -> Optional[str]:
        """Get department name from nested dict."""
        return self.department.get("name") if self.department else None

    @property
    def location_name(self) -> Optional[str]:
        """Get location name from nested dict."""
        return self.location.get("name") if self.location else None

    def __str__(self) -> str:
        return f"#{self.id} - {self.full_name} ({self.identifier})"
