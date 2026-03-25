from dataclasses import dataclass
from typing import Optional


@dataclass
class Priority:
    """Represents a ConnectWise ticket priority."""
    id: int
    name: str
    sortOrder: Optional[int] = None
    defaultFlag: bool = False
    imageLink: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Priority':
        """
        Create a Priority instance from a dictionary.

        Args:
            data: Dictionary containing priority data from API

        Returns:
            Priority: Priority object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key priority details."""
        return f"#{self.id} - {self.name}"
