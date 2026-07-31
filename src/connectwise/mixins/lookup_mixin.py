from typing import List, Optional

from ..models.priority import Priority
from ..models.source import Source


class LookupMixin:
    """General service lookup methods (priorities, sources, etc.)."""

    def get_priorities(self, run_as: Optional[str] = None) -> List[Priority]:
        """
        Get all ticket priorities.

        Args:
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Priority]: List of priorities
        """
        results = self.get_all("service/priorities", run_as=run_as)
        return [Priority.from_dict(r) for r in results]

    def get_sources(self, run_as: Optional[str] = None) -> List[Source]:
        """
        Get all ticket sources.

        Args:
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Source]: List of sources
        """
        results = self.get_all("service/sources", run_as=run_as)
        return [Source.from_dict(r) for r in results]
