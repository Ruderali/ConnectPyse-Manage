from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class Opportunity:
    """Represents a ConnectWise sales opportunity."""
    id: int
    name: str
    company: dict
    status: dict
    type: Optional[dict] = None
    stage: Optional[dict] = None
    source: Optional[dict] = None
    location: Optional[dict] = None
    department: Optional[dict] = None
    primarySalesRep: Optional[dict] = None
    secondarySalesRep: Optional[dict] = None
    contact: Optional[dict] = None
    probability: Optional[dict] = None
    rating: Optional[dict] = None
    expectedCloseDate: Optional[str] = None
    closedDate: Optional[str] = None
    closedBy: Optional[str] = None
    dateBecameLead: Optional[str] = None
    estimatedRevenue: Optional[float] = None
    estimatedCost: Optional[float] = None
    estimatedDays: Optional[int] = None
    forecastRevenue: Optional[float] = None
    closedRevenue: Optional[float] = None
    notes: Optional[str] = None
    campaign: Optional[dict] = None
    customerPO: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Opportunity':
        """Create an Opportunity instance from an API response dictionary."""
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
    def stage_name(self) -> Optional[str]:
        """Get stage name from nested dict."""
        return self.stage.get("name") if self.stage else None

    @property
    def type_name(self) -> Optional[str]:
        """Get type name from nested dict."""
        return self.type.get("name") if self.type else None

    @property
    def primary_sales_rep_name(self) -> Optional[str]:
        """Get primary sales rep name from nested dict."""
        return self.primarySalesRep.get("name") if self.primarySalesRep else None

    @property
    def primary_sales_rep_id(self) -> Optional[int]:
        """Get primary sales rep ID from nested dict."""
        return self.primarySalesRep.get("id") if self.primarySalesRep else None

    @property
    def probability_value(self) -> Optional[int]:
        """
        Get the probability percentage as an integer.
        The API stores the probability name as a string (e.g. "75") on the probability object.
        """
        if not self.probability:
            return None
        name = self.probability.get("name")
        try:
            return int(name) if name is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def is_closed(self) -> bool:
        """
        Check if the opportunity is closed.
        Checks closedDate since the API does not return closedFlag on the opportunity itself.
        """
        return self.closedDate is not None

    @property
    def margin(self) -> float:
        """Calculate estimated margin (estimatedRevenue - estimatedCost)."""
        return (self.estimatedRevenue or 0.0) - (self.estimatedCost or 0.0)

    @property
    def expected_close_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.expectedCloseDate)

    @property
    def closed_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.closedDate)

    def __str__(self) -> str:
        return f"#{self.id} - {self.name} [{self.company_name}] ({self.stage_name})"
