# ConnectWise Integration - AI Agent Guide

This guide helps AI agents (like Claude, GPT, etc.) understand how to use the ConnectWise integration effectively when assisting users with ConnectWise API tasks.

## Quick Reference

### What This Integration Does

This is a Python wrapper for the ConnectWise Manage API that:
- Provides typed dataclasses for Tickets, Configurations, and Notes
- Handles authentication and error handling automatically
- Returns proper exceptions instead of error dicts
- Supports all standard HTTP methods (GET, POST, PATCH, PUT, DELETE)
- Protects credentials from accidental logging

### Basic Usage Pattern

```python
from integrations.connectwise import ConnectWiseClient, TicketDefaults

# Initialize client (all parameters required)
cw = ConnectWiseClient(
    base_url="https://connect.example.com",
    client="CompanyName",
    username="api_user",
    password="api_password",
    client_id="uuid-string"
)

# Get a ticket (returns Ticket object or None)
ticket = cw.get_ticket(ticket_id=12345)
if ticket:
    print(f"{ticket.summary} - Status: {ticket.status_name}")

# Create a ticket (returns Ticket object)
new_ticket = cw.create_ticket(
    summary="Issue summary",
    body="Detailed description",
    company_id=250,
    board_id=1,
    priority_id=8
)
```

## Key Design Principles

### 1. Dataclasses Over Dicts

**High-level mixin methods return dataclasses:**
```python
# ✅ Returns Ticket object
ticket = cw.get_ticket(ticket_id=123)
print(ticket.status_name)  # Uses property

# ✅ Returns List[Ticket]
tickets = cw.get_tickets(conditions="closedFlag=false")
```

**Base HTTP methods return raw JSON:**
```python
# ✅ Returns dict (for custom endpoints or fields parameter)
result = cw.get("service/tickets/123", fields="id,summary")
```

### 2. 404s Return None (Not Exceptions)

```python
ticket = cw.get_ticket(ticket_id=999999)
if ticket is None:
    print("Ticket not found")  # No exception raised
```

### 3. Explicit Over Implicit

- No environment variables in the library
- All client parameters are required (except optional ticket_defaults)
- Users control configuration management

### 4. Properties for Convenience

Dataclasses provide properties for nested data:

```python
ticket = cw.get_ticket(ticket_id=123)

# Instead of: ticket.company.get('name')
print(ticket.company_name)  # ✅ Property

# Instead of: ticket.status.get('name')
print(ticket.status_name)  # ✅ Property

# Datetime parsing included
print(ticket.closed_datetime)  # ✅ Returns datetime object
```

## Common Patterns

### Finding Tickets

```python
# Get open tickets for a company
tickets = cw.get_tickets(
    conditions="closedFlag=false AND company/id=250",
    pagesize=1000
)

# Search by summary
tickets = cw.get_tickets(
    conditions='summary contains "server offline"'
)
```

### Working with Configurations

```python
# Get all configurations for a company
configs = cw.get_configurations(
    conditions="company/id=250"
)

# Attach configuration to ticket
config = cw.attach_configuration(
    ticket_id=12345,
    config_id=67890
)
```

### Managing Ticket Notes

```python
# Add internal note
note = cw.add_ticket_note(
    ticket_id=12345,
    note_text="Internal investigation notes",
    internal=True
)

# Get all notes
notes = cw.get_ticket_notes(ticket_id=12345)
for note in notes:
    if note.is_internal:
        print(f"Internal: {note.text}")
```

### Using Ticket Defaults

For creating multiple tickets with same defaults:

```python
from integrations.connectwise import TicketDefaults

defaults = TicketDefaults(
    company_id=250,
    board_id=1,
    priority_id=8,
    source_id=42  # RMM integration
)

cw = ConnectWiseClient(
    base_url=url,
    client=client,
    username=username,
    password=password,
    client_id=client_id,
    ticket_defaults=defaults
)

# Now create_ticket uses defaults if not specified
ticket = cw.create_ticket(
    summary="Issue",
    body="Description"
    # company_id, board_id, priority_id use defaults
)
```

## Error Handling

### Exception Hierarchy

```python
from integrations.connectwise import (
    ConnectWiseAPIError,        # Base exception
    ConnectWiseNotFoundError,   # 404
    ConnectWiseBadRequestError, # 400
    ConnectWiseRateLimitError,  # 429
    ConnectWiseServerError      # 5xx
)

try:
    ticket = cw.update_ticket_status(ticket_id=123, status_id=456)
except ConnectWiseNotFoundError:
    print("Ticket doesn't exist")
except ConnectWiseRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ConnectWiseAPIError as e:
    print(f"API error: {e}")
```

### 404s Don't Raise

```python
# get_ticket returns None for 404s
ticket = cw.get_ticket(ticket_id=999999)
if ticket is None:
    # Handle missing ticket
    pass
```

## Advanced Usage

### Partial Data with Fields Parameter

When using the `fields` parameter, dataclasses handle partial data gracefully:

```python
# Get limited fields (returns dict)
result = cw.get(
    "service/tickets",
    conditions="closedFlag=false",
    fields="id,summary,status"
)

# Full ticket retrieval (returns Ticket object)
ticket = cw.get_ticket(ticket_id=123)
```

### Updating Tickets

```python
# Update status
ticket = cw.update_ticket_status(
    ticket_id=123,
    status_id=456
)

# Update priority
ticket = cw.update_ticket_priority(
    ticket_id=123,
    priority_id=8
)

# Generic field update
ticket = cw.update_ticket_field(
    ticket_id=123,
    field_path="/customFieldName",
    value="new value"
)
```

### Pagination

The `get_all()` method handles pagination automatically:

```python
# Automatically paginates through all results
all_tickets = cw.get_tickets(conditions="closedFlag=false")
print(f"Found {len(all_tickets)} tickets")
```

## Credential Security

Passwords are wrapped in `SecretString` to prevent accidental exposure:

```python
cw = ConnectWiseClient(...)
print(cw._password)  # Prints: **********

# Access only when needed (internal use)
actual_password = cw._password.get_secret_value()
```

## Common Pitfalls to Avoid

### ❌ Don't: Use .get() on Dataclass Attributes

```python
# ❌ Wrong
ticket = cw.get_ticket(ticket_id=123)
company_name = ticket.company.get('name')  # Works but verbose

# ✅ Right
company_name = ticket.company_name  # Use property
```

### ❌ Don't: Expect Environment Variables

```python
# ❌ Wrong - library doesn't read env vars
cw = ConnectWiseClient()  # Will fail

# ✅ Right - pass all parameters
cw = ConnectWiseClient(
    base_url=Config.CW_URL,  # Your app reads env vars
    client=Config.CW_CLIENT,
    username=Config.CW_USERNAME,
    password=Config.CW_PASSWORD,
    client_id=Config.CW_CLIENT_ID
)
```

### ❌ Don't: Catch 404s as Exceptions for Get Operations

```python
# ❌ Wrong - 404s return None for get operations
try:
    ticket = cw.get_ticket(ticket_id=123)
except ConnectWiseNotFoundError:
    pass  # This won't catch 404s

# ✅ Right
ticket = cw.get_ticket(ticket_id=123)
if ticket is None:
    print("Not found")
```

## API Endpoint Structure

ConnectWise uses this endpoint pattern:
- Tickets: `service/tickets`
- Configurations: `company/configurations`
- Notes: `service/tickets/{id}/notes`
- Companies: `company/companies`

Base HTTP methods follow this pattern:
```python
# GET single
result = cw.get("service/tickets/123")

# GET with conditions
result = cw.get("service/tickets", conditions="closedFlag=false")

# POST
result = cw.post("service/tickets", data={...})

# PATCH
result = cw.patch("service/tickets", record_id=123, operations=[...])

# PUT
result = cw.put("service/tickets", record_id=123, data={...})

# DELETE
success = cw.delete("service/tickets", record_id=123)
```

## Rate Limiting

ConnectWise APIs have rate limits (typically 60-100 requests/minute). The integration detects 429 responses:

```python
try:
    tickets = cw.get_tickets(conditions="...")
except ConnectWiseRateLimitError as e:
    if e.retry_after:
        time.sleep(e.retry_after)
        tickets = cw.get_tickets(conditions="...")
```

## When Helping Users

1. **Always pass all required parameters** - Don't assume env vars
2. **Use high-level methods when available** - They return dataclasses
3. **Check for None on get operations** - Don't catch exceptions
4. **Use properties on dataclasses** - Cleaner than dict access
5. **Be specific about conditions** - Help users avoid 100k+ result queries
6. **Suggest ticket_defaults** - For apps creating many similar tickets

## Example: Complete Ticket Workflow

```python
from integrations.connectwise import ConnectWiseClient, TicketDefaults

# Setup
defaults = TicketDefaults(company_id=250, board_id=1, priority_id=8)
cw = ConnectWiseClient(base_url=url, client=client,
                       username=user, password=pwd,
                       client_id=cid, ticket_defaults=defaults)

# Create ticket
ticket = cw.create_ticket(
    summary="Server Offline",
    body="Server PROD-WEB-01 is unreachable"
)
print(f"Created ticket #{ticket.id}")

# Attach configuration
config = cw.get_configurations(
    conditions='name="PROD-WEB-01" AND company/id=250'
)[0]
cw.attach_configuration(ticket.id, config.id)

# Add note
cw.add_ticket_note(
    ticket_id=ticket.id,
    note_text="Investigating server connectivity",
    internal=True
)

# Update status when resolved
updated = cw.update_ticket_status(
    ticket_id=ticket.id,
    status_id=456  # Resolved status
)
print(f"Ticket closed: {updated.is_closed}")
```

This covers the most common use cases. For complete API reference, see [api-reference.md](api-reference.md).
