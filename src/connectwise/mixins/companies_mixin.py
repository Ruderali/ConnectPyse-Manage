from typing import List, Optional

from ..models.company import Company
from ..models.company_status import CompanyStatus


class CompaniesMixin:
    """Company-related API methods."""

    def get_companies(self, conditions: str = "", orderby: str = "", limit: int = None) -> List[Company]:
        """
        Get companies.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause (e.g., "dateEntered desc")
            limit: Cap the number of results returned. If set, makes a single
                   page request instead of paginating through all records.

        Returns:
            List[Company]: List of companies
        """
        if limit is not None:
            results = self.get("company/companies", conditions=conditions,
                               orderby=orderby, pagesize=limit) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("company/companies", conditions=conditions, orderby=orderby)
        return [Company.from_dict(r) for r in results]

    def get_company(self, company_id: int) -> Optional[Company]:
        """
        Get a specific company by ID.

        Args:
            company_id: Company ID to retrieve

        Returns:
            Optional[Company]: Company object, or None if not found
        """
        result = self.get(f"company/companies/{company_id}")
        return Company.from_dict(result) if result else None

    def get_company_count(self, conditions: str = "") -> Optional[int]:
        """
        Return the total number of companies matching the given conditions
        without fetching any company data.

        Args:
            conditions: ConnectWise conditions string for filtering

        Returns:
            int: Total company count, or None if the endpoint was not found
        """
        return self.get_count("company/companies", conditions=conditions)

    def get_company_statuses(self) -> List[CompanyStatus]:
        """
        Get all company statuses.

        Returns:
            List[CompanyStatus]: List of company statuses
        """
        results = self.get_all("company/companies/statuses")
        return [CompanyStatus.from_dict(r) for r in results]
