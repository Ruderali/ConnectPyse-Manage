from dataclasses import dataclass
from typing import Optional


@dataclass
class BoardStatus:
    """Represents a status on a ConnectWise service board."""
    id: int
    name: str
    boardId: Optional[int] = None
    closedStatus: bool = False
    defaultFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'BoardStatus':
        """
        Create a BoardStatus instance from a dictionary.

        Args:
            data: Dictionary containing board status data from API

        Returns:
            BoardStatus: BoardStatus object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key board status details."""
        return f"#{self.id} - {self.name}"
