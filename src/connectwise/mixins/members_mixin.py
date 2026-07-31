from typing import List, Optional

from ..models import Member


class MembersMixin:
    """System member (internal staff) API methods. Read-only."""

    def get_members(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Member]:
        """
        Get system members with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Member]: List of members
        """
        if limit is not None:
            results = self.get("system/members", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("system/members", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Member.from_dict(r) for r in results]

    def get_member(self, member_id: int, run_as: Optional[str] = None) -> Optional[Member]:
        """
        Get a specific member by ID.

        Args:
            member_id: Member ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Member]: Member details, or None if not found
        """
        result = self.get(f"system/members/{member_id}", run_as=run_as)
        return Member.from_dict(result) if result else None

    def get_member_by_identifier(self, identifier: str, run_as: Optional[str] = None) -> Optional[Member]:
        """
        Get a member by their login identifier (username).

        Args:
            identifier: The member's login username
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Member]: Member details, or None if not found
        """
        results = self.get_members(
            conditions=f'identifier="{identifier}"',
            limit=1,
            run_as=run_as
        )
        return results[0] if results else None

    def get_member_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of members matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Member count, or None if endpoint not found
        """
        return self.get_count("system/members", conditions=conditions, run_as=run_as)
