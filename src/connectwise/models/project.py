from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class Project:
    """Represents a ConnectWise project."""
    id: int
    name: str
    company: dict
    status: dict
    type: Optional[dict] = None
    board: Optional[dict] = None
    manager: Optional[dict] = None
    estimatedStart: Optional[str] = None
    estimatedEnd: Optional[str] = None
    actualStart: Optional[str] = None
    actualEnd: Optional[str] = None
    estimatedHours: Optional[float] = None
    actualHours: Optional[float] = None
    budgetFlag: bool = False
    budgetHours: Optional[float] = None
    billingAmount: Optional[float] = None
    billingMethod: Optional[str] = None
    billingRateType: Optional[str] = None
    percentComplete: Optional[float] = None
    description: Optional[str] = None
    closedFlag: bool = False
    agreement: Optional[dict] = None
    site: Optional[dict] = None
    opportunity: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Create a Project instance from an API response dictionary."""
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def company_name(self) -> str:
        """Get company name from nested dict."""
        return self.company.get("name", "") if self.company else ""

    @property
    def company_id(self) -> Optional[int]:
        """Get company ID from nested dict."""
        return self.company.get("id") if self.company else None

    @property
    def status_name(self) -> str:
        """Get status name from nested dict."""
        return self.status.get("name", "") if self.status else ""

    @property
    def type_name(self) -> Optional[str]:
        """Get type name from nested dict."""
        return self.type.get("name") if self.type else None

    @property
    def board_name(self) -> Optional[str]:
        """Get board name from nested dict."""
        return self.board.get("name") if self.board else None

    @property
    def manager_name(self) -> Optional[str]:
        """Get manager name from nested dict."""
        return self.manager.get("name") if self.manager else None

    @property
    def manager_id(self) -> Optional[int]:
        """Get manager ID from nested dict."""
        return self.manager.get("id") if self.manager else None

    @property
    def is_closed(self) -> bool:
        """Check if the project is closed."""
        return self.closedFlag

    @property
    def estimated_start_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.estimatedStart)

    @property
    def estimated_end_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.estimatedEnd)

    @property
    def actual_start_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.actualStart)

    @property
    def actual_end_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.actualEnd)

    def __str__(self) -> str:
        return f"#{self.id} - {self.name} [{self.company_name}] ({self.status_name})"
