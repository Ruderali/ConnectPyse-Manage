from typing import List, Optional

from ..models import ScheduleEntry


class ScheduleMixin:
    """Schedule entry API methods."""

    def get_schedule_entries(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[ScheduleEntry]:
        """
        Get schedule entries with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[ScheduleEntry]: List of schedule entries
        """
        if limit is not None:
            results = self.get("schedule/entries", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("schedule/entries", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [ScheduleEntry.from_dict(r) for r in results]

    def get_schedule_entry(self, entry_id: int, run_as: Optional[str] = None) -> Optional[ScheduleEntry]:
        """
        Get a specific schedule entry by ID.

        Args:
            entry_id: Schedule entry ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[ScheduleEntry]: Schedule entry details, or None if not found
        """
        result = self.get(f"schedule/entries/{entry_id}", run_as=run_as)
        return ScheduleEntry.from_dict(result) if result else None

    def get_schedule_entry_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of schedule entries matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Schedule entry count, or None if endpoint not found
        """
        return self.get_count("schedule/entries", conditions=conditions, run_as=run_as)

    def get_member_schedule(
        self,
        member_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[ScheduleEntry]:
        """
        Get all schedule entries for a specific member.

        Args:
            member_id: Member ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[ScheduleEntry]: Schedule entries for the member
        """
        full_conditions = f"member/id={member_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        return self.get_schedule_entries(conditions=full_conditions, run_as=run_as)

    def get_ticket_schedule(self, ticket_id: int, run_as: Optional[str] = None) -> List[ScheduleEntry]:
        """
        Get all schedule entries for a specific service ticket.

        Args:
            ticket_id: Ticket ID to filter by
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[ScheduleEntry]: Schedule entries assigned to the ticket
        """
        return self.get_schedule_entries(
            conditions=f"objectId={ticket_id} AND type/identifier='S'",
            run_as=run_as
        )

    def create_schedule_entry(
        self,
        object_id: int,
        type_identifier: str,
        member_id: int,
        date_start: str,
        date_end: str,
        hours: float = None,
        name: str = None,
        run_as: Optional[str] = None
    ) -> ScheduleEntry:
        """
        Create a new schedule entry.

        Args:
            object_id: ID of the object being scheduled (ticket, project, activity)
            type_identifier: Schedule type identifier — "S" (Service), "P" (Project),
                             "A" (Activity), etc.
            member_id: ID of the member being scheduled
            date_start: Start datetime (ISO format string)
            date_end: End datetime (ISO format string)
            hours: Optional hours for the entry
            name: Optional name/description for the entry
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            ScheduleEntry: Created schedule entry object
        """
        payload = {
            "objectId": object_id,
            "type": {"identifier": type_identifier},
            "member": {"id": member_id},
            "dateStart": date_start,
            "dateEnd": date_end,
        }
        if hours is not None:
            payload["hours"] = hours
        if name is not None:
            payload["name"] = name

        result = self.post("schedule/entries", payload, run_as=run_as)
        return ScheduleEntry.from_dict(result)
