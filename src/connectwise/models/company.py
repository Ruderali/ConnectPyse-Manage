from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    """Represents a ConnectWise company."""
    id: int
    name: str
    status: Optional[dict] = None
    identifier: Optional[str] = None
    phoneNumber: Optional[str] = None
    website: Optional[str] = None
    addressLine1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[dict] = None
    territory: Optional[dict] = None
    market: Optional[dict] = None
    deletedFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'Company':
        """
        Create a Company instance from a dictionary.

        Args:
            data: Dictionary containing company data from API

        Returns:
            Company: Company object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def status_name(self) -> str:
        """Get status name from nested dict."""
        return self.status.get("name", "") if self.status else ""

    @property
    def territory_name(self) -> str:
        """Get territory name from nested dict."""
        return self.territory.get("name", "") if self.territory else ""

    @property
    def market_name(self) -> str:
        """Get market name from nested dict."""
        return self.market.get("name", "") if self.market else ""

    def __str__(self) -> str:
        """String representation showing key company details."""
        return f"#{self.id} - {self.name}"
