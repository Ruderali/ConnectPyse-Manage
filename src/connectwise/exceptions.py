"""Custom exceptions for ConnectWise API interactions."""


class ConnectWiseError(Exception):
    """Base exception for ConnectWise API errors."""
    pass


class ConnectWiseAPIError(ConnectWiseError):
    """Raised when the ConnectWise API returns an error response."""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        """
        Initialize API error with details.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Raw response data from API
        """
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {super().__str__()}"
        return super().__str__()


class ConnectWiseAuthenticationError(ConnectWiseAPIError):
    """Raised when authentication fails (401)."""
    pass


class ConnectWiseNotFoundError(ConnectWiseAPIError):
    """Raised when a resource is not found (404)."""
    pass


class ConnectWiseBadRequestError(ConnectWiseAPIError):
    """Raised when the request is invalid (400)."""
    pass


class ConnectWiseRateLimitError(ConnectWiseAPIError):
    """Raised when API rate limit is exceeded (429)."""

    def __init__(self, message: str = "API rate limit exceeded", retry_after: int = None, **kwargs):
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (from Retry-After header)
            **kwargs: Additional arguments for ConnectWiseAPIError
        """
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class ConnectWiseServerError(ConnectWiseAPIError):
    """Raised when the ConnectWise server returns a 5xx error."""
    pass


class ConnectWiseConfigurationError(ConnectWiseError):
    """Raised when the client is misconfigured."""
    pass
