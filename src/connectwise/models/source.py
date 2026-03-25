from dataclasses import dataclass


@dataclass
class Source:
    """Represents a ConnectWise ticket source."""
    id: int
    name: str
    defaultFlag: bool = False
    enteredByFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> 'Source':
        """
        Create a Source instance from a dictionary.

        Args:
            data: Dictionary containing source data from API

        Returns:
            Source: Source object
        """
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    def __str__(self) -> str:
        """String representation showing key source details."""
        return f"#{self.id} - {self.name}"
