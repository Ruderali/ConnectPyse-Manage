from typing import List, Optional

from ..models import Ticket, Note


class TicketMixin:
    """Ticket-related API methods."""
    
    def create_ticket(
        self,
        summary: str,
        body: str,
        company_id: int = None,
        board_id: int = None,
        priority_id: int = None,
        status_id: int = None,
        type_id: int = None,
        source_id: int = None,
        config_ids: List[int] = None
    ) -> Ticket:
        """
        Create a ticket in ConnectWise and attach any specified configurations.

        Args:
            summary: Ticket summary/subject
            body: Ticket body/description
            company_id: Company ID (uses ticket_defaults if not provided)
            board_id: Board ID (uses ticket_defaults if not provided)
            priority_id: Priority ID (uses ticket_defaults if not provided)
            status_id: Status ID (uses ticket_defaults if not provided)
            type_id: Type ID (uses ticket_defaults if not provided)
            source_id: Source ID (uses ticket_defaults if not provided)
            config_ids: Optional list of configuration IDs to attach

        Returns:
            Ticket: Created ticket object
        """
        if config_ids is None:
            config_ids = []

        # Use ticket defaults if not provided
        company_id = company_id or self.ticket_defaults.company_id
        board_id = board_id or self.ticket_defaults.board_id
        priority_id = priority_id or self.ticket_defaults.priority_id
        status_id = status_id or self.ticket_defaults.status_id
        type_id = type_id or self.ticket_defaults.type_id
        source_id = source_id or self.ticket_defaults.source_id

        payload = {
            "summary": summary,
            "board": {"id": board_id},
            "company": {"id": company_id},
            "priority": {"id": priority_id},
            "type": {"id": type_id} if type_id else None,
            "status": {"id": status_id} if status_id else None,
            "source": {"id": source_id} if source_id else None,
            "initialDescription": body
        }

        # Create the ticket
        ticket_data = self.post("service/tickets", payload)

        # Some APIs return an object, some a list – normalize just in case
        if isinstance(ticket_data, list):
            ticket_data = ticket_data[0]

        ticket_id = ticket_data.get("id")

        # Attach configurations (if any)
        for config_id in config_ids:
            self.attach_configuration(ticket_id, config_id)

        return Ticket.from_dict(ticket_data)
    
    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """
        Get a specific ticket by ID.

        Args:
            ticket_id: Ticket ID to retrieve

        Returns:
            Optional[Ticket]: Ticket details, or None if not found
        """
        result = self.get(f"service/tickets/{ticket_id}")
        return Ticket.from_dict(result) if result else None
    
    def get_tickets(
        self,
        conditions: str = "",
        pagesize: int = 1000,
        orderby: str = ""
    ) -> List[Ticket]:
        """
        Get multiple tickets with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            pagesize: Results per page
            orderby: Order by clause

        Returns:
            List[Ticket]: List of tickets
        """
        results = self.get_all("service/tickets", conditions=conditions,
                              pagesize=pagesize, orderby=orderby)
        return [Ticket.from_dict(ticket) for ticket in results]
    
    def update_ticket_status(self, ticket_id: int, status_id: int) -> Optional[Ticket]:
        """
        Update the status of a ticket in ConnectWise.

        Args:
            ticket_id: The ID of the ticket to update
            status_id: The new status ID to set

        Returns:
            Optional[Ticket]: Updated ticket, or None if not found
        """
        operations = [
            {
                "op": "replace",
                "path": "/status",
                "value": {"id": status_id}
            }
        ]

        result = self.patch("service/tickets", ticket_id, operations)
        return Ticket.from_dict(result) if result else None
    
    def update_ticket_priority(self, ticket_id: int, priority_id: int) -> Optional[Ticket]:
        """
        Update the priority of a ticket in ConnectWise.

        Args:
            ticket_id: The ID of the ticket to update
            priority_id: The new priority ID to set

        Returns:
            Optional[Ticket]: Updated ticket, or None if not found
        """
        operations = [
            {
                "op": "replace",
                "path": "/priority",
                "value": {"id": priority_id}
            }
        ]

        result = self.patch("service/tickets", ticket_id, operations)
        return Ticket.from_dict(result) if result else None
    
    def update_ticket_company(self, ticket_id: int, company_id: int) -> Optional[Ticket]:
        """
        Update the company associated with a ticket.

        Args:
            ticket_id: The ID of the ticket to update
            company_id: The ID of the company to assign

        Returns:
            Optional[Ticket]: Updated ticket, or None if not found
        """
        operations = [
            {
                "op": "replace",
                "path": "/company",
                "value": {"id": company_id}
            }
        ]

        result = self.patch("service/tickets", ticket_id, operations)
        return Ticket.from_dict(result) if result else None
    
    def update_ticket_field(self, ticket_id: int, field_path: str,
                           value: any) -> Optional[Ticket]:
        """
        Update any ticket field using PATCH operation.

        Args:
            ticket_id: The ID of the ticket to update
            field_path: Field path (e.g., "/summary", "/company")
            value: New value for the field

        Returns:
            Optional[Ticket]: Updated ticket, or None if not found
        """
        operations = [
            {
                "op": "replace",
                "path": field_path,
                "value": value
            }
        ]

        result = self.patch("service/tickets", ticket_id, operations)
        return Ticket.from_dict(result) if result else None
    
    def merge_ticket(self, child_ticket_id: int, parent_ticket_id: int,
                    child_status_id: int) -> dict:
        """
        Merge a child ticket into a parent ticket in ConnectWise.
        This updates the child ticket's status and attaches it to the parent.

        Args:
            child_ticket_id: The ticket ID of the child ticket
            parent_ticket_id: The ticket ID of the parent ticket
            child_status_id: The status ID to assign to the child ticket

        Returns:
            dict: A dict containing the results of both operations
                  {"child_ticket": Ticket, "merge_response": dict}
        """
        # Step 1: Update child ticket status
        child_ticket = self.update_ticket_status(
            child_ticket_id,
            child_status_id
        )

        # Step 2: Attach child to parent
        merge_endpoint = f"service/tickets/{parent_ticket_id}/attachChildren"
        data = {"childTicketIds": [child_ticket_id]}
        merge_response = self.post(merge_endpoint, data)

        return {
            "child_ticket": child_ticket,
            "merge_response": merge_response
        }
    
    def add_ticket_note(self, ticket_id: int, note_text: str,
                       internal: bool = True) -> Note:
        """
        Add a note to a ticket.

        Args:
            ticket_id: Ticket ID
            note_text: Note content
            internal: Whether the note is internal (default: True)

        Returns:
            Note: Created note object
        """
        payload = {
            "text": note_text,
            "detailDescriptionFlag": not internal,
            "internalAnalysisFlag": internal
        }

        result = self.post(f"service/tickets/{ticket_id}/notes", payload)
        return Note.from_dict(result)
    
    def get_ticket_notes(
        self,
        ticket_id: int,
        conditions: str = "",
        childconditions: str = "",
        fields: str = "",
        pagesize: int = None,
        orderby: str = ""
    ) -> List[Note]:
        """
        Get all notes for a ticket.

        Args:
            ticket_id: Ticket ID
            conditions: Optional conditions string for filtering notes
            childconditions: Optional child conditions string
            fields: Optional comma-separated fields to include in the response
            pagesize: Results per page (defaults to 1000)
            orderby: Optional order by clause

        Returns:
            List[Note]: List of notes
        """
        results = self.get_all(
            f"service/tickets/{ticket_id}/notes",
            conditions=conditions,
            childconditions=childconditions,
            fields=fields,
            pagesize=pagesize,
            orderby=orderby
        )
        return [Note.from_dict(note) for note in results]