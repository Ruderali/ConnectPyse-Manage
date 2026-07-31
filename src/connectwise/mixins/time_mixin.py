from typing import List, Optional

from ..models import TimeEntry


class TimeMixin:
    """Time entry API methods."""

    def get_time_entries(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[TimeEntry]:
        """
        Get time entries with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[TimeEntry]: List of time entries
        """
        if limit is not None:
            results = self.get("time/entries", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("time/entries", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [TimeEntry.from_dict(r) for r in results]

    def get_time_entry(self, entry_id: int, run_as: Optional[str] = None) -> Optional[TimeEntry]:
        """
        Get a specific time entry by ID.

        Args:
            entry_id: Time entry ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[TimeEntry]: Time entry details, or None if not found
        """
        result = self.get(f"time/entries/{entry_id}", run_as=run_as)
        return TimeEntry.from_dict(result) if result else None

    def get_time_entry_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of time entries matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Time entry count, or None if endpoint not found
        """
        return self.get_count("time/entries", conditions=conditions, run_as=run_as)

    def get_member_time_entries(
        self,
        member_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[TimeEntry]:
        """
        Get all time entries for a specific member.

        Args:
            member_id: Member ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[TimeEntry]: Time entries for the member
        """
        full_conditions = f"member/id={member_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        return self.get_time_entries(conditions=full_conditions, run_as=run_as)

    def create_time_entry(
        self,
        charge_to_id: int,
        charge_to_type: str,
        member_id: int,
        actual_hours: float,
        notes: str = "",
        billable: str = "Billable",
        time_start: str = None,
        time_end: str = None,
        work_type_id: int = None,
        work_role_id: int = None,
        company_id: int = None,
        run_as: Optional[str] = None
    ) -> TimeEntry:
        """
        Create a new time entry.

        Args:
            charge_to_id: ID of the ticket or project this time is charged to
            charge_to_type: Type of resource — "ServiceTicket", "ProjectTicket",
                            "ChargeCode", or "Activity"
            member_id: ID of the member logging the time
            actual_hours: Number of hours to log
            notes: Optional notes for the time entry
            billable: Billing option — "Billable", "DoNotBill", "NoCharge", or "NoDefault"
            time_start: Optional start time (ISO format string)
            time_end: Optional end time (ISO format string)
            work_type_id: Optional work type ID
            work_role_id: Optional work role ID
            company_id: Optional company ID (inferred from ticket if not provided)
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            TimeEntry: Created time entry object
        """
        payload = {
            "chargeToId": charge_to_id,
            "chargeToType": charge_to_type,
            "member": {"id": member_id},
            "actualHours": actual_hours,
            "billableOption": billable,
        }
        if notes:
            payload["notes"] = notes
        if time_start is not None:
            payload["timeStart"] = time_start
        if time_end is not None:
            payload["timeEnd"] = time_end
        if work_type_id is not None:
            payload["workType"] = {"id": work_type_id}
        if work_role_id is not None:
            payload["workRole"] = {"id": work_role_id}
        if company_id is not None:
            payload["company"] = {"id": company_id}

        result = self.post("time/entries", payload, run_as=run_as)
        return TimeEntry.from_dict(result)
