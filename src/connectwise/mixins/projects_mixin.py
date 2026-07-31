from typing import List, Optional

from ..models import Project, ProjectPhase, Ticket, TimeEntry


class ProjectsMixin:
    """Project, phase, and project ticket API methods."""

    def get_projects(
        self,
        conditions: str = "",
        orderby: str = "",
        limit: int = None,
        run_as: Optional[str] = None
    ) -> List[Project]:
        """
        Get projects with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            orderby: Order by clause
            limit: Cap the number of results. If set, makes a single page
                   request instead of paginating through all records.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Project]: List of projects
        """
        if limit is not None:
            results = self.get("project/projects", conditions=conditions,
                               orderby=orderby, pagesize=limit, run_as=run_as) or []
            if not isinstance(results, list):
                results = [results]
        else:
            results = self.get_all("project/projects", conditions=conditions,
                                   orderby=orderby, run_as=run_as)
        return [Project.from_dict(r) for r in results]

    def get_project(self, project_id: int, run_as: Optional[str] = None) -> Optional[Project]:
        """
        Get a specific project by ID.

        Args:
            project_id: Project ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Project]: Project details, or None if not found
        """
        result = self.get(f"project/projects/{project_id}", run_as=run_as)
        return Project.from_dict(result) if result else None

    def get_project_count(self, conditions: str = "", run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of projects matching the given conditions.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[int]: Project count, or None if endpoint not found
        """
        return self.get_count("project/projects", conditions=conditions, run_as=run_as)

    def get_company_projects(
        self,
        company_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[Project]:
        """
        Get all projects for a specific company.

        Args:
            company_id: Company ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Project]: Projects for the company
        """
        full_conditions = f"company/id={company_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        return self.get_projects(conditions=full_conditions, run_as=run_as)

    def get_project_phases(self, project_id: int, run_as: Optional[str] = None) -> List[ProjectPhase]:
        """
        Get all phases for a specific project.

        Args:
            project_id: Project ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[ProjectPhase]: Phases of the project
        """
        results = self.get_all(f"project/projects/{project_id}/phases", run_as=run_as)
        return [ProjectPhase.from_dict(r) for r in results]

    def get_project_phase(
        self,
        project_id: int,
        phase_id: int,
        run_as: Optional[str] = None
    ) -> Optional[ProjectPhase]:
        """
        Get a specific phase of a project.

        Args:
            project_id: Project ID
            phase_id: Phase ID to retrieve
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[ProjectPhase]: Phase details, or None if not found
        """
        result = self.get(f"project/projects/{project_id}/phases/{phase_id}", run_as=run_as)
        return ProjectPhase.from_dict(result) if result else None

    def get_project_tickets(
        self,
        project_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[Ticket]:
        """
        Get all tickets associated with a project.

        Args:
            project_id: Project ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Ticket]: Project tickets (same Ticket model, chargeToType="ProjectTicket")
        """
        full_conditions = f"project/id={project_id}"
        if conditions:
            full_conditions += f" AND {conditions}"
        results = self.get_all("project/tickets", conditions=full_conditions, run_as=run_as)
        return [Ticket.from_dict(r) for r in results]

    def get_project_time_entries(
        self,
        project_id: int,
        conditions: str = "",
        run_as: Optional[str] = None
    ) -> List[TimeEntry]:
        """
        Get all time entries charged to a project.

        Args:
            project_id: Project ID to filter by
            conditions: Optional additional conditions string
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[TimeEntry]: Time entries for the project
        """
        full_conditions = f'chargeToId={project_id} AND chargeToType="ProjectTicket"'
        if conditions:
            full_conditions += f" AND {conditions}"
        results = self.get_all("time/entries", conditions=full_conditions, run_as=run_as)
        return [TimeEntry.from_dict(r) for r in results]

    def create_project(
        self,
        name: str,
        company_id: int,
        status_id: int,
        board_id: int = None,
        manager_id: int = None,
        estimated_start: str = None,
        estimated_end: str = None,
        description: str = None,
        billing_method: str = None,
        run_as: Optional[str] = None
    ) -> Project:
        """
        Create a new project.

        Args:
            name: Project name
            company_id: Company ID to associate with the project
            status_id: Project status ID
            board_id: Optional board ID
            manager_id: Optional manager member ID
            estimated_start: Optional estimated start date (ISO format string)
            estimated_end: Optional estimated end date (ISO format string)
            description: Optional project description
            billing_method: Optional billing method
                            ("ActualRates", "FixedFee", "NotToExceed", "OverrideRate")
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Project: Created project object
        """
        payload = {
            "name": name,
            "company": {"id": company_id},
            "status": {"id": status_id},
        }
        if board_id is not None:
            payload["board"] = {"id": board_id}
        if manager_id is not None:
            payload["manager"] = {"id": manager_id}
        if estimated_start is not None:
            payload["estimatedStart"] = estimated_start
        if estimated_end is not None:
            payload["estimatedEnd"] = estimated_end
        if description is not None:
            payload["description"] = description
        if billing_method is not None:
            payload["billingMethod"] = billing_method

        result = self.post("project/projects", payload, run_as=run_as)
        return Project.from_dict(result)

    def create_project_phase(
        self,
        project_id: int,
        description: str,
        start_date: str = None,
        end_date: str = None,
        estimated_hours: float = None,
        board_id: int = None,
        run_as: Optional[str] = None
    ) -> ProjectPhase:
        """
        Create a new phase on an existing project.

        Args:
            project_id: Project ID to add the phase to
            description: Phase description/name
            start_date: Optional phase start date (ISO format string)
            end_date: Optional phase end date (ISO format string)
            estimated_hours: Optional estimated hours for this phase
            board_id: Optional board ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            ProjectPhase: Created phase object
        """
        payload = {
            "projectId": project_id,
            "description": description,
        }
        if start_date is not None:
            payload["startDate"] = start_date
        if end_date is not None:
            payload["endDate"] = end_date
        if estimated_hours is not None:
            payload["estimatedHours"] = estimated_hours
        if board_id is not None:
            payload["board"] = {"id": board_id}

        result = self.post(f"project/projects/{project_id}/phases", payload, run_as=run_as)
        return ProjectPhase.from_dict(result)
