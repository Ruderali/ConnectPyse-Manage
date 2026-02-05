# ConnectWise Manage Python Integration

A Python toolkit for the ConnectWise Manage API with full type support and error handling.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🎯 **Typed Dataclasses** - Ticket, Configuration, and Note models with convenient properties
- 🔒 **Credential Protection** - SecretString wrapper prevents accidental password exposure
- 🚨 **Smart Error Handling** - Specific exceptions for different error types (404s return None)
- 🔄 **Full HTTP Support** - GET, POST, PATCH, PUT, DELETE methods
- 📦 **Opinionated Defaults** - TicketDefaults for consistent ticket creation
- 🎨 **Clean API** - No environment variable magic, explicit configuration

## Installation

```bash
pip install ConnectPyse-Manage
```

For development:
```bash
pip install -e .
```

## Quick Start

### 1. Initialize the Client

```python
from connectwise import ConnectWiseClient

cw = ConnectWiseClient(
    base_url="https://connect.example.com",
    client="YourCompany",
    username="api_user",
    password="api_password",
    client_id="your-client-id-uuid"
)
```

### 2. Work with Tickets

```python
# Get a ticket (returns Ticket object or None)
ticket = cw.get_ticket(ticket_id=12345)
if ticket:
    print(f"{ticket.summary} - {ticket.status_name}")
    print(f"Company: {ticket.company_name}")
    print(f"Priority: {ticket.priority_name}")

# Create a ticket
new_ticket = cw.create_ticket(
    summary="Server offline",
    body="PROD-WEB-01 is unreachable",
    company_id=250,
    board_id=1,
    priority_id=8
)
print(f"Created ticket #{new_ticket.id}")

# Update ticket status
updated = cw.update_ticket_status(
    ticket_id=new_ticket.id,
    status_id=456
)

# Add a note
note = cw.add_ticket_note(
    ticket_id=new_ticket.id,
    note_text="Investigating the issue",
    internal=True
)
```

### 3. Work with Configurations

```python
# Find configurations by name
configs = cw.get_configurations(
    conditions='name contains "PROD" AND company/id=250'
)

for config in configs:
    print(f"{config.name} - IP: {config.ipAddress}")

# Attach configuration to ticket
cw.attach_configuration(
    ticket_id=12345,
    config_id=configs[0].id
)
```

### 4. Search and Filter

```python
# Get open tickets for a company
tickets = cw.get_tickets(
    conditions="closedFlag=false AND company/id=250",
    pagesize=1000
)

# Search by summary text
urgent_tickets = cw.get_tickets(
    conditions='summary contains "urgent" AND priority/id>=8'
)
```

## Using Ticket Defaults

For applications that create many similar tickets:

```python
from connectwise import ConnectWiseClient, TicketDefaults

# Define defaults
defaults = TicketDefaults(
    company_id=250,
    board_id=1,
    priority_id=8,
    source_id=42  # RMM integration
)

# Initialize with defaults
cw = ConnectWiseClient(
    base_url="https://connect.example.com",
    client="YourCompany",
    username="api_user",
    password="api_password",
    client_id="uuid",
    ticket_defaults=defaults
)

# Create tickets without repeating parameters
ticket = cw.create_ticket(
    summary="Issue summary",
    body="Issue description"
    # company_id, board_id, priority_id, source_id use defaults
)
```

## Error Handling

The integration uses specific exceptions for different error types:

```python
from connectwise import (
    ConnectWiseAPIError,
    ConnectWiseNotFoundError,
    ConnectWiseRateLimitError,
    ConnectWiseBadRequestError
)

try:
    ticket = cw.update_ticket_status(ticket_id=123, status_id=456)
except ConnectWiseNotFoundError:
    print("Ticket doesn't exist")
except ConnectWiseRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ConnectWiseBadRequestError as e:
    print(f"Invalid request: {e}")
except ConnectWiseAPIError as e:
    print(f"API error [{e.status_code}]: {e}")
```

**Note:** 404s return `None` for get operations instead of raising exceptions:

```python
ticket = cw.get_ticket(ticket_id=999999)
if ticket is None:
    print("Ticket not found")  # No exception raised
```

## Dataclass Properties

All models provide convenient properties for nested data:

```python
ticket = cw.get_ticket(ticket_id=12345)

# Clean property access
print(ticket.company_name)      # Instead of ticket.company.get('name')
print(ticket.status_name)       # Instead of ticket.status.get('name')
print(ticket.priority_name)     # Instead of ticket.priority.get('name')

# Datetime parsing included
if ticket.is_closed:
    print(f"Closed: {ticket.closed_datetime}")  # Returns datetime object

# Configuration properties
config = cw.get_configuration(config_id=67890)
print(f"{config.name} - {config.type_name}")
print(f"Company: {config.company_name}")
print(f"Active: {config.is_active}")
```

## Advanced Usage

### Custom Fields and Filtering

```python
# Get tickets with specific fields only (returns raw dict)
result = cw.get(
    "service/tickets",
    conditions="closedFlag=false",
    fields="id,summary,status"
)

# Use base HTTP methods for custom endpoints
result = cw.post("custom/endpoint", data={...})
result = cw.patch("service/tickets", record_id=123, operations=[...])
success = cw.delete("service/tickets", record_id=123)
```

### Complete Workflow Example

```python
# Find server configuration
configs = cw.get_configurations(
    conditions='name="PROD-WEB-01" AND company/id=250'
)

if configs:
    config = configs[0]

    # Create ticket
    ticket = cw.create_ticket(
        summary=f"Server {config.name} Offline",
        body=f"Server unreachable. IP: {config.ipAddress}",
        company_id=250,
        board_id=1,
        priority_id=8
    )

    # Attach configuration
    cw.attach_configuration(ticket.id, config.id)

    # Add investigation note
    cw.add_ticket_note(
        ticket_id=ticket.id,
        note_text="Checking server connectivity",
        internal=True
    )

    # Get ticket URL for external systems
    ticket_url = cw.get_ticket_url(ticket.id)
    print(f"View ticket: {ticket_url}")
```

## Performance Tips

1. **Use specific conditions** to limit results:
   ```python
   # ❌ Slow - fetches everything
   tickets = cw.get_tickets()

   # ✅ Fast - filtered query
   tickets = cw.get_tickets(conditions="company/id=250 AND closedFlag=false")
   ```

2. **Leverage the fields parameter** for partial data:
   ```python
   result = cw.get("service/tickets", fields="id,summary,status")
   ```

3. **Handle rate limits gracefully**:
   ```python
   import time

   try:
       tickets = cw.get_tickets(conditions="...")
   except ConnectWiseRateLimitError as e:
       if e.retry_after:
           time.sleep(e.retry_after)
           tickets = cw.get_tickets(conditions="...")
   ```

## Credential Security

Passwords are automatically wrapped in `SecretString` to prevent accidental exposure in logs:

```python
cw = ConnectWiseClient(...)
print(cw._password)  # Output: **********
```

## ConnectWise Conditions Syntax

ConnectWise uses a specific syntax for filtering:

```python
# Basic operators: =, !=, <, >, <=, >=
conditions = "closedFlag=false"

# Logical operators: AND, OR
conditions = "closedFlag=false AND company/id=250"

# String operators: contains, like
conditions = 'summary contains "server"'
conditions = 'name like "PROD-%"'

# Nested properties
conditions = "company/id=250 AND status/name='Open'"

# Complex conditions
conditions = "(closedFlag=false AND priority/id>=8) OR summary contains 'urgent'"
```

## Documentation

- [API Reference](docs/api-reference.md) - Complete API documentation
- [AI Agent Guide](docs/agents.md) - Guide for AI assistants using this library

## Requirements

- Python 3.9+
- `requests` library

## Development

```bash
# Clone the repository
git clone https://github.com/Ruderali/ConnectPyse.git
cd ConnectPyse

# Install in development mode
pip install -e .

# Run tests
pytest
```

## Contributing

Contributions are welcome! This library aims to stay a pure API wrapper without business logic.

**Design Principles:**
- Keep it simple - no complex abstractions
- Return dataclasses from high-level methods
- Return raw JSON from base HTTP methods
- 404s return None for get operations
- Raise specific exceptions for errors
- No environment variable reading
- No business logic

## License

MIT License - see LICENSE file for details

## Related Projects

- [npycentral](https://github.com/Ruderali/npycentral) - N-Central RMM Python integration (same author)

## Support

For issues and questions:
- GitHub Issues: [Ruderali/ConnectPyse/issues](https://github.com/Ruderali/ConnectPyse/issues)
- Documentation: See `docs/` directory

---

**Note:** This is an unofficial library and is not affiliated with or endorsed by ConnectWise.
