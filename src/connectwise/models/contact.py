from dataclasses import dataclass
from typing import Optional


@dataclass
class Contact:
    """Represents a ConnectWise company contact."""
    id: int
    firstName: str
    company: dict
    lastName: str = ""
    title: Optional[str] = None
    site: Optional[dict] = None
    inactiveFlag: bool = False
    defaultPhoneType: Optional[str] = None
    defaultPhoneNbr: Optional[str] = None
    defaultBillingFlag: bool = False
    defaultContactFlag: bool = False
    communicationItems: Optional[list] = None
    department: Optional[dict] = None
    managerId: Optional[int] = None
    mobileGuid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """Create a Contact instance from an API response dictionary."""
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def full_name(self) -> str:
        """Get the contact's full name."""
        return f"{self.firstName} {self.lastName}"

    @property
    def company_name(self) -> str:
        """Get company name from nested dict."""
        return self.company.get("name", "") if self.company else ""

    @property
    def company_id(self) -> Optional[int]:
        """Get company ID from nested dict."""
        return self.company.get("id") if self.company else None

    @property
    def is_active(self) -> bool:
        """Check if the contact is active."""
        return not self.inactiveFlag

    @property
    def primary_email(self) -> Optional[str]:
        """
        Get the primary email address from communicationItems.
        Returns the value of the first item where type.name == "Email" and defaultFlag == True.
        """
        if not self.communicationItems:
            return None
        for item in self.communicationItems:
            item_type = item.get("type", {})
            if item_type.get("name") == "Email" and item.get("defaultFlag"):
                return item.get("value")
        return None

    @property
    def primary_phone(self) -> Optional[str]:
        """
        Get the primary phone number from communicationItems.
        Returns the value of the first item where type.name is a phone type and defaultFlag == True.
        """
        if not self.communicationItems:
            return None
        phone_types = {"Direct", "Cell", "Main"}
        for item in self.communicationItems:
            item_type = item.get("type", {})
            if item_type.get("name") in phone_types and item.get("defaultFlag"):
                return item.get("value")
        return None

    def __str__(self) -> str:
        return f"#{self.id} - {self.full_name} [{self.company_name}]"
