from dataclasses import dataclass


@dataclass
class Board:
    """Represents a ConnectWise service board."""
    id: int
    name: str
    inactive: bool = False
    projectFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'Board':
        """
        Create a Board instance from a dictionary.

        Args:
            data: Dictionary containing board data from API

        Returns:
            Board: Board object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key board details."""
        return f"#{self.id} - {self.name}"
