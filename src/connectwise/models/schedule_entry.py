from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class ScheduleEntry:
    """Represents a ConnectWise schedule entry."""
    id: int
    objectId: int
    name: str
    member: Optional[dict] = None
    where: Optional[dict] = None
    dateStart: Optional[str] = None
    dateEnd: Optional[str] = None
    reminder: Optional[dict] = None
    status: Optional[dict] = None
    type: Optional[dict] = None
    span: Optional[dict] = None
    doneFlag: bool = False
    acknowledgedFlag: bool = False
    allowScheduleConflictsFlag: bool = False
    addMemberToProjectFlag: bool = False
    projectRoleId: Optional[int] = None
    mobileGuid: Optional[str] = None
    closeDate: Optional[str] = None
    hours: Optional[float] = None
    moveRemainingBudgetFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduleEntry':
        """Create a ScheduleEntry instance from an API response dictionary."""
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def member_name(self) -> Optional[str]:
        """Get member name from nested dict."""
        return self.member.get("name") if self.member else None

    @property
    def member_id(self) -> Optional[int]:
        """Get member ID from nested dict."""
        return self.member.get("id") if self.member else None

    @property
    def status_name(self) -> Optional[str]:
        """Get status name from nested dict."""
        return self.status.get("name") if self.status else None

    @property
    def type_name(self) -> Optional[str]:
        """Get schedule type name from nested dict."""
        return self.type.get("name") if self.type else None

    @property
    def is_done(self) -> bool:
        """Check if the schedule entry is marked as done."""
        return self.doneFlag

    @property
    def date_start_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.dateStart)

    @property
    def date_end_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.dateEnd)

    def __str__(self) -> str:
        return f"#{self.id} - {self.name} [{self.member_name}] {self.dateStart}"
