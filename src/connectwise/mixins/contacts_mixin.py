from typing import List, Optional

from ..models import Contact


class ContactsMixin:
    """Company contact API methods."""

    def get_contacts(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Contact]:
        """
        Get contacts with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Contact]: List of contacts
        """
        if limit is not None:
            results = self.get("company/contacts", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("company/contacts", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Contact.from_dict(r) for r in results]

    def get_contact(self, contact_id: int, run_as: Optional[str] = None) -> Optional[Contact]:
        """
        Get a specific contact by ID.

        Args:
            contact_id: Contact ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Contact]: Contact details, or None if not found
        """
        result = self.get(f"company/contacts/{contact_id}", run_as=run_as)
        return Contact.from_dict(result) if result else None

    def get_contact_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of contacts matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Contact count, or None if endpoint not found
        """
        return self.get_count("company/contacts", conditions=conditions, run_as=run_as)

    def create_contact(
        self,
        first_name: str,
        last_name: str,
        company_id: int,
        email: str = None,
        title: str = None,
        phone: str = None,
        phone_type: str = "Direct",
        run_as: Optional[str] = None
    ) -> Contact:
        """
        Create a new contact.

        Args:
            first_name: Contact's first name
            last_name: Contact's last name
            company_id: Company ID to associate the contact with
            email: Optional email address (set as default email)
            title: Optional job title
            phone: Optional phone number
            phone_type: Phone number type — "Direct", "Cell", or "Main" (default: "Direct")
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Contact: Created contact object
        """
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "company": {"id": company_id},
        }
        if title is not None:
            payload["title"] = title

        communication_items = []
        if email is not None:
            communication_items.append({
                "type": {"name": "Email"},
                "value": email,
                "defaultFlag": True
            })
        if phone is not None:
            communication_items.append({
                "type": {"name": phone_type},
                "value": phone,
                "defaultFlag": True
            })
        if communication_items:
            payload["communicationItems"] = communication_items

        result = self.post("company/contacts", payload, run_as=run_as)
        return Contact.from_dict(result)
