from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class AgreementAddition:
    """Represents a line item addition on a ConnectWise agreement."""
    id: int
    agreementId: int
    product: dict
    quantity: float
    unitPrice: Optional[float] = None
    unitCost: Optional[float] = None
    extPrice: Optional[float] = None
    extCost: Optional[float] = None
    taxableFlag: bool = False
    billCustomer: str = "Billable"
    effectiveDate: Optional[str] = None
    cancelledDate: Optional[str] = None
    cancelledFlag: bool = False
    invoiceDescription: Optional[str] = None
    purchaseItemFlag: bool = False
    specialOrderFlag: bool = False
    description: Optional[str] = None
    uom: Optional[str] = None
    sequenceNumber: Optional[float] = None
    lessIncluded: Optional[float] = None
    adjustedQuantity: Optional[float] = None
    adjustedUnitPrice: Optional[float] = None
    adjustedExtPrice: Optional[float] = None
    serialNumber: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AgreementAddition':
        """Create an AgreementAddition instance from an API response dictionary."""
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def product_id(self) -> Optional[int]:
        """Get product ID from nested dict."""
        return self.product.get("id") if self.product else None

    @property
    def product_identifier(self) -> Optional[str]:
        """Get product identifier from nested dict."""
        return self.product.get("identifier") if self.product else None

    @property
    def product_description(self) -> Optional[str]:
        """Get product description from nested dict."""
        return self.product.get("description") if self.product else None

    @property
    def is_cancelled(self) -> bool:
        """Check if this addition has been cancelled."""
        return self.cancelledFlag

    @property
    def effective_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.effectiveDate)

    @property
    def cancelled_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.cancelledDate)

    def __str__(self) -> str:
        return f"#{self.id} - {self.product_identifier or self.description} (qty: {self.quantity})"
