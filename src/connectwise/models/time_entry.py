from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class TimeEntry:
    """Represents a ConnectWise time entry."""
    id: int
    company: dict
    chargeToId: int
    chargeToType: str
    member: Optional[dict] = None
    locationId: Optional[int] = None
    businessUnitId: Optional[int] = None
    workType: Optional[dict] = None
    workRole: Optional[dict] = None
    agreement: Optional[dict] = None
    timeStart: Optional[str] = None
    timeEnd: Optional[str] = None
    hoursDeduct: Optional[float] = None
    actualHours: Optional[float] = None
    billableOption: str = "Billable"
    notes: Optional[str] = None
    internalNotes: Optional[str] = None
    addToDetailDescriptionFlag: bool = False
    addToInternalAnalysisFlag: bool = False
    addToResolutionFlag: bool = False
    emailResourceFlag: bool = False
    emailContactFlag: bool = False
    emailCcFlag: bool = False
    hoursBilled: Optional[float] = None
    enteredBy: Optional[str] = None
    dateEntered: Optional[str] = None
    invoiceId: Optional[int] = None
    mobileGuid: Optional[str] = None
    hourlyRate: Optional[float] = None
    ticket: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'TimeEntry':
        """Create a TimeEntry instance from an API response dictionary."""
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
    def company_name(self) -> str:
        """Get company name from nested dict."""
        return self.company.get("name", "") if self.company else ""

    @property
    def company_id(self) -> Optional[int]:
        """Get company ID from nested dict."""
        return self.company.get("id") if self.company else None

    @property
    def work_type_name(self) -> Optional[str]:
        """Get work type name from nested dict."""
        return self.workType.get("name") if self.workType else None

    @property
    def work_role_name(self) -> Optional[str]:
        """Get work role name from nested dict."""
        return self.workRole.get("name") if self.workRole else None

    @property
    def agreement_id(self) -> Optional[int]:
        """Get agreement ID from nested dict."""
        return self.agreement.get("id") if self.agreement else None

    @property
    def agreement_name(self) -> Optional[str]:
        """Get agreement name from nested dict."""
        return self.agreement.get("name") if self.agreement else None

    @property
    def is_billable(self) -> bool:
        """Check if this time entry is billable."""
        return self.billableOption == "Billable"

    @property
    def time_start_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.timeStart)

    @property
    def time_end_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.timeEnd)

    @property
    def date_entered_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.dateEntered)

    def __str__(self) -> str:
        return f"#{self.id} - {self.member_name} ({self.actualHours}h) [{self.chargeToType}:{self.chargeToId}]"
