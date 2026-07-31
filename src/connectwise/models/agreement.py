from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class Agreement:
    """Represents a ConnectWise finance agreement."""
    id: int
    name: str
    company: dict
    type: dict
    status: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    noEndingDateFlag: bool = False
    billAmount: Optional[float] = None
    billCycleId: Optional[int] = None
    billOneTimeFlag: bool = False
    invoiceDescription: Optional[str] = None
    cancelledFlag: bool = False
    reasonCancelled: Optional[str] = None
    contactName: Optional[str] = None
    sla: Optional[dict] = None
    location: Optional[dict] = None
    department: Optional[dict] = None
    opportunity: Optional[dict] = None
    workOrder: Optional[str] = None
    internalNotes: Optional[str] = None
    applicationUnits: Optional[str] = None
    applicationLimit: Optional[float] = None
    applicationCycle: Optional[str] = None
    applicationUnlimitedFlag: bool = False
    taxable: Optional[bool] = None
    prorateFlag: bool = False
    invoiceTemplateSetupId: Optional[int] = None
    billToCompany: Optional[dict] = None
    billToSite: Optional[dict] = None
    billToContact: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Agreement':
        """Create an Agreement instance from an API response dictionary."""
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
    def type_name(self) -> str:
        """Get agreement type name from nested dict."""
        return self.type.get("name", "") if self.type else ""

    @property
    def is_active(self) -> bool:
        """Check if the agreement is active (not cancelled and status is Active)."""
        return not self.cancelledFlag and self.status == "Active"

    @property
    def start_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.startDate)

    @property
    def end_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.endDate)

    def __str__(self) -> str:
        return f"#{self.id} - {self.name} [{self.company_name}]"
