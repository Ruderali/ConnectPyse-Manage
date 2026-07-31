from typing import List, Optional

from ..models import Configuration


class ConfigurationMixin:
    """Configuration-related API methods."""

    def attach_configuration(self, ticket_id: int, config_id: int,
                            run_as: Optional[str] = None) -> Configuration:
        """
        Attach a configuration to a ConnectWise ticket.

        Args:
            ticket_id: Ticket ID to attach configuration to
            config_id: Configuration ID to attach
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Configuration: The attached configuration
        """
        body = {"id": config_id}
        result = self.post(f"service/tickets/{ticket_id}/configurations", body, run_as=run_as)
        return Configuration.from_dict(result)

    def detach_configuration(self, ticket_id: int, config_id: int,
                            run_as: Optional[str] = None) -> bool:
        """
        Detach a configuration from a ticket.

        Args:
            ticket_id: Ticket ID
            config_id: Configuration ID to detach
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            bool: True if successfully detached, False if not found
        """
        return self.delete(f"service/tickets/{ticket_id}/configurations", config_id, run_as=run_as)

    def get_ticket_configurations(self, ticket_id: int,
                                 run_as: Optional[str] = None) -> List[Configuration]:
        """
        Get all configurations attached to a ticket.

        Args:
            ticket_id: Ticket ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Configuration]: List of attached configurations
        """
        results = self.get_all(f"service/tickets/{ticket_id}/configurations", run_as=run_as)
        return [Configuration.from_dict(config) for config in results]

    def get_configuration_count(self, conditions: str = "",
                               run_as: Optional[str] = None) -> Optional[int]:
        """
        Return the total number of configurations matching the given conditions
        without fetching any configuration data.

        Args:
            conditions: ConnectWise conditions string for filtering
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            int: Total configuration count, or None if the endpoint was not found
        """
        return self.get_count("company/configurations", conditions=conditions, run_as=run_as)

    def get_configuration(self, config_id: int,
                         run_as: Optional[str] = None) -> Optional[Configuration]:
        """
        Get details of a specific configuration.

        Args:
            config_id: Configuration ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Optional[Configuration]: Configuration details, or None if not found
        """
        result = self.get(f"company/configurations/{config_id}", run_as=run_as)
        return Configuration.from_dict(result) if result else None

    def get_configurations(
        self,
        conditions: str = "",
        pagesize: int = 1000,
        run_as: Optional[str] = None
    ) -> List[Configuration]:
        """
        Get multiple configurations with optional filtering.

        Args:
            conditions: ConnectWise conditions string for filtering
            pagesize: Results per page
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Configuration]: List of configurations
        """
        results = self.get_all("company/configurations",
                              conditions=conditions,
                              pagesize=pagesize,
                              run_as=run_as)
        return [Configuration.from_dict(config) for config in results]

    def get_company_configurations(self, company_id: int,
                                  run_as: Optional[str] = None) -> List[Configuration]:
        """
        Get all configurations for a specific company.

        Args:
            company_id: Company ID
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[Configuration]: List of configurations for the company
        """
        conditions = f"company/id={company_id}"
        return self.get_configurations(conditions=conditions, run_as=run_as)

    def get_configuration_type_questions(self, type_id: int,
                                        run_as: Optional[str] = None) -> List[dict]:
        """
        Get the custom question definitions for a configuration type.

        Args:
            type_id: The configuration type ID.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            List[dict]: List of question definitions, each containing
                        'questionId', 'question' (label), 'fieldType', etc.
        """
        results = self.get_all(f"company/configurations/types/{type_id}/questions", run_as=run_as)
        return results

    def create_configuration(self, config: Configuration,
                            run_as: Optional[str] = None) -> Configuration:
        """
        Create a new configuration item in ConnectWise.

        Args:
            config: Configuration object with fields populated.
                    The id field is ignored (CW assigns it).
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Configuration: The created configuration with CW-assigned id.
        """
        data = config.to_dict(exclude_id=True)
        result = self.post("company/configurations", data=data, run_as=run_as)
        return Configuration.from_dict(result)

    def update_configuration(self, config_id: int, config: Configuration,
                            run_as: Optional[str] = None) -> Configuration:
        """
        Update an existing configuration item using PATCH.

        Builds JSON-Patch operations from non-None fields on the config object.

        Args:
            config_id: ID of the configuration to update.
            config: Configuration object with fields to update populated.
                    Only non-None optional fields generate patch operations.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            Configuration: The updated configuration.
        """
        data = config.to_dict(exclude_id=True)
        operations = [
            {"op": "replace", "path": field, "value": value}
            for field, value in data.items()
        ]
        result = self.patch("company/configurations", config_id, operations, run_as=run_as)
        return Configuration.from_dict(result)

    def delete_configuration(self, config_id: int,
                            run_as: Optional[str] = None) -> bool:
        """
        Delete a configuration item.

        Args:
            config_id: Configuration ID to delete.
            run_as: Optional precomputed auth token to make this call as another member

        Returns:
            bool: True if deleted, False if not found.
        """
        return self.delete("company/configurations", config_id, run_as=run_as)
