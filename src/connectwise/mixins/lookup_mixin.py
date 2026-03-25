from typing import List

from ..models.priority import Priority
from ..models.source import Source


class LookupMixin:
    """General service lookup methods (priorities, sources, etc.)."""

    def get_priorities(self) -> List[Priority]:
        """
        Get all ticket priorities.

        Returns:
            List[Priority]: List of priorities
        """
        results = self.get_all("service/priorities")
        return [Priority.from_dict(r) for r in results]

    def get_sources(self) -> List[Source]:
        """
        Get all ticket sources.

        Returns:
            List[Source]: List of sources
        """
        results = self.get_all("service/sources")
        return [Source.from_dict(r) for r in results]
