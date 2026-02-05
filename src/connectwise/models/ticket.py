from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Ticket:
    """Represents a ConnectWise ticket."""
    id: int
    summary: str
    board: dict
    company: dict
    priority: dict
    status: dict
    recordType: str = "ServiceTicket"
    type: Optional[dict] = None
    source: Optional[dict] = None
    subType: Optional[dict] = None
    item: Optional[dict] = None
    team: Optional[dict] = None
    owner: Optional[dict] = None
    contact: Optional[dict] = None
    site: Optional[dict] = None
    initialDescription: Optional[str] = None
    requiredDate: Optional[str] = None
    closedDate: Optional[str] = None
    closedBy: Optional[str] = None
    closedFlag: bool = False
    actualHours: float = 0.0
    budgetHours: float = 0.0
    customerUpdatedFlag: bool = False
    automaticEmailContactFlag: bool = False
    automaticEmailResourceFlag: bool = False
    automaticEmailCcFlag: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Ticket':
        """
        Create a Ticket instance from a dictionary.
        
        Args:
            data: Dictionary containing ticket data from API
            
        Returns:
            Ticket: Ticket object
        """
        # Extract only fields that exist in the dataclass
        valid_fields = {
            field for field in cls.__dataclass_fields__.keys()
        }
        filtered_data = {
            key: value for key, value in data.items() 
            if key in valid_fields
        }
        return cls(**filtered_data)
    
    @property
    def board_name(self) -> str:
        """Get board name from nested dict."""
        return self.board.get("name", "") if self.board else ""
    
    @property
    def company_name(self) -> str:
        """Get company name from nested dict."""
        return self.company.get("name", "") if self.company else ""
    
    @property
    def company_id(self) -> Optional[int]:
        """Get company ID from nested dict."""
        return self.company.get("id") if self.company else None
    
    @property
    def priority_name(self) -> str:
        """Get priority name from nested dict."""
        return self.priority.get("name", "") if self.priority else ""
    
    @property
    def status_name(self) -> str:
        """Get status name from nested dict."""
        return self.status.get("name", "") if self.status else ""
    
    @property
    def type_name(self) -> Optional[str]:
        """Get type name from nested dict."""
        return self.type.get("name") if self.type else None
    
    @property
    def source_name(self) -> Optional[str]:
        """Get source name from nested dict."""
        return self.source.get("name") if self.source else None
    
    @property
    def owner_name(self) -> Optional[str]:
        """Get owner name from nested dict."""
        return self.owner.get("name") if self.owner else None
    
    @property
    def contact_name(self) -> Optional[str]:
        """Get contact name from nested dict."""
        return self.contact.get("name") if self.contact else None
    
    @property
    def is_closed(self) -> bool:
        """Check if ticket is closed."""
        return self.closedFlag
    
    @property
    def closed_datetime(self) -> Optional[datetime]:
        """Parse closedDate as a datetime object."""
        if not self.closedDate:
            return None
        try:
            return datetime.fromisoformat(self.closedDate.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    @property
    def required_datetime(self) -> Optional[datetime]:
        """Parse requiredDate as a datetime object."""
        if not self.requiredDate:
            return None
        try:
            return datetime.fromisoformat(self.requiredDate.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    def __str__(self) -> str:
        """String representation showing key ticket details."""
        return f"#{self.id} - {self.summary} [{self.status_name}]"