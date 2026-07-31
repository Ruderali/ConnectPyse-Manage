from typing import List, Optional

from ..models import Agreement, AgreementAddition


class AgreementsMixin:
    """Finance agreement and addition API methods."""

    def get_agreements(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Agreement]:
        """
        Get finance agreements with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Agreement]: List of agreements
        """
        if limit is not None:
            results = self.get("finance/agreements", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("finance/agreements", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Agreement.from_dict(r) for r in results]

    def get_agreement(self, agreement_id: int, run_as: Optional[str] = None) -> Optional[Agreement]:
        """
        Get a specific agreement by ID.

        Args:
            agreement_id: Agreement ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Agreement]: Agreement details, or None if not found
        """
        result = self.get(f"finance/agreements/{agreement_id}", run_as=run_as)
        return Agreement.from_dict(result) if result else None

    def get_agreement_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of agreements matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Agreement count, or None if endpoint not found
        """
        return self.get_count("finance/agreements", conditions=conditions, run_as=run_as)

    def get_company_agreements(self, company_id: int, run_as: Optional[str] = None) -> List[Agreement]:
        """
        Get all active agreements for a company.

        Args:
            company_id: Company ID to filter by
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Agreement]: Active agreements for the company
        """
        return self.get_agreements(
            conditions=f"company/id={company_id} AND cancelledFlag=false",
            run_as=run_as
        )

    def get_agreement_additions(
        self,
        agreement_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[AgreementAddition]:
        """
        Get all additions for a specific agreement.

        Args:
            agreement_id: Agreement ID
            conditions: Optional conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[AgreementAddition]: List of agreement additions
        """
        results = self.get_all(
            f"finance/agreements/{agreement_id}/additions",
            conditions=conditions,
            run_as=run_as
        )
        return [AgreementAddition.from_dict(r) for r in results]

    def get_agreement_addition(
        self,
        agreement_id: int,
        addition_id: int,
        run_as: Optional[str] = None
    ) -> Optional[AgreementAddition]:
        """
        Get a specific addition on an agreement.

        Args:
            agreement_id: Agreement ID
            addition_id: Addition ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[AgreementAddition]: Addition details, or None if not found
        """
        result = self.get(f"finance/agreements/{agreement_id}/additions/{addition_id}", run_as=run_as)
        return AgreementAddition.from_dict(result) if result else None

    def create_agreement_addition(
        self,
        agreement_id: int,
        product_id: int,
        quantity: float,
        unit_price: float = None,
        bill_customer: str = "Billable",
        effective_date: str = None,
        description: str = None,
        taxable: bool = False,
        uom: str = None,
        run_as: Optional[str] = None
    ) -> AgreementAddition:
        """
        Create a new addition on an agreement.

        Args:
            agreement_id: Agreement ID to add the addition to
            product_id: Product catalog ID for this addition
            quantity: Quantity of the product
            unit_price: Optional unit price override
            bill_customer: Billing option — "Billable", "DoNotBill", or "NoCharge"
            effective_date: Optional effective date string (ISO format)
            description: Optional description override
            taxable: Whether this addition is taxable
            uom: Unit of measure (e.g. "Each", "Monthly", "Yearly")
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            AgreementAddition: Created addition object
        """
        payload = {
            "product": {"id": product_id},
            "quantity": quantity,
            "billCustomer": bill_customer,
            "taxableFlag": taxable,
        }
        if unit_price is not None:
            payload["unitPrice"] = unit_price
        if effective_date is not None:
            payload["effectiveDate"] = effective_date
        if description is not None:
            payload["description"] = description
        if uom is not None:
            payload["uom"] = uom

        result = self.post(f"finance/agreements/{agreement_id}/additions", payload, run_as=run_as)
        return AgreementAddition.from_dict(result)
