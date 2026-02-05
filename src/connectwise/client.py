import base64
import requests
from typing import Optional

from .mixins.ticket_mixin import TicketMixin
from .mixins.configuration_mixin import ConfigurationMixin
from .utils import SecretString
from .defaults import TicketDefaults
from .exceptions import (
    ConnectWiseAPIError,
    ConnectWiseAuthenticationError,
    ConnectWiseNotFoundError,
    ConnectWiseBadRequestError,
    ConnectWiseRateLimitError,
    ConnectWiseServerError,
    ConnectWiseConfigurationError
)


class ConnectWiseClient(TicketMixin, ConfigurationMixin):
    """ConnectWise API Client with modular functionality via mixins."""
    
    def __init__(
        self,
        base_url: str,
        client: str,
        username: str,
        password: str,
        client_id: str,
        ticket_defaults: Optional[TicketDefaults] = None
    ):
        """
        Initialize ConnectWise client with credentials and optional defaults.

        Args:
            base_url: ConnectWise base URL (e.g., https://connect.newtrend.com.au)
            client: ConnectWise client/company identifier
            username: API username
            password: API password
            client_id: Client ID for API requests
            ticket_defaults: Optional TicketDefaults object for ticket creation defaults
        """
        # Validate required parameters
        if not base_url:
            raise ConnectWiseConfigurationError("base_url is required")
        if not client:
            raise ConnectWiseConfigurationError("client is required")
        if not username:
            raise ConnectWiseConfigurationError("username is required")
        if not password:
            raise ConnectWiseConfigurationError("password is required")
        if not client_id:
            raise ConnectWiseConfigurationError("client_id is required")

        # Normalize base_url - strip trailing slashes and any API path
        # Support both old format (with /v4_6_release/apis/3.0) and new format (just domain)
        self.base_url = base_url.rstrip('/')
        if '/apis/' in self.base_url:
            # Old format - extract just the base
            self.base_url = self.base_url.split('/apis/')[0]
        if self.base_url.endswith('/v4_6_release'):
            # Already has version, keep it
            self.api_path = '/apis/3.0'
            self.service_path = '/services/system_io/Service'
        else:
            # Assume we need to add the version
            self.api_path = '/v4_6_release/apis/3.0'
            self.service_path = '/v4_6_release/services/system_io/Service'

        self.client = client
        self.username = username
        self.client_id = client_id

        # Wrap password in SecretString to prevent accidental exposure
        self._password = SecretString(password)

        # Store ticket defaults
        self.ticket_defaults = ticket_defaults or TicketDefaults()

        # Build the auth header
        self._auth_token = self._get_auth()
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def _get_auth(self) -> str:
        """Builds the Basic Auth header value."""
        credentials = f"{self.client}+{self.username}:{self._password.get_secret_value()}"
        token = base64.b64encode(credentials.encode()).decode()
        return f"Basic {token}"
    
    # ========================================================================
    # URL HELPERS
    # ========================================================================
    
    def get_api_url(self) -> str:
        """Get the full API base URL."""
        return f"{self.base_url}{self.api_path}"
    
    def get_ticket_url(self, ticket_id: int) -> str:
        """
        Get the full URL to view a ticket in ConnectWise.
        
        Args:
            ticket_id: The ticket ID
            
        Returns:
            str: Full URL to the ticket
        """
        return f"{self.base_url}{self.service_path}/fv_sr100_request.rails?service_recid={ticket_id}"
    
    # ========================================================================
    # ERROR HANDLING
    # ========================================================================

    def _handle_response_error(self, response: requests.Response) -> None:
        """
        Handle API error responses by raising appropriate exceptions.

        Args:
            response: The response object from requests

        Raises:
            ConnectWiseNotFoundError: For 404 responses
            ConnectWiseAuthenticationError: For 401 responses
            ConnectWiseBadRequestError: For 400 responses
            ConnectWiseRateLimitError: For 429 responses
            ConnectWiseServerError: For 5xx responses
            ConnectWiseAPIError: For other error responses
        """
        try:
            error_data = response.json()
            error_message = error_data.get('message', str(error_data))
        except:
            error_message = response.text or f"HTTP {response.status_code} error"

        status_code = response.status_code

        if status_code == 404:
            raise ConnectWiseNotFoundError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None
            )
        elif status_code == 401:
            raise ConnectWiseAuthenticationError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None
            )
        elif status_code == 400:
            raise ConnectWiseBadRequestError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None
            )
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise ConnectWiseRateLimitError(
                error_message,
                status_code=status_code,
                retry_after=int(retry_after) if retry_after else None,
                response_data=error_data if 'error_data' in locals() else None
            )
        elif status_code >= 500:
            raise ConnectWiseServerError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None
            )
        else:
            raise ConnectWiseAPIError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None
            )

    # ========================================================================
    # BASE HTTP METHODS
    # ========================================================================
    
    def get(self, endpoint: str, conditions: str = "", childconditions: str = "",
            fields: str = "", pagesize: int = None, page: int = None,
            orderby: str = "") -> Optional[dict]:
        """
        Perform a single GET request to the ConnectWise API.
        This method handles single requests without pagination.

        Returns:
            dict: Response data, or None if resource not found (404)

        Raises:
            ConnectWiseAPIError: For API errors (except 404)
        """
        url = f"{self.get_api_url()}/{endpoint}"
        headers = {
            "Authorization": self._auth_token,
            "clientId": self.client_id
        }

        # Build query params
        params = {}
        if conditions:
            params["conditions"] = conditions
        if childconditions:
            params["childconditions"] = childconditions
        if fields:
            params["fields"] = fields
        if pagesize:
            params["pagesize"] = pagesize
        if orderby:
            params["orderby"] = orderby
        if page:
            params["page"] = page

        # Send request
        response = requests.get(url, headers=headers, params=params)

        # Handle 404s by returning None (expected case for missing resources)
        if response.status_code == 404:
            return None

        # Handle other errors
        if not response.ok:
            self._handle_response_error(response)

        return response.json()
    
    def get_all(self, endpoint: str, conditions: str = "", childconditions: str = "",
                fields: str = "", pagesize: int = None, orderby: str = "") -> list:
        """
        Perform paginated GET requests to retrieve all records from the ConnectWise API.
        This method automatically handles pagination and returns all results as a list.

        Returns:
            list: All records from the endpoint

        Raises:
            ConnectWiseAPIError: For API errors
        """
        # Get the total count first
        ct = self.get(
            f"{endpoint}/count",
            conditions=conditions if conditions else None,
            childconditions=childconditions if childconditions else None
        )

        # If count endpoint returns None (404), return empty list
        if ct is None:
            return []

        try:
            count = int(ct.get("count", 0))
        except (AttributeError, ValueError, TypeError):
            return []

        if pagesize is None:
            pagesize = 1000

        responses = []
        total_pages = (count + pagesize - 1) // pagesize

        for page in range(1, total_pages + 1):
            result = self.get(
                endpoint,
                conditions=conditions,
                childconditions=childconditions,
                fields=fields,
                pagesize=pagesize,
                page=page,
                orderby=orderby
            )

            # If a page returns None, stop pagination
            if result is None:
                break

            if isinstance(result, list):
                responses.extend(result)
            else:
                # Single result, wrap in list
                responses.append(result)

        return responses
    
    def patch(self, endpoint: str, record_id: int, operations: list) -> Optional[dict]:
        """
        Perform a PATCH request to update specific fields on a ConnectWise API entity.

        Args:
            endpoint: The API endpoint (e.g., "service/tickets")
            record_id: The ID of the record to update
            operations: List of patch operations following ConnectWise format
                       Each operation should have: {"op": "replace|add|remove",
                                                     "path": "fieldname",
                                                     "value": "newvalue"}

        Returns:
            dict: The updated record, or None if not found (404)

        Raises:
            ConnectWiseAPIError: For API errors (except 404)
        """
        url = f"{self.get_api_url()}/{endpoint}/{record_id}"
        headers = {
            "Authorization": self._auth_token,
            "clientId": self.client_id,
            "Content-Type": "application/json"
        }

        # Send request with operations as JSON array
        response = requests.patch(url, headers=headers, json=operations)

        # Handle 404s by returning None
        if response.status_code == 404:
            return None

        # Handle other errors
        if not response.ok:
            self._handle_response_error(response)

        return response.json()
    
    def post(self, endpoint: str, data: dict) -> dict:
        """
        Perform a POST request to create a new record in the ConnectWise API.

        Args:
            endpoint: The API endpoint (e.g., "service/tickets")
            data: Dictionary representing the JSON payload for the new record

        Returns:
            dict: The created record

        Raises:
            ConnectWiseAPIError: For API errors
        """
        url = f"{self.get_api_url()}/{endpoint}"
        headers = {
            "Authorization": self._auth_token,
            "clientId": self.client_id,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data)

        # Handle errors
        if not response.ok:
            self._handle_response_error(response)

        return response.json()

    def put(self, endpoint: str, record_id: int, data: dict) -> Optional[dict]:
        """
        Perform a PUT request to replace/update a record in the ConnectWise API.

        Args:
            endpoint: The API endpoint (e.g., "service/tickets")
            record_id: The ID of the record to update
            data: Dictionary representing the complete JSON payload

        Returns:
            dict: The updated record, or None if not found (404)

        Raises:
            ConnectWiseAPIError: For API errors (except 404)
        """
        url = f"{self.get_api_url()}/{endpoint}/{record_id}"
        headers = {
            "Authorization": self._auth_token,
            "clientId": self.client_id,
            "Content-Type": "application/json"
        }

        response = requests.put(url, headers=headers, json=data)

        # Handle 404s by returning None
        if response.status_code == 404:
            return None

        # Handle other errors
        if not response.ok:
            self._handle_response_error(response)

        return response.json()

    def delete(self, endpoint: str, record_id: int) -> bool:
        """
        Perform a DELETE request to remove a record from the ConnectWise API.

        Args:
            endpoint: The API endpoint (e.g., "service/tickets")
            record_id: The ID of the record to delete

        Returns:
            bool: True if deletion was successful, False if not found (404)

        Raises:
            ConnectWiseAPIError: For API errors (except 404)
        """
        url = f"{self.get_api_url()}/{endpoint}/{record_id}"
        headers = {
            "Authorization": self._auth_token,
            "clientId": self.client_id
        }

        response = requests.delete(url, headers=headers)

        # Handle 404s by returning False
        if response.status_code == 404:
            return False

        # Handle other errors
        if not response.ok:
            self._handle_response_error(response)

        # DELETE typically returns 204 No Content on success
        return response.status_code == 204 or response.ok