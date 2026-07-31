from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class Invoice:
    """Represents a ConnectWise finance invoice."""
    id: int
    invoiceNumber: str
    type: str
    status: dict
    company: dict
    date: Optional[str] = None
    dueDate: Optional[str] = None
    billingDelivery: Optional[str] = None
    billingStatus: Optional[str] = None
    billingTerms: Optional[dict] = None
    reference: Optional[str] = None
    customerPO: Optional[str] = None
    total: Optional[float] = None
    payments: Optional[float] = None
    balance: Optional[float] = None
    salesTax: Optional[float] = None
    currency: Optional[dict] = None
    locationId: Optional[int] = None
    departmentId: Optional[int] = None
    territory: Optional[dict] = None
    agreement: Optional[dict] = None
    billToCompany: Optional[dict] = None
    closedBy: Optional[str] = None
    internalNotes: Optional[str] = None
    topComment: Optional[str] = None
    bottomComment: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Create an Invoice instance from an API response dictionary."""
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
    def agreement_id(self) -> Optional[int]:
        """Get agreement ID from nested dict."""
        return self.agreement.get("id") if self.agreement else None

    @property
    def agreement_name(self) -> Optional[str]:
        """Get agreement name from nested dict."""
        return self.agreement.get("name") if self.agreement else None

    @property
    def is_closed(self) -> bool:
        """Check if the invoice is closed (reads from status.isClosed)."""
        return bool(self.status.get("isClosed")) if self.status else False

    @property
    def invoice_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.date)

    @property
    def due_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.dueDate)

    def __str__(self) -> str:
        return f"#{self.id} - {self.invoiceNumber} [{self.company_name}] ${self.total}"
