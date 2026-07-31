from typing import List, Optional

from ..models.company import Company
from ..models.company_status import CompanyStatus


class CompaniesMixin:
    """Company-related API methods."""

    def get_companies(self, conditions: str = "", orderby: str = "", limit: int = None,
                     run_as: Optional[str] = None) -> List[Company]:
        """
        Get companies.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause (e.g., "dateEntered desc")
            limit: Cap the number of results returned. If set, makes a single
                   page request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Company]: List of companies
        """
        if limit is not None:
            results = self.get("company/companies", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("company/companies", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Company.from_dict(r) for r in results]

    def get_company(self, company_id: int, run_as: Optional[str] = None) -> Optional[Company]:
        """
        Get a specific company by ID.

        Args:
            company_id: Company ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Company]: Company object, or None if not found
        """
        result = self.get(f"company/companies/{company_id}", run_as=run_as)
        return Company.from_dict(result) if result else None

    def get_company_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of companies matching the given conditions
        without fetching any company data.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            int: Total company count, or None if the endpoint was not found
        """
        return self.get_count("company/companies", conditions=conditions, run_as=run_as)

    def get_company_statuses(self, run_as: Optional[str] = None) -> List[CompanyStatus]:
        """
        Get all company statuses.

        Args:
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[CompanyStatus]: List of company statuses
        """
        results = self.get_all("company/companies/statuses", run_as=run_as)
        return [CompanyStatus.from_dict(r) for r in results]

    def get_company_contacts(self, company_id: int, conditions: str = "",
                            run_as: Optional[str] = None) -> List:
        """
        Get all contacts for a specific company.

        Args:
            company_id: Company ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Contact]: Contacts for the company
        """
        from ..models import Contact
        full_conditions = f"company/id={company_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        results = self.get_all("company/contacts", conditions=full_conditions, run_as=run_as)
        return [Contact.from_dict(r) for r in results]
