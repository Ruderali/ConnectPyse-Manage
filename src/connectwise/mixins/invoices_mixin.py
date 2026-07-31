from typing import List, Optional

from ..models import Invoice


class InvoicesMixin:
    """Finance invoice API methods. Read-only."""

    def get_invoices(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Invoice]:
        """
        Get invoices with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Invoice]: List of invoices
        """
        if limit is not None:
            results = self.get("finance/invoices", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("finance/invoices", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Invoice.from_dict(r) for r in results]

    def get_invoice(self, invoice_id: int, run_as: Optional[str] = None) -> Optional[Invoice]:
        """
        Get a specific invoice by ID.

        Args:
            invoice_id: Invoice ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Invoice]: Invoice details, or None if not found
        """
        result = self.get(f"finance/invoices/{invoice_id}", run_as=run_as)
        return Invoice.from_dict(result) if result else None

    def get_invoice_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of invoices matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Invoice count, or None if endpoint not found
        """
        return self.get_count("finance/invoices", conditions=conditions, run_as=run_as)

    def get_company_invoices(
        self,
        company_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[Invoice]:
        """
        Get all invoices for a specific company.

        Args:
            company_id: Company ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Invoice]: Invoices for the company
        """
        full_conditions = f"company/id={company_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        return self.get_invoices(conditions=full_conditions, run_as=run_as)

    def get_agreement_invoices(self, agreement_id: int, run_as: Optional[str] = None) -> List[Invoice]:
        """
        Get all invoices associated with a specific agreement.

        Args:
            agreement_id: Agreement ID to filter by
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Invoice]: Invoices for the agreement
        """
        return self.get_invoices(conditions=f"agreement/id={agreement_id}", run_as=run_as)
