from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class ProjectPhase:
    """Represents a phase within a ConnectWise project."""
    id: int
    projectId: int
    description: str
    status: Optional[dict] = None
    board: Optional[dict] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    wbsCode: Optional[str] = None
    billTime: Optional[str] = None
    billExpenses: Optional[str] = None
    billProducts: Optional[str] = None
    markAsClosedFlag: bool = False
    estimatedHours: Optional[float] = None
    scheduledHours: Optional[float] = None
    actualHours: Optional[float] = None
    parentPhaseId: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectPhase':
        """Create a ProjectPhase instance from an API response dictionary."""
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }
        return cls(**filtered_data)

    @property
    def status_name(self) -> Optional[str]:
        """Get status name from nested dict."""
        return self.status.get("name") if self.status else None

    @property
    def board_name(self) -> Optional[str]:
        """Get board name from nested dict."""
        return self.board.get("name") if self.board else None

    @property
    def is_closed(self) -> bool:
        """Check if the phase is marked as closed."""
        return self.markAsClosedFlag

    @property
    def start_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.startDate)

    @property
    def end_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.endDate)

    def __str__(self) -> str:
        return f"#{self.id} - {self.description} (Project #{self.projectId})"
