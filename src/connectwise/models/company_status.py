from dataclasses import dataclass


@dataclass
class CompanyStatus:
    """Represents a ConnectWise company status."""
    id: int
    name: str
    defaultFlag: bool = False
    inactiveFlag: bool = False
    notificationFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'CompanyStatus':
        """
        Create a CompanyStatus instance from a dictionary.

        Args:
            data: Dictionary containing company status data from API

        Returns:
            CompanyStatus: CompanyStatus object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key company status details."""
        return f"#{self.id} - {self.name}"
