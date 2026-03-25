from dataclasses import dataclass
from typing import Optional


@dataclass
class BoardItem:
    """Represents an item on a ConnectWise service board."""
    id: int
    name: str
    boardId: Optional[int] = None
    inactive: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'BoardItem':
        """
        Create a BoardItem instance from a dictionary.

        Args:
            data: Dictionary containing board item data from API

        Returns:
            BoardItem: BoardItem object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key board item details."""
        return f"#{self.id} - {self.name}"
