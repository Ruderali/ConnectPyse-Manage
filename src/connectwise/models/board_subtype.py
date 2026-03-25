from dataclasses import dataclass
from typing import Optional


@dataclass
class BoardSubtype:
    """Represents a subtype on a ConnectWise service board."""
    id: int
    name: str
    boardId: Optional[int] = None
    inactive: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'BoardSubtype':
        """
        Create a BoardSubtype instance from a dictionary.

        Args:
            data: Dictionary containing board subtype data from API

        Returns:
            BoardSubtype: BoardSubtype object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key board subtype details."""
        return f"#{self.id} - {self.name}"
