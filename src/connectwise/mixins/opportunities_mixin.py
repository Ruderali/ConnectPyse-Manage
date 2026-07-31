from typing import List, Optional

from ..models import Opportunity


class OpportunitiesMixin:
    """Sales opportunity API methods. Read-only."""

    def get_opportunities(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Opportunity]:
        """
        Get opportunities with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Opportunity]: List of opportunities
        """
        if limit is not None:
            results = self.get("sales/opportunities", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("sales/opportunities", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Opportunity.from_dict(r) for r in results]

    def get_opportunity(self, opportunity_id: int, run_as: Optional[str] = None) -> Optional[Opportunity]:
        """
        Get a specific opportunity by ID.

        Args:
            opportunity_id: Opportunity ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Opportunity]: Opportunity details, or None if not found
        """
        result = self.get(f"sales/opportunities/{opportunity_id}", run_as=run_as)
        return Opportunity.from_dict(result) if result else None

    def get_opportunity_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of opportunities matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Opportunity count, or None if endpoint not found
        """
        return self.get_count("sales/opportunities", conditions=conditions, run_as=run_as)

    def get_company_opportunities(
        self,
        company_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[Opportunity]:
        """
        Get all opportunities for a specific company.

        Args:
            company_id: Company ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Opportunity]: Opportunities for the company
        """
        full_conditions = f"company/id={company_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        return self.get_opportunities(conditions=full_conditions, run_as=run_as)

    def get_open_opportunities(
        self,
        conditions: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Opportunity]:
        """
        Get all open (not closed) opportunities.

        Args:
            conditions: Optional additional conditions string
            limit: Cap the number of results returned
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Opportunity]: Open opportunities
        """
        full_conditions = "closedDate=null"
        if conditions:
            full_conditions += f" AND {conditions}"
        return self.get_opportunities(conditions=full_conditions, limit=limit, run_as=run_as)
