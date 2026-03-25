import base64
import logging
import time
import requests
from typing import Optional

from .mixins.ticket_mixin import TicketMixin
from .mixins.configuration_mixin import ConfigurationMixin
from .mixins.companies_mixin import CompaniesMixin
from .mixins.boards_mixin import BoardsMixin
from .mixins.lookup_mixin import LookupMixin
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

logger = logging.getLogger(__name__)


class ConnectWiseClient(TicketMixin, ConfigurationMixin, CompaniesMixin, BoardsMixin, LookupMixin):
    """ConnectWise API Client with modular functionality via mixins."""
    
    def __init__(
        self,
        base_url: str,
        client: str,
        username: str,
        password: str,
        client_id: str,
        ticket_defaults: Optional[TicketDefaults] = None,
        max_retries: int = 3,
        retry_backoff_base: int = 2,
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
            max_retries: Number of retries on 429 rate limit responses (default: 3)
            retry_backoff_base: Base for exponential backoff in seconds (default: 2 → 2s, 4s, 8s)
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

        # Retry configuration
        self.max_retries = max_retries
        self.retry_backoff_base = retry_backoff_base

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

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, headers=headers, params=params)
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < self.max_retries:
                    wait = self.retry_backoff_base ** attempt
                    logger.warning(f"Connection error on GET {endpoint}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait)
                    continue
                raise ConnectWiseAPIError(f"Connection failed for {endpoint}: {e}")

            # Handle 404s by returning None (expected case for missing resources)
            if response.status_code == 404:
                return None

            if response.status_code == 429 and attempt < self.max_retries:
                retry_after = response.headers.get('Retry-After')
                wait = int(retry_after) if retry_after else self.retry_backoff_base ** attempt
                logger.warning(f"Rate limited on GET {endpoint}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(wait)
                continue

            # Handle other errors
            if not response.ok:
                self._handle_response_error(response)

            return response.json()
    
    def get_count(self, endpoint: str, conditions: str = "",
                  childconditions: str = "") -> Optional[int]:
        """
        Return the total record count for an endpoint without fetching any records.

        Args:
            endpoint: The API endpoint (e.g., "service/tickets")
            conditions: ConnectWise conditions string for filtering
            childconditions: Child conditions string for filtering

        Returns:
            int: Total record count, or None if the endpoint was not found (404)

        Raises:
            ConnectWiseAPIError: For API errors
        """
        result = self.get(
            f"{endpoint}/count",
            conditions=conditions if conditions else None,
            childconditions=childconditions if childconditions else None
        )
        if result is None:
            return None
        try:
            return int(result.get("count", 0))
        except (AttributeError, ValueError, TypeError):
            return 0

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
        count = self.get_count(endpoint, conditions=conditions, childconditions=childconditions)
        if count is None:
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

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.patch(url, headers=headers, json=operations)
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < self.max_retries:
                    wait = self.retry_backoff_base ** attempt
                    logger.warning(f"Connection error on PATCH {endpoint}/{record_id}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait)
                    continue
                raise ConnectWiseAPIError(f"Connection failed for {endpoint}/{record_id}: {e}")

            # Handle 404s by returning None
            if response.status_code == 404:
                return None

            if response.status_code == 429 and attempt < self.max_retries:
                retry_after = response.headers.get('Retry-After')
                wait = int(retry_after) if retry_after else self.retry_backoff_base ** attempt
                logger.warning(f"Rate limited on PATCH {endpoint}/{record_id}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(wait)
                continue

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

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(url, headers=headers, json=data)
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < self.max_retries:
                    wait = self.retry_backoff_base ** attempt
                    logger.warning(f"Connection error on POST {endpoint}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait)
                    continue
                raise ConnectWiseAPIError(f"Connection failed for {endpoint}: {e}")

            if response.status_code == 429 and attempt < self.max_retries:
                retry_after = response.headers.get('Retry-After')
                wait = int(retry_after) if retry_after else self.retry_backoff_base ** attempt
                logger.warning(f"Rate limited on POST {endpoint}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(wait)
                continue

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

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.put(url, headers=headers, json=data)
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt < self.max_retries:
                    wait = self.retry_backoff_base ** attempt
                    logger.warning(f"Connection error on PUT {endpoint}/{record_id}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(wait)
                    continue
                raise ConnectWiseAPIError(f"Connection failed for {endpoint}/{record_id}: {e}")

            # Handle 404s by returning None
            if response.status_code == 404:
                return None

            if response.status_code == 429 and attempt < self.max_retries:
                retry_after = response.headers.get('Retry-After')
                wait = int(retry_after) if retry_after else self.retry_backoff_base ** attempt
                logger.warning(f"Rate limited on PUT {endpoint}/{record_id}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(wait)
                continue

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

        for attempt in range(self.max_retries + 1):
            response = requests.delete(url, headers=headers)

            # Handle 404s by returning False
            if response.status_code == 404:
                return False

            if response.status_code == 429 and attempt < self.max_retries:
                retry_after = response.headers.get('Retry-After')
                wait = int(retry_after) if retry_after else self.retry_backoff_base ** attempt
                logger.warning(f"Rate limited on DELETE {endpoint}/{record_id}, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(wait)
                continue

            # Handle other errors
            if not response.ok:
                self._handle_response_error(response)

            # DELETE typically returns 204 No Content on success
            return response.status_code == 204 or response.ok