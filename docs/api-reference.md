# ConnectWise Integration - API Reference

Complete API reference for the ConnectWise Manage integration library.

## Table of Contents

- [Client Setup](#client-setup)
- [Tickets](#tickets)
  - [get_ticket](#get_ticket)
  - [get_tickets](#get_tickets)
  - [get_ticket_count](#get_ticket_count)
- [Configurations](#configurations)
  - [get_configuration_count](#get_configuration_count)
- [Notes](#notes)
- [Companies](#companies)
  - [get_companies](#get_companies)
  - [get_company](#get_company)
  - [get_company_count](#get_company_count)
  - [get_company_statuses](#get_company_statuses)
- [Boards](#boards)
  - [get_boards](#get_boards)
  - [get_board_count](#get_board_count)
  - [get_board_statuses](#get_board_statuses)
  - [get_board_types](#get_board_types)
  - [get_board_subtypes](#get_board_subtypes)
  - [get_board_items](#get_board_items)
- [Lookups](#lookups)
  - [get_priorities](#get_priorities)
  - [get_sources](#get_sources)
- [Agreements](#agreements)
  - [get_agreements](#get_agreements)
  - [get_agreement](#get_agreement)
  - [get_agreement_count](#get_agreement_count)
  - [get_company_agreements](#get_company_agreements)
  - [get_agreement_additions](#get_agreement_additions)
  - [get_agreement_addition](#get_agreement_addition)
  - [create_agreement_addition](#create_agreement_addition)
- [Time Entries](#time-entries)
  - [get_time_entries](#get_time_entries)
  - [get_time_entry](#get_time_entry)
  - [get_time_entry_count](#get_time_entry_count)
  - [get_member_time_entries](#get_member_time_entries)
  - [get_ticket_time_entries](#get_ticket_time_entries)
  - [create_time_entry](#create_time_entry)
- [Members](#members)
  - [get_members](#get_members)
  - [get_member](#get_member)
  - [get_member_by_identifier](#get_member_by_identifier)
  - [get_member_count](#get_member_count)
- [Contacts](#contacts)
  - [get_contacts](#get_contacts)
  - [get_contact](#get_contact)
  - [get_contact_count](#get_contact_count)
  - [get_ticket_contact](#get_ticket_contact)
  - [get_company_contacts](#get_company_contacts)
  - [create_contact](#create_contact)
- [Invoices](#invoices)
  - [get_invoices](#get_invoices)
  - [get_invoice](#get_invoice)
  - [get_invoice_count](#get_invoice_count)
  - [get_company_invoices](#get_company_invoices)
  - [get_agreement_invoices](#get_agreement_invoices)
- [Projects](#projects)
  - [get_projects](#get_projects)
  - [get_project](#get_project)
  - [get_project_count](#get_project_count)
  - [get_company_projects](#get_company_projects)
  - [get_project_phases](#get_project_phases)
  - [get_project_phase](#get_project_phase)
  - [get_project_tickets](#get_project_tickets)
  - [get_project_time_entries](#get_project_time_entries)
  - [create_project](#create_project)
  - [create_project_phase](#create_project_phase)
- [Opportunities](#opportunities)
  - [get_opportunities](#get_opportunities)
  - [get_opportunity](#get_opportunity)
  - [get_opportunity_count](#get_opportunity_count)
  - [get_company_opportunities](#get_company_opportunities)
  - [get_open_opportunities](#get_open_opportunities)
- [Schedule Entries](#schedule-entries)
  - [get_schedule_entries](#get_schedule_entries)
  - [get_schedule_entry](#get_schedule_entry)
  - [get_schedule_entry_count](#get_schedule_entry_count)
  - [get_member_schedule](#get_member_schedule)
  - [get_ticket_schedule](#get_ticket_schedule)
  - [create_schedule_entry](#create_schedule_entry)
- [Base HTTP Methods](#base-http-methods)
  - [get](#get)
  - [get_all](#get_all)
  - [get_count](#get_count)
- [Exceptions](#exceptions)
- [Models](#models)
- [Utilities](#utilities)

---

## Client Setup

### ConnectWiseClient

Main client class for ConnectWise API interactions.

```python
from integrations.connectwise import ConnectWiseClient, TicketDefaults

client = ConnectWiseClient(
    base_url: str,
    client: str,
    username: str,
    password: str,
    client_id: str,
    ticket_defaults: Optional[TicketDefaults] = None,
    max_retries: int = 3,
    retry_backoff_base: int = 2
)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `base_url` | `str` | Yes | ConnectWise base URL (e.g., `https://connect.example.com`) |
| `client` | `str` | Yes | ConnectWise client/company identifier |
| `username` | `str` | Yes | API username |
| `password` | `str` | Yes | API password (automatically wrapped in SecretString) |
| `client_id` | `str` | Yes | Client ID for API requests |
| `ticket_defaults` | `TicketDefaults` | No | Optional defaults for ticket creation |
| `max_retries` | `int` | No | Retries on 429 rate limit responses (default: 3) |
| `retry_backoff_base` | `int` | No | Base for exponential backoff in seconds (default: 2 → 2s, 4s, 8s) |

**Example:**

```python
cw = ConnectWiseClient(
    base_url="https://connect.newtrend.com.au",
    client="NewtrendIT",
    username="api_user",
    password="secret",
    client_id="d420d537-7997-466e-bc72-575bc7553d97"
)
```

### TicketDefaults

Optional configuration for ticket creation defaults.

```python
from integrations.connectwise import TicketDefaults

defaults = TicketDefaults(
    company_id: Optional[int] = None,
    board_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    status_id: Optional[int] = None,
    type_id: Optional[int] = None,
    source_id: Optional[int] = None
)
```

**Example:**

```python
defaults = TicketDefaults(
    company_id=250,
    board_id=1,
    priority_id=8,
    source_id=42
)

cw = ConnectWiseClient(..., ticket_defaults=defaults)
```

---

### Impersonation (`run_as`)

Every method that makes an API call accepts an optional `run_as` parameter, letting a single
long-lived client instance make individual calls as a different ConnectWise member — for example,
a web app holding one privileged credential that needs to act as whichever user is logged in for
that request.

`run_as` takes a **precomputed auth token**, not raw credentials. Build one with `compute_auth()`,
which mirrors how the client builds its own primary-credential token internally:

```python
token = client.compute_auth(identifier: str, secret: str) -> str
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | `str` | Yes | Username, or API public key, of the member to act as |
| `secret` | `str` | Yes | Password, or API private key, of the member to act as |

**Returns:** A `"Basic <base64>"` auth header value, usable as `run_as` on any call.

> **Note:** ConnectWise's API key model maps the public key to the `identifier` slot and the
> private key to the `secret` slot — same wire format as a username/password pair, different
> semantic meaning. `compute_auth()` uses the client's own `client` (company) identifier
> internally, so you only ever pass the member-specific identifier/secret pair.

Compute the token once per user/request and reuse it across calls — there's no need to recompute
it for every method call:

```python
# Precompute once (e.g. per incoming request in a web app)
run_as_token = cw.compute_auth(identifier=member_public_key, secret=member_private_key)

# Reuse it across as many calls as needed — each executes as that member,
# not as the client's primary credential
ticket = cw.get_ticket(ticket_id=12345, run_as=run_as_token)
cw.update_ticket_status(ticket_id=12345, status_id=456, run_as=run_as_token)
note = cw.add_ticket_note(
    ticket_id=12345,
    note_text="Picked this up",
    run_as=run_as_token
)
```

Omitting `run_as` (or passing `None`) uses the client's own primary credential, unchanged from
default behavior. `run_as` is safe to use concurrently across requests sharing one client
instance — it's passed per-call and never mutates shared client state, so concurrent calls under
different identities won't cross-contaminate each other's auth.

---

## Tickets

### get_ticket

Retrieve a specific ticket by ID.

```python
ticket = client.get_ticket(ticket_id: int, run_as: Optional[str] = None) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Ticket` object or `None` if not found

**Example:**

```python
ticket = cw.get_ticket(ticket_id=12345)
if ticket:
    print(f"{ticket.summary} - Status: {ticket.status_name}")
    print(f"Company: {ticket.company_name}")
    print(f"Closed: {ticket.is_closed}")
else:
    print("Ticket not found")
```

### get_tickets

Retrieve multiple tickets with optional filtering.

```python
tickets = client.get_tickets(
    conditions: str = "",
    pagesize: int = 1000,
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `pagesize` | `int` | No | Results per page when paginating all records (default: 1000). **Do not use this to cap results** — use `limit` instead. |
| `orderby` | `str` | No | Order by clause. **Use `id desc` rather than `dateEntered desc`** on large environments — `dateEntered` is not indexed and will cause a server timeout. |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Ticket` objects

**Example:**

```python
# Get all open tickets for a company
tickets = cw.get_tickets(conditions="closedFlag=false AND company/id=250")

# Get the 5 most recently created tickets — use id desc, not dateEntered desc
tickets = cw.get_tickets(orderby="id desc", limit=5)

# Search by summary
tickets = cw.get_tickets(conditions='summary contains "server offline"')

print(f"Found {len(tickets)} tickets")
for ticket in tickets:
    print(f"#{ticket.id}: {ticket.summary}")
```

### get_ticket_count

Return the total number of tickets matching the given conditions without fetching any ticket data. Use this to check volumes before committing to a potentially expensive `get_tickets` call.

```python
count = client.get_ticket_count(
    conditions: str = "",
    run_as: Optional[str] = None
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

**Example:**

```python
from datetime import datetime, timezone, timedelta

seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
date_str = seven_days_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
conditions = f'board/name="Events" AND dateEntered>=[{date_str}]'

# Check volume first — no records fetched
count = cw.get_ticket_count(conditions=conditions)
print(f"{count} tickets in the last 7 days")

if count > 500:
    print("Too many to fetch at once — consider narrowing your conditions")
else:
    tickets = cw.get_tickets(conditions=conditions)
```

---

### create_ticket

Create a new ticket in ConnectWise.

```python
ticket = client.create_ticket(
    summary: str,
    body: str,
    company_id: int = None,
    board_id: int = None,
    priority_id: int = None,
    status_id: int = None,
    type_id: int = None,
    source_id: int = None,
    config_ids: List[int] = None,
    run_as: Optional[str] = None
) -> Ticket
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `summary` | `str` | Yes | Ticket summary/subject |
| `body` | `str` | Yes | Ticket body/description |
| `company_id` | `int` | No | Company ID (uses defaults if not provided) |
| `board_id` | `int` | No | Board ID (uses defaults if not provided) |
| `priority_id` | `int` | No | Priority ID (uses defaults if not provided) |
| `status_id` | `int` | No | Status ID (uses defaults if not provided) |
| `type_id` | `int` | No | Type ID (uses defaults if not provided) |
| `source_id` | `int` | No | Source ID (uses defaults if not provided) |
| `config_ids` | `List[int]` | No | List of configuration IDs to attach |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `Ticket` object

**Example:**

```python
ticket = cw.create_ticket(
    summary="Server PROD-WEB-01 Offline",
    body="Server has been unreachable since 10:30 AM",
    company_id=250,
    board_id=1,
    priority_id=8,
    type_id=322,
    config_ids=[67890]
)
print(f"Created ticket #{ticket.id}")
```

### update_ticket_status

Update the status of a ticket.

```python
ticket = client.update_ticket_status(
    ticket_id: int,
    status_id: int,
    run_as: Optional[str] = None
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `status_id` | `int` | Yes | New status ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated `Ticket` object or `None` if not found

**Example:**

```python
ticket = cw.update_ticket_status(
    ticket_id=12345,
    status_id=456
)
if ticket:
    print(f"Status updated to: {ticket.status_name}")
```

### update_ticket_priority

Update the priority of a ticket.

```python
ticket = client.update_ticket_priority(
    ticket_id: int,
    priority_id: int,
    run_as: Optional[str] = None
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `priority_id` | `int` | Yes | New priority ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated `Ticket` object or `None` if not found

**Example:**

```python
ticket = cw.update_ticket_priority(
    ticket_id=12345,
    priority_id=8
)
```

### update_ticket_company

Update the company associated with a ticket.

```python
ticket = client.update_ticket_company(
    ticket_id: int,
    company_id: int,
    run_as: Optional[str] = None
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `company_id` | `int` | Yes | New company ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated `Ticket` object or `None` if not found

**Example:**

```python
ticket = cw.update_ticket_company(
    ticket_id=12345,
    company_id=250
)
```

### update_ticket_field

Update any ticket field using PATCH operation.

```python
ticket = client.update_ticket_field(
    ticket_id: int,
    field_path: str,
    value: any,
    run_as: Optional[str] = None
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `field_path` | `str` | Yes | Field path (e.g., "/summary", "/customField") |
| `value` | `any` | Yes | New value for the field |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated `Ticket` object or `None` if not found

**Example:**

```python
ticket = cw.update_ticket_field(
    ticket_id=12345,
    field_path="/summary",
    value="Updated Summary Text"
)
```

### merge_ticket

Merge a child ticket into a parent ticket.

```python
result = client.merge_ticket(
    child_ticket_id: int,
    parent_ticket_id: int,
    child_status_id: int,
    run_as: Optional[str] = None
) -> dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `child_ticket_id` | `int` | Yes | Child ticket ID |
| `parent_ticket_id` | `int` | Yes | Parent ticket ID |
| `child_status_id` | `int` | Yes | Status to set on child ticket |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Dict with keys: `child_ticket` (Ticket), `merge_response` (dict)

**Example:**

```python
result = cw.merge_ticket(
    child_ticket_id=12345,
    parent_ticket_id=12340,
    child_status_id=1248
)
print(f"Merged ticket #{result['child_ticket'].id}")
```

### add_ticket_note

Add a note to a ticket.

```python
note = client.add_ticket_note(
    ticket_id: int,
    note_text: str,
    internal: bool = True,
    run_as: Optional[str] = None
) -> Note
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `note_text` | `str` | Yes | Note content |
| `internal` | `bool` | No | Whether note is internal (default: True) |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `Note` object

**Example:**

```python
# Internal note
note = cw.add_ticket_note(
    ticket_id=12345,
    note_text="Investigating server connectivity issues",
    internal=True
)

# External note (visible to customer)
note = cw.add_ticket_note(
    ticket_id=12345,
    note_text="We are investigating the issue",
    internal=False
)
```

### get_ticket_notes

Get all notes for a ticket.

```python
notes = client.get_ticket_notes(ticket_id: int, run_as: Optional[str] = None) -> List[Note]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Note` objects

**Example:**

```python
notes = cw.get_ticket_notes(ticket_id=12345)
for note in notes:
    note_type = "Internal" if note.is_internal else "External"
    print(f"[{note_type}] {note.text}")
    if note.created_datetime:
        print(f"  Created: {note.created_datetime}")
```

### get_ticket_url

Get the full URL to view a ticket in ConnectWise UI.

```python
url = client.get_ticket_url(ticket_id: int) -> str
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |

**Returns:** Full URL string

**Example:**

```python
url = cw.get_ticket_url(ticket_id=12345)
print(f"View ticket: {url}")
# Output: https://connect.example.com/v4_6_release/services/system_io/Service/fv_sr100_request.rails?service_recid=12345
```

### get_ticket_time_entries

Get all time entries charged to a specific service ticket.

```python
entries = client.get_ticket_time_entries(
    ticket_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[TimeEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `conditions` | `str` | No | Additional conditions string to further filter results |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `TimeEntry` objects

**Notes:** Internally filters on `chargeToId={ticket_id} AND chargeToType="ServiceTicket"`.

**Example:**

```python
entries = cw.get_ticket_time_entries(ticket_id=12345)
total_hours = sum(e.actualHours or 0 for e in entries)
print(f"{len(entries)} time entries — {total_hours:.2f} hours total")

for e in entries:
    print(f"  {e.member_name}: {e.actualHours}h  billable={e.is_billable}")
```

### get_ticket_contact

Get the full `Contact` object for the contact assigned to a ticket.

```python
contact = client.get_ticket_contact(ticket_id: int, run_as: Optional[str] = None) -> Optional[Contact]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Contact` object, or `None` if the ticket has no contact assigned or the ticket is not found.

**Notes:** Fetches the ticket first to extract the contact ID, then fetches the full contact record.

**Example:**

```python
contact = cw.get_ticket_contact(ticket_id=12345)
if contact:
    print(f"Contact: {contact.full_name} ({contact.company_name})")
    if contact.primary_email:
        print(f"Email: {contact.primary_email}")
```

---

## Configurations

### get_configuration

Get details of a specific configuration.

```python
config = client.get_configuration(config_id: int, run_as: Optional[str] = None) -> Optional[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_id` | `int` | Yes | Configuration ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Configuration` object or `None` if not found

**Example:**

```python
config = cw.get_configuration(config_id=67890)
if config:
    print(f"{config.name} - {config.type_name}")
    print(f"Company: {config.company_name}")
    print(f"Status: {config.status_name}")
```

### get_configurations

Get multiple configurations with optional filtering.

```python
configs = client.get_configurations(
    conditions: str = "",
    pagesize: int = 1000,
    run_as: Optional[str] = None
) -> List[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string |
| `pagesize` | `int` | No | Results per page (default: 1000) |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Configuration` objects

**Example:**

```python
# Get all configurations for a company
configs = cw.get_configurations(
    conditions="company/id=250"
)

# Search by name
configs = cw.get_configurations(
    conditions='name contains "PROD-WEB"'
)

for config in configs:
    print(f"{config.name} - {config.ipAddress}")
```

### get_company_configurations

Get all configurations for a specific company.

```python
configs = client.get_company_configurations(
    company_id: int,
    run_as: Optional[str] = None
) -> List[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Configuration` objects

**Example:**

```python
configs = cw.get_company_configurations(company_id=250)
print(f"Found {len(configs)} configurations")
```

### get_ticket_configurations

Get all configurations attached to a ticket.

```python
configs = client.get_ticket_configurations(
    ticket_id: int,
    run_as: Optional[str] = None
) -> List[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Configuration` objects

**Example:**

```python
configs = cw.get_ticket_configurations(ticket_id=12345)
for config in configs:
    print(f"Attached: {config.name}")
```

### attach_configuration

Attach a configuration to a ticket.

```python
config = client.attach_configuration(
    ticket_id: int,
    config_id: int,
    run_as: Optional[str] = None
) -> Configuration
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `config_id` | `int` | Yes | Configuration ID to attach |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Attached `Configuration` object

**Example:**

```python
config = cw.attach_configuration(
    ticket_id=12345,
    config_id=67890
)
print(f"Attached {config.name} to ticket")
```

### detach_configuration

Detach a configuration from a ticket.

```python
success = client.detach_configuration(
    ticket_id: int,
    config_id: int,
    run_as: Optional[str] = None
) -> bool
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `config_id` | `int` | Yes | Configuration ID to detach |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `True` if successful, `False` if not found

**Example:**

```python
success = cw.detach_configuration(
    ticket_id=12345,
    config_id=67890
)
if success:
    print("Configuration detached")
```

### create_configuration

Create a new configuration item in ConnectWise.

```python
config = client.create_configuration(
    config: Configuration,
    run_as: Optional[str] = None
) -> Configuration
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config` | `Configuration` | Yes | Configuration object with fields populated. The `id` field is ignored (CW assigns it). |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `Configuration` object with CW-assigned ID

**Example:**

```python
config = Configuration(
    id=0,
    name="SRV-PROD-01",
    company={"id": 250},
    type={"id": 158},
    status={"id": 2},
    location={"id": 11},
    site={"id": 1298},
    ipAddress="10.10.1.50",
    osType="Windows Server 2022",
    serialNumber="DELL-ABC123",
)

created = cw.create_configuration(config)
print(f"Created config #{created.id}: {created.name}")
```

### update_configuration

Update an existing configuration item using PATCH. Builds JSON-Patch operations from non-None fields on the config object.

```python
config = client.update_configuration(
    config_id: int,
    config: Configuration,
    run_as: Optional[str] = None
) -> Configuration
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_id` | `int` | Yes | ID of the configuration to update |
| `config` | `Configuration` | Yes | Configuration object with fields to update. Only non-None optional fields generate patch operations. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated `Configuration` object

**Example:**

```python
patch = Configuration(
    id=0,
    name="SRV-PROD-01 (Updated)",
    company={"id": 250},
    type={"id": 158},
    status={"id": 2},
    ipAddress="10.10.1.55",
    ram="262144",
)

updated = cw.update_configuration(config_id=39661, config=patch)
print(f"Updated IP: {updated.ipAddress}")
```

### delete_configuration

Delete a configuration item.

```python
success = client.delete_configuration(
    config_id: int,
    run_as: Optional[str] = None
) -> bool
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_id` | `int` | Yes | Configuration ID to delete |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `True` if deleted, `False` if not found

**Example:**

```python
success = cw.delete_configuration(config_id=39661)
if success:
    print("Configuration deleted")
```

### get_configuration_count

Return the total number of configurations matching the given conditions without fetching any configuration data.

```python
count = client.get_configuration_count(
    conditions: str = "",
    run_as: Optional[str] = None
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

**Example:**

```python
total = cw.get_configuration_count()
company_total = cw.get_configuration_count(conditions="company/id=250")
print(f"{company_total} configs for company 250 (out of {total} total)")
```

---

### get_configuration_type_questions

Get the custom question definitions for a configuration type. Useful for resolving question names to IDs.

```python
questions = client.get_configuration_type_questions(
    type_id: int,
    run_as: Optional[str] = None
) -> List[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type_id` | `int` | Yes | Configuration type ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of question definition dicts, each containing `id`, `question` (label), `fieldType`, etc.

> **Note:** The type questions endpoint returns `id` as the question identifier key, not `questionId`. The `questionId` key only appears on question entries within a configuration item's own `questions` list. The `set_question_by_name` helper handles both formats.

**Example:**

```python
questions = cw.get_configuration_type_questions(type_id=158)
for q in questions:
    qid = q.get("questionId") or q.get("id")
    print(f"  [{qid}] {q['question']} ({q['fieldType']})")
# Output:
#   [1214] NTLocalAdmin (Password)
#   [1215] Engineer Notes (TextArea)
#   [1216] Installed Roles (TextArea)
```

---

## Notes

See [add_ticket_note](#add_ticket_note) and [get_ticket_notes](#get_ticket_notes) in the Tickets section.

---

## Companies

### get_companies

Retrieve companies with optional filtering, ordering, and result cap.

```python
companies = client.get_companies(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Company]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause (e.g., `"id desc"`) |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Company` objects

**Example:**

```python
# Get all active companies
companies = cw.get_companies(conditions="deletedFlag=false")

# Get the 3 most recently added companies
recent = cw.get_companies(orderby="id desc", limit=3)

for c in companies:
    print(f"{c}  status={c.status_name}  territory={c.territory_name}")
```

---

### get_company

Get a specific company by ID.

```python
company = client.get_company(company_id: int, run_as: Optional[str] = None) -> Optional[Company]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Company` object or `None` if not found

**Example:**

```python
company = cw.get_company(company_id=250)
if company:
    print(f"{company.name} — {company.status_name}")
```

---

### get_company_count

Return the total number of companies matching the given conditions without fetching any company data.

```python
count = client.get_company_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

**Example:**

```python
total = cw.get_company_count()
deleted = cw.get_company_count(conditions="deletedFlag=true")
print(f"{total} companies ({deleted} deleted)")
```

---

### get_company_statuses

Get all company statuses.

```python
statuses = client.get_company_statuses(run_as: Optional[str] = None) -> List[CompanyStatus]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `CompanyStatus` objects

**Example:**

```python
for s in cw.get_company_statuses():
    print(f"{s}  default={s.defaultFlag}")
```

---

### get_company_contacts

Get all contacts associated with a specific company.

```python
contacts = client.get_company_contacts(
    company_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[Contact]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |
| `conditions` | `str` | No | Additional conditions string to further filter results |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Contact` objects

**Example:**

```python
contacts = cw.get_company_contacts(company_id=250)
for c in contacts:
    print(f"{c.full_name}  email={c.primary_email}")

# Get only active contacts
active = cw.get_company_contacts(company_id=250, conditions="inactiveFlag=false")
```

---

## Boards

### get_boards

Get all service boards.

```python
boards = client.get_boards(active_only: bool = True, run_as: Optional[str] = None) -> List[Board]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `active_only` | `bool` | No | Only return active (non-inactive) boards (default: `True`) |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Board` objects

**Example:**

```python
boards = cw.get_boards()
for b in boards:
    print(f"{b}")
```

---

### get_board_count

Return the total number of service boards without fetching board data.

```python
count = client.get_board_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

**Example:**

```python
active = cw.get_board_count(conditions="inactive=false")
total = cw.get_board_count()
print(f"{active} active boards out of {total}")
```

---

### get_board_statuses

Get all statuses for a specific board.

```python
statuses = client.get_board_statuses(board_id: int, run_as: Optional[str] = None) -> List[BoardStatus]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `BoardStatus` objects

**Example:**

```python
for s in cw.get_board_statuses(board_id=1):
    print(f"{s}  closed={s.closedStatus}  default={s.defaultFlag}")
```

---

### get_board_types

Get all types for a specific board.

```python
types = client.get_board_types(board_id: int, run_as: Optional[str] = None) -> List[BoardType]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `BoardType` objects

**Example:**

```python
for t in cw.get_board_types(board_id=1):
    print(f"{t}")
```

---

### get_board_subtypes

Get all subtypes for a specific board.

```python
subtypes = client.get_board_subtypes(board_id: int, run_as: Optional[str] = None) -> List[BoardSubtype]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `BoardSubtype` objects

---

### get_board_items

Get all items for a specific board.

```python
items = client.get_board_items(board_id: int, run_as: Optional[str] = None) -> List[BoardItem]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `BoardItem` objects

---

## Lookups

General service reference data (priorities, sources).

### get_priorities

Get all ticket priorities.

```python
priorities = client.get_priorities(run_as: Optional[str] = None) -> List[Priority]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Priority` objects

**Example:**

```python
for p in cw.get_priorities():
    print(f"{p}  sortOrder={p.sortOrder}  default={p.defaultFlag}")
```

---

### get_sources

Get all ticket sources.

```python
sources = client.get_sources(run_as: Optional[str] = None) -> List[Source]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Source` objects

**Example:**

```python
for s in cw.get_sources():
    print(f"{s}  default={s.defaultFlag}")
```

---

## Agreements

Finance agreement read methods. Write operations (create/update/delete agreement) are intentionally not implemented due to financial implications.

### get_agreements

Get finance agreements with optional filtering.

```python
agreements = client.get_agreements(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Agreement]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Agreement` objects

**Example:**

```python
agreements = cw.get_agreements(conditions="cancelledFlag=false")
for a in agreements:
    print(f"{a.name}  company={a.company_name}  active={a.is_active}")
```

### get_agreement

Get a specific agreement by ID.

```python
agreement = client.get_agreement(agreement_id: int, run_as: Optional[str] = None) -> Optional[Agreement]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agreement_id` | `int` | Yes | Agreement ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Agreement` object or `None` if not found

**Example:**

```python
agreement = cw.get_agreement(agreement_id=1234)
if agreement:
    print(f"{agreement.name}  type={agreement.type_name}  active={agreement.is_active}")
    print(f"Start: {agreement.start_datetime}  End: {agreement.end_datetime}")
```

### get_agreement_count

Return the total number of agreements matching the given conditions without fetching any agreement data.

```python
count = client.get_agreement_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

**Example:**

```python
active = cw.get_agreement_count(conditions="cancelledFlag=false")
print(f"{active} active agreements")
```

### get_company_agreements

Get all active (non-cancelled) agreements for a company.

```python
agreements = client.get_company_agreements(company_id: int, run_as: Optional[str] = None) -> List[Agreement]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Agreement` objects (pre-filtered: `cancelledFlag=false`)

**Example:**

```python
agreements = cw.get_company_agreements(company_id=250)
for a in agreements:
    print(f"{a.name}  ({a.type_name})")
```

### get_agreement_additions

Get all additions on a specific agreement.

```python
additions = client.get_agreement_additions(
    agreement_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[AgreementAddition]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agreement_id` | `int` | Yes | Agreement ID |
| `conditions` | `str` | No | Optional conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `AgreementAddition` objects

**Example:**

```python
additions = cw.get_agreement_additions(agreement_id=1234)
for add in additions:
    print(f"{add.product_identifier}  qty={add.quantity}  cancelled={add.is_cancelled}")
```

### get_agreement_addition

Get a specific addition on an agreement.

```python
addition = client.get_agreement_addition(
    agreement_id: int,
    addition_id: int,
    run_as: Optional[str] = None
) -> Optional[AgreementAddition]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agreement_id` | `int` | Yes | Agreement ID |
| `addition_id` | `int` | Yes | Addition ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `AgreementAddition` object or `None` if not found

### create_agreement_addition

Create a new addition on an agreement.

```python
addition = client.create_agreement_addition(
    agreement_id: int,
    product_id: int,
    quantity: float,
    unit_price: float = None,
    bill_customer: str = "Billable",
    effective_date: str = None,
    description: str = None,
    taxable: bool = False,
    uom: str = None,
    run_as: Optional[str] = None
) -> AgreementAddition
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agreement_id` | `int` | Yes | Agreement ID to add the addition to |
| `product_id` | `int` | Yes | Product catalog ID |
| `quantity` | `float` | Yes | Quantity of the product |
| `unit_price` | `float` | No | Optional unit price override |
| `bill_customer` | `str` | No | Billing option: `"Billable"`, `"DoNotBill"`, or `"NoCharge"` (default: `"Billable"`) |
| `effective_date` | `str` | No | Effective date (ISO format string) |
| `description` | `str` | No | Description override |
| `taxable` | `bool` | No | Whether taxable (default: `False`) |
| `uom` | `str` | No | Unit of measure (e.g. `"Each"`, `"Monthly"`, `"Yearly"`) |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `AgreementAddition` object

**Example:**

```python
addition = cw.create_agreement_addition(
    agreement_id=1234,
    product_id=567,
    quantity=5,
    bill_customer="Billable",
    effective_date="2026-05-01T00:00:00Z"
)
print(f"Created addition #{addition.id}  product={addition.product_identifier}")
```

---

## Time Entries

### get_time_entries

Get time entries with optional filtering.

```python
entries = client.get_time_entries(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[TimeEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `TimeEntry` objects

**Example:**

```python
# Get recent billable entries
entries = cw.get_time_entries(
    conditions='billableOption="Billable"',
    orderby="id desc",
    limit=20
)
for e in entries:
    print(f"{e.member_name}: {e.actualHours}h on {e.chargeToType} #{e.chargeToId}")
```

### get_time_entry

Get a specific time entry by ID.

```python
entry = client.get_time_entry(entry_id: int, run_as: Optional[str] = None) -> Optional[TimeEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | `int` | Yes | Time entry ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `TimeEntry` object or `None` if not found

### get_time_entry_count

Return the total number of time entries matching the given conditions without fetching any data.

```python
count = client.get_time_entry_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

### get_member_time_entries

Get all time entries for a specific member.

```python
entries = client.get_member_time_entries(
    member_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[TimeEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member_id` | `int` | Yes | Member ID to filter by |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `TimeEntry` objects

**Example:**

```python
entries = cw.get_member_time_entries(member_id=42)
total = sum(e.actualHours or 0 for e in entries)
print(f"Member 42 has logged {total:.2f} hours total")
```

### get_ticket_time_entries

See [get_ticket_time_entries](#get_ticket_time_entries) in the Tickets section.

### create_time_entry

Create a new time entry.

```python
entry = client.create_time_entry(
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
) -> TimeEntry
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `charge_to_id` | `int` | Yes | ID of the ticket or project this time is charged to |
| `charge_to_type` | `str` | Yes | `"ServiceTicket"`, `"ProjectTicket"`, `"ChargeCode"`, or `"Activity"` |
| `member_id` | `int` | Yes | ID of the member logging the time |
| `actual_hours` | `float` | Yes | Number of hours to log |
| `notes` | `str` | No | Notes for the time entry |
| `billable` | `str` | No | `"Billable"`, `"DoNotBill"`, `"NoCharge"`, or `"NoDefault"` (default: `"Billable"`) |
| `time_start` | `str` | No | Start time (ISO format string) |
| `time_end` | `str` | No | End time (ISO format string) |
| `work_type_id` | `int` | No | Work type ID |
| `work_role_id` | `int` | No | Work role ID |
| `company_id` | `int` | No | Company ID (inferred from ticket if not provided) |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `TimeEntry` object

**Example:**

```python
entry = cw.create_time_entry(
    charge_to_id=12345,
    charge_to_type="ServiceTicket",
    member_id=42,
    actual_hours=1.5,
    notes="Investigated server connectivity issue",
    billable="Billable"
)
print(f"Created time entry #{entry.id}")
```

---

## Members

Read-only. Write operations (create/update/delete members) are not implemented.

### get_members

Get system members (internal staff) with optional filtering.

```python
members = client.get_members(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Member]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Member` objects

**Example:**

```python
members = cw.get_members(conditions="inactiveFlag=false")
for m in members:
    print(f"{m.full_name}  ({m.identifier})  dept={m.department_name}")
```

### get_member

Get a specific member by ID.

```python
member = client.get_member(member_id: int, run_as: Optional[str] = None) -> Optional[Member]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member_id` | `int` | Yes | Member ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Member` object or `None` if not found

**Example:**

```python
# Get the full member object from a ticket's owner field
member = cw.get_member(ticket.owner_id)
if member:
    print(f"Owner: {member.full_name}  active={member.is_active}")
```

### get_member_by_identifier

Look up a member by their login username.

```python
member = client.get_member_by_identifier(identifier: str, run_as: Optional[str] = None) -> Optional[Member]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `identifier` | `str` | Yes | The member's login username |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Member` object or `None` if not found

**Example:**

```python
member = cw.get_member_by_identifier("jsmith")
if member:
    print(f"Found: {member.full_name} (id={member.id})")
```

### get_member_count

Return the total number of members matching the given conditions.

```python
count = client.get_member_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

---

## Contacts

### get_contacts

Get contacts with optional filtering.

```python
contacts = client.get_contacts(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Contact]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Contact` objects

**Example:**

```python
contacts = cw.get_contacts(conditions="inactiveFlag=false", limit=50)
for c in contacts:
    print(f"{c.full_name}  {c.company_name}  email={c.primary_email}")
```

### get_contact

Get a specific contact by ID.

```python
contact = client.get_contact(contact_id: int, run_as: Optional[str] = None) -> Optional[Contact]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contact_id` | `int` | Yes | Contact ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Contact` object or `None` if not found

### get_contact_count

Return the total number of contacts matching the given conditions.

```python
count = client.get_contact_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

### get_ticket_contact

See [get_ticket_contact](#get_ticket_contact) in the Tickets section.

### get_company_contacts

See [get_company_contacts](#get_company_contacts) in the Companies section.

### create_contact

Create a new contact.

```python
contact = client.create_contact(
    first_name: str,
    last_name: str,
    company_id: int,
    email: str = None,
    title: str = None,
    phone: str = None,
    phone_type: str = "Direct",
    run_as: Optional[str] = None
) -> Contact
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `first_name` | `str` | Yes | Contact's first name |
| `last_name` | `str` | Yes | Contact's last name |
| `company_id` | `int` | Yes | Company ID to associate the contact with |
| `email` | `str` | No | Email address (set as default email) |
| `title` | `str` | No | Job title |
| `phone` | `str` | No | Phone number |
| `phone_type` | `str` | No | Phone number type: `"Direct"`, `"Cell"`, or `"Main"` (default: `"Direct"`) |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `Contact` object

**Example:**

```python
contact = cw.create_contact(
    first_name="Jane",
    last_name="Smith",
    company_id=250,
    email="jane.smith@example.com",
    title="IT Manager",
    phone="08 9000 0000"
)
print(f"Created contact #{contact.id}: {contact.full_name}")
```

---

## Invoices

Read-only. Write operations (create/update/delete invoices) are not implemented due to financial implications.

### get_invoices

Get invoices with optional filtering.

```python
invoices = client.get_invoices(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Invoice]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Invoice` objects

**Example:**

```python
invoices = cw.get_invoices(orderby="id desc", limit=10)
for inv in invoices:
    print(f"#{inv.invoiceNumber}  {inv.company_name}  balance={inv.balance}  closed={inv.is_closed}")
```

### get_invoice

Get a specific invoice by ID.

```python
invoice = client.get_invoice(invoice_id: int, run_as: Optional[str] = None) -> Optional[Invoice]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_id` | `int` | Yes | Invoice ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Invoice` object or `None` if not found

### get_invoice_count

Return the total number of invoices matching the given conditions.

```python
count = client.get_invoice_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

### get_company_invoices

Get all invoices for a specific company.

```python
invoices = client.get_company_invoices(
    company_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[Invoice]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Invoice` objects

**Example:**

```python
invoices = cw.get_company_invoices(company_id=250)
outstanding = [inv for inv in invoices if not inv.is_closed and (inv.balance or 0) > 0]
print(f"{len(outstanding)} outstanding invoices")
```

### get_agreement_invoices

Get all invoices associated with a specific agreement.

```python
invoices = client.get_agreement_invoices(agreement_id: int, run_as: Optional[str] = None) -> List[Invoice]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agreement_id` | `int` | Yes | Agreement ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Invoice` objects

**Example:**

```python
invoices = cw.get_agreement_invoices(agreement_id=1234)
print(f"{len(invoices)} invoices on agreement 1234")
```

---

## Projects

### get_projects

Get projects with optional filtering.

```python
projects = client.get_projects(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Project]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Project` objects

**Example:**

```python
projects = cw.get_projects(conditions="closedFlag=false")
for p in projects:
    print(f"{p.name}  company={p.company_name}  status={p.status_name}")
```

### get_project

Get a specific project by ID.

```python
project = client.get_project(project_id: int, run_as: Optional[str] = None) -> Optional[Project]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `int` | Yes | Project ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Project` object or `None` if not found

### get_project_count

Return the total number of projects matching the given conditions.

```python
count = client.get_project_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

### get_company_projects

Get all projects for a specific company.

```python
projects = client.get_company_projects(
    company_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[Project]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Project` objects

**Example:**

```python
projects = cw.get_company_projects(company_id=250)
open_projects = [p for p in projects if not p.is_closed]
print(f"{len(open_projects)} open projects for company 250")
```

### get_project_phases

Get all phases for a specific project.

```python
phases = client.get_project_phases(project_id: int, run_as: Optional[str] = None) -> List[ProjectPhase]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `int` | Yes | Project ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `ProjectPhase` objects

**Example:**

```python
phases = cw.get_project_phases(project_id=789)
for phase in phases:
    print(f"{phase.description}  closed={phase.is_closed}")
```

### get_project_phase

Get a specific phase of a project.

```python
phase = client.get_project_phase(
    project_id: int,
    phase_id: int,
    run_as: Optional[str] = None
) -> Optional[ProjectPhase]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `int` | Yes | Project ID |
| `phase_id` | `int` | Yes | Phase ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `ProjectPhase` object or `None` if not found

### get_project_tickets

Get all tickets associated with a project.

```python
tickets = client.get_project_tickets(
    project_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `int` | Yes | Project ID |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Ticket` objects (same model as service tickets, `chargeToType="ProjectTicket"`)

**Example:**

```python
tickets = cw.get_project_tickets(project_id=789)
open_tickets = [t for t in tickets if not t.is_closed]
print(f"{len(open_tickets)} open tickets on this project")
```

### get_project_time_entries

Get all time entries charged to a project.

```python
entries = client.get_project_time_entries(
    project_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[TimeEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `int` | Yes | Project ID |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `TimeEntry` objects

**Notes:** Internally filters on `chargeToId={project_id} AND chargeToType="ProjectTicket"`.

**Example:**

```python
entries = cw.get_project_time_entries(project_id=789)
total_hours = sum(e.actualHours or 0 for e in entries)
print(f"Project 789: {total_hours:.2f} hours logged")
```

### create_project

Create a new project.

```python
project = client.create_project(
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
) -> Project
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Project name |
| `company_id` | `int` | Yes | Company ID to associate with the project |
| `status_id` | `int` | Yes | Project status ID |
| `board_id` | `int` | No | Board ID |
| `manager_id` | `int` | No | Manager member ID |
| `estimated_start` | `str` | No | Estimated start date (ISO format string) |
| `estimated_end` | `str` | No | Estimated end date (ISO format string) |
| `description` | `str` | No | Project description |
| `billing_method` | `str` | No | `"ActualRates"`, `"FixedFee"`, `"NotToExceed"`, or `"OverrideRate"` |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `Project` object

**Example:**

```python
project = cw.create_project(
    name="Office 365 Migration",
    company_id=250,
    status_id=1,
    manager_id=42,
    estimated_start="2026-05-01T00:00:00Z",
    estimated_end="2026-07-31T00:00:00Z"
)
print(f"Created project #{project.id}: {project.name}")
```

### create_project_phase

Create a new phase on an existing project.

```python
phase = client.create_project_phase(
    project_id: int,
    description: str,
    start_date: str = None,
    end_date: str = None,
    estimated_hours: float = None,
    board_id: int = None,
    run_as: Optional[str] = None
) -> ProjectPhase
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | `int` | Yes | Project ID to add the phase to |
| `description` | `str` | Yes | Phase description/name |
| `start_date` | `str` | No | Phase start date (ISO format string) |
| `end_date` | `str` | No | Phase end date (ISO format string) |
| `estimated_hours` | `float` | No | Estimated hours for this phase |
| `board_id` | `int` | No | Board ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `ProjectPhase` object

**Example:**

```python
phase = cw.create_project_phase(
    project_id=789,
    description="Phase 1: Discovery",
    start_date="2026-05-01T00:00:00Z",
    end_date="2026-05-15T00:00:00Z",
    estimated_hours=20.0
)
print(f"Created phase #{phase.id}: {phase.description}")
```

---

## Opportunities

Read-only. Write operations (create/update/delete opportunities) are not implemented due to sales pipeline implications.

### get_opportunities

Get opportunities with optional filtering.

```python
opportunities = client.get_opportunities(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Opportunity]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Opportunity` objects

**Example:**

```python
opps = cw.get_opportunities(orderby="id desc", limit=10)
for o in opps:
    print(f"{o.name}  company={o.company_name}  stage={o.stage_name}  margin={o.margin}")
```

### get_opportunity

Get a specific opportunity by ID.

```python
opportunity = client.get_opportunity(opportunity_id: int, run_as: Optional[str] = None) -> Optional[Opportunity]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `opportunity_id` | `int` | Yes | Opportunity ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `Opportunity` object or `None` if not found

### get_opportunity_count

Return the total number of opportunities matching the given conditions.

```python
count = client.get_opportunity_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

### get_company_opportunities

Get all opportunities for a specific company.

```python
opportunities = client.get_company_opportunities(
    company_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[Opportunity]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Opportunity` objects

**Example:**

```python
opps = cw.get_company_opportunities(company_id=250)
print(f"Company 250 has {len(opps)} opportunities")
```

### get_open_opportunities

Get all open (not yet closed) opportunities.

```python
opportunities = client.get_open_opportunities(
    conditions: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[Opportunity]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | Additional conditions string to narrow results |
| `limit` | `int` | No | Cap the number of results |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `Opportunity` objects (pre-filtered: `closedDate=null`)

**Notes:** An opportunity is considered open when `closedDate` is null on the record. The `closedDate` field is set regardless of whether the opportunity was won or lost.

**Example:**

```python
open_opps = cw.get_open_opportunities()
print(f"{len(open_opps)} open opportunities")

# Narrow to a specific company
company_opps = cw.get_open_opportunities(conditions="company/id=250")
total_pipeline = sum(o.estimatedRevenue or 0 for o in company_opps)
print(f"Pipeline: ${total_pipeline:,.2f}")
```

---

## Schedule Entries

### get_schedule_entries

Get schedule entries with optional filtering.

```python
entries = client.get_schedule_entries(
    conditions: str = "",
    orderby: str = "",
    limit: int = None,
    run_as: Optional[str] = None
) -> List[ScheduleEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `ScheduleEntry` objects

**Example:**

```python
entries = cw.get_schedule_entries(limit=20)
for e in entries:
    print(f"{e.member_name}  {e.date_start_datetime}  done={e.is_done}")
```

### get_schedule_entry

Get a specific schedule entry by ID.

```python
entry = client.get_schedule_entry(entry_id: int, run_as: Optional[str] = None) -> Optional[ScheduleEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entry_id` | `int` | Yes | Schedule entry ID to retrieve |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `ScheduleEntry` object or `None` if not found

### get_schedule_entry_count

Return the total number of schedule entries matching the given conditions.

```python
count = client.get_schedule_entry_count(conditions: str = "", run_as: Optional[str] = None) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found

### get_member_schedule

Get all schedule entries for a specific member.

```python
entries = client.get_member_schedule(
    member_id: int,
    conditions: str = "",
    run_as: Optional[str] = None
) -> List[ScheduleEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `member_id` | `int` | Yes | Member ID to filter by |
| `conditions` | `str` | No | Additional conditions string |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `ScheduleEntry` objects

**Example:**

```python
entries = cw.get_member_schedule(member_id=42)
upcoming = [e for e in entries if not e.is_done]
print(f"Member 42 has {len(upcoming)} upcoming scheduled entries")
```

### get_ticket_schedule

Get all schedule entries for a specific service ticket. Use this to find which members are assigned/dispatched to a ticket.

```python
entries = client.get_ticket_schedule(ticket_id: int, run_as: Optional[str] = None) -> List[ScheduleEntry]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** List of `ScheduleEntry` objects (pre-filtered to service-type schedule entries for the ticket)

**Notes:** This is the correct way to find who is dispatched to a ticket. The `ticket.owner` field only stores the primary owner — schedule entries capture all resource assignments.

**Example:**

```python
schedule = cw.get_ticket_schedule(ticket_id=12345)
for entry in schedule:
    print(f"  {entry.member_name}  {entry.date_start_datetime} → {entry.date_end_datetime}")
```

### create_schedule_entry

Create a new schedule entry.

```python
entry = client.create_schedule_entry(
    object_id: int,
    type_identifier: str,
    member_id: int,
    date_start: str,
    date_end: str,
    hours: float = None,
    name: str = None,
    run_as: Optional[str] = None
) -> ScheduleEntry
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_id` | `int` | Yes | ID of the object being scheduled (ticket, project, activity) |
| `type_identifier` | `str` | Yes | Schedule type: `"S"` (Service), `"P"` (Project), `"A"` (Activity) |
| `member_id` | `int` | Yes | ID of the member being scheduled |
| `date_start` | `str` | Yes | Start datetime (ISO format string) |
| `date_end` | `str` | Yes | End datetime (ISO format string) |
| `hours` | `float` | No | Hours for the entry |
| `name` | `str` | No | Name/description for the entry |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created `ScheduleEntry` object

**Example:**

```python
entry = cw.create_schedule_entry(
    object_id=12345,
    type_identifier="S",
    member_id=42,
    date_start="2026-04-15T09:00:00Z",
    date_end="2026-04-15T11:00:00Z",
    hours=2.0
)
print(f"Scheduled {entry.member_name} on ticket #{entry.objectId}")
```

---

## Base HTTP Methods

These low-level methods provide direct access to the ConnectWise API for custom operations.

### get

Perform a single GET request.

```python
result = client.get(
    endpoint: str,
    conditions: str = "",
    childconditions: str = "",
    fields: str = "",
    pagesize: int = None,
    page: int = None,
    orderby: str = "",
    run_as: Optional[str] = None
) -> Optional[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint (e.g., "service/tickets") |
| `conditions` | `str` | No | Filter conditions |
| `childconditions` | `str` | No | Child object conditions |
| `fields` | `str` | No | Specific fields to return |
| `pagesize` | `int` | No | Results per page |
| `page` | `int` | No | Page number |
| `orderby` | `str` | No | Sort order |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Dict or `None` if not found

**Example:**

```python
# Get single ticket with specific fields
result = cw.get(
    "service/tickets/12345",
    fields="id,summary,status"
)

# Get tickets with conditions
result = cw.get(
    "service/tickets",
    conditions="closedFlag=false",
    pagesize=100
)
```

### get_all

Perform paginated GET requests to retrieve all records.

```python
results = client.get_all(
    endpoint: str,
    conditions: str = "",
    childconditions: str = "",
    fields: str = "",
    pagesize: int = None,
    orderby: str = "",
    run_as: Optional[str] = None
) -> list
```

**Parameters:** Same as `get()` but without `page` parameter, plus `run_as` (see [Impersonation](#impersonation-run_as))

**Returns:** List of all results (automatically paginated)

**Example:**

```python
# Get all open tickets (handles pagination automatically)
tickets = cw.get_all(
    "service/tickets",
    conditions="closedFlag=false",
    pagesize=1000
)
```

### get_count

Return the total record count for any endpoint without fetching any records. This calls the `{endpoint}/count` API path directly.

```python
count = client.get_count(
    endpoint: str,
    conditions: str = "",
    childconditions: str = "",
    run_as: Optional[str] = None
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint (e.g., `"service/tickets"`) |
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `childconditions` | `str` | No | Child conditions string for filtering |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `int` total count, or `None` if the endpoint was not found (404)

**Example:**

```python
# Count tickets on a board
count = cw.get_count(
    "service/tickets",
    conditions='board/name="Service Desk" AND closedFlag=false'
)
print(f"{count} open tickets")

# Count configurations for a company
config_count = cw.get_count(
    "company/configurations",
    conditions="company/id=250"
)
```

---

### post

Perform a POST request to create a record.

```python
result = client.post(
    endpoint: str,
    data: dict,
    run_as: Optional[str] = None
) -> dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `data` | `dict` | Yes | JSON payload for new record |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Created record as dict

**Example:**

```python
result = cw.post(
    "service/tickets",
    data={
        "summary": "Test Ticket",
        "board": {"id": 1},
        "company": {"id": 250},
        "priority": {"id": 8}
    }
)
```

### patch

Perform a PATCH request to update specific fields.

```python
result = client.patch(
    endpoint: str,
    record_id: int,
    operations: list,
    run_as: Optional[str] = None
) -> Optional[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `record_id` | `int` | Yes | Record ID to update |
| `operations` | `list` | Yes | List of patch operations |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated record or `None` if not found

**Example:**

```python
result = cw.patch(
    "service/tickets",
    record_id=12345,
    operations=[
        {
            "op": "replace",
            "path": "/status",
            "value": {"id": 456}
        }
    ]
)
```

### put

Perform a PUT request to replace/update a record.

```python
result = client.put(
    endpoint: str,
    record_id: int,
    data: dict,
    run_as: Optional[str] = None
) -> Optional[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `record_id` | `int` | Yes | Record ID to update |
| `data` | `dict` | Yes | Complete JSON payload |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** Updated record or `None` if not found

**Example:**

```python
result = cw.put(
    "service/tickets",
    record_id=12345,
    data={...}  # Complete ticket object
)
```

### delete

Perform a DELETE request to remove a record.

```python
success = client.delete(
    endpoint: str,
    record_id: int,
    run_as: Optional[str] = None
) -> bool
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `record_id` | `int` | Yes | Record ID to delete |
| `run_as` | `str` | No | Optional precomputed auth token (from `compute_auth()`) to make this call as another member — see [Impersonation](#impersonation-run_as) |

**Returns:** `True` if successful, `False` if not found

**Example:**

```python
success = cw.delete(
    "service/tickets/12345/configurations",
    record_id=67890
)
```

---

## Exceptions

### Exception Hierarchy

```
ConnectWiseError (base)
├── ConnectWiseAPIError
│   ├── ConnectWiseAuthenticationError (401)
│   ├── ConnectWiseNotFoundError (404)
│   ├── ConnectWiseBadRequestError (400)
│   ├── ConnectWiseRateLimitError (429)
│   └── ConnectWiseServerError (5xx)
└── ConnectWiseConfigurationError
```

### ConnectWiseAPIError

Base exception for API errors.

**Attributes:**
- `status_code: int` - HTTP status code
- `response_data: dict` - Raw response data

**Example:**

```python
try:
    ticket = cw.create_ticket(...)
except ConnectWiseAPIError as e:
    print(f"Error [{e.status_code}]: {e}")
    print(f"Details: {e.response_data}")
```

### ConnectWiseRateLimitError

Raised when API rate limit is exceeded (429).

**Additional Attributes:**
- `retry_after: int` - Seconds to wait before retry

**Example:**

```python
import time

try:
    tickets = cw.get_tickets(...)
except ConnectWiseRateLimitError as e:
    if e.retry_after:
        print(f"Rate limited. Waiting {e.retry_after} seconds...")
        time.sleep(e.retry_after)
        tickets = cw.get_tickets(...)
```

### ConnectWiseNotFoundError

Raised for 404 errors (except for high-level get methods which return None).

### ConnectWiseAuthenticationError

Raised for authentication failures (401).

### ConnectWiseBadRequestError

Raised for bad requests (400).

### ConnectWiseServerError

Raised for server errors (5xx).

### ConnectWiseConfigurationError

Raised when client is misconfigured (missing required parameters).

---

## Models

### Ticket

Dataclass representing a ConnectWise ticket.

**Key Attributes:**
- `id: int` - Ticket ID
- `summary: str` - Ticket summary
- `board: dict` - Board information
- `company: dict` - Company information
- `priority: dict` - Priority information
- `status: dict` - Status information
- `closedFlag: bool` - Whether ticket is closed
- `closedDate: Optional[str]` - Close date (ISO string)
- `lastUpdated: Optional[str]` - Last updated timestamp from `_info` (ISO string)
- `updatedBy: Optional[str]` - Username of last update from `_info`
- `dateEntered: Optional[str]` - Creation timestamp from `_info` (ISO string)

**Properties:**
- `board_name: str` - Board name
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `priority_name: str` - Priority name
- `status_name: str` - Status name
- `type_name: Optional[str]` - Type name
- `source_name: Optional[str]` - Source name
- `owner_name: Optional[str]` - Owner name
- `owner_id: Optional[int]` - Owner member ID (use with `get_member()` to hydrate)
- `owner_identifier: Optional[str]` - Owner login username
- `contact_name: Optional[str]` - Contact name
- `is_closed: bool` - Whether ticket is closed
- `closed_datetime: Optional[datetime]` - Parsed close datetime
- `required_datetime: Optional[datetime]` - Parsed required datetime
- `last_updated_datetime: Optional[datetime]` - Parsed last updated datetime
- `date_entered_datetime: Optional[datetime]` - Parsed creation datetime

**Example:**

```python
ticket = cw.get_ticket(ticket_id=12345)
print(f"#{ticket.id}: {ticket.summary}")
print(f"Company: {ticket.company_name}")
print(f"Status: {ticket.status_name}")
if ticket.is_closed:
    print(f"Closed: {ticket.closed_datetime}")
```

### Configuration

Dataclass representing a ConnectWise configuration (device/asset).

**Required Attributes:**
- `id: int` - Configuration ID
- `name: str` - Configuration name
- `company: dict` - Company information (e.g. `{"id": 250}`)
- `type: dict` - Type information (e.g. `{"id": 158}`)
- `status: dict` - Status information (e.g. `{"id": 2}`)

**Optional Attributes:**
- `location: Optional[dict]` - Location (e.g. `{"id": 11, "name": "Kewdale"}`)
- `site: Optional[dict]` - Site (e.g. `{"id": 1298, "name": "Head Office"}`)
- `contact: Optional[dict]` - Contact (e.g. `{"id": 6191}`)
- `department: Optional[dict]` - Department (e.g. `{"id": 2, "identifier": "Ops Team"}`)
- `locationId: Optional[int]` - Location ID
- `businessUnitId: Optional[int]` - Business unit ID
- `companyLocationId: Optional[int]` - Company location ID
- `serialNumber: Optional[str]` - Serial number
- `modelNumber: Optional[str]` - Model number
- `ipAddress: Optional[str]` - IP address
- `macAddress: Optional[str]` - MAC address
- `osType: Optional[str]` - Operating system type
- `osInfo: Optional[str]` - OS version info
- `cpuSpeed: Optional[str]` - CPU speed
- `ram: Optional[str]` - RAM amount
- `localHardDrives: Optional[str]` - Drive info
- `questions: Optional[list]` - Custom questions/fields
- `activeFlag: bool` - Whether active (default: `True`)
- `billFlag: bool` - Whether billable (default: `False`)
- `showRemoteFlag: Optional[bool]` - Show remote link
- `showAutomateFlag: Optional[bool]` - Show automate link
- `needsRenewalFlag: Optional[bool]` - Needs renewal

**Properties:**
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `type_name: str` - Type name
- `status_name: str` - Status name
- `vendor_name: Optional[str]` - Vendor name
- `manufacturer_name: Optional[str]` - Manufacturer name
- `is_active: bool` - Whether configuration is active
- `purchase_datetime: Optional[datetime]` - Parsed purchase date
- `installation_datetime: Optional[datetime]` - Parsed installation date
- `warranty_expiration_datetime: Optional[datetime]` - Parsed warranty expiration

**Methods:**

#### `to_dict(exclude_none=True, exclude_id=False)`

Convert Configuration to an API-compatible dict for POST/PATCH.

```python
config = Configuration(id=0, name="SRV-01", company={"id": 250}, type={"id": 158}, status={"id": 2})
data = config.to_dict(exclude_id=True)
# Returns: {"name": "SRV-01", "company": {"id": 250}, "type": {"id": 158}, "status": {"id": 2}, ...}
```

#### `set_question(question_id, answer)`

Set or update a custom question answer by question ID.

```python
config.set_question(1214, "my_password")
```

#### `set_question_by_name(name, answer, question_definitions)`

Set or update a custom question answer by matching its label (case-insensitive). Requires the question definitions list from `get_configuration_type_questions()`. Raises `ValueError` if no matching question is found.

```python
# Fetch question definitions once per type
qdefs = cw.get_configuration_type_questions(type_id=158)

config = Configuration(id=0, name="SRV-01", company={"id": 250}, type={"id": 158}, status={"id": 2})
config.set_question_by_name("NTLocalAdmin", "my_password", qdefs)
config.set_question_by_name("Engineer Notes", "Fresh install", qdefs)
config.set_question_by_name("Installed Roles", "DC, DNS, DHCP", qdefs)

created = cw.create_configuration(config)
```

**Example:**

```python
config = cw.get_configuration(config_id=67890)
print(f"{config.name} - {config.type_name}")
print(f"IP: {config.ipAddress}")
print(f"Serial: {config.serialNumber}")
print(f"Location: {config.location}")
print(f"Active: {config.is_active}")
```

### Company

Dataclass representing a ConnectWise company.

**Key Attributes:**
- `id: int` - Company ID
- `name: str` - Company name
- `identifier: Optional[str]` - Short identifier
- `status: Optional[dict]` - Status dict
- `territory: Optional[dict]` - Territory dict
- `market: Optional[dict]` - Market dict
- `deletedFlag: bool` - Whether deleted

**Properties:**
- `status_name: str` - Status name
- `territory_name: str` - Territory name
- `market_name: str` - Market name

---

### CompanyStatus

Dataclass representing a ConnectWise company status.

**Attributes:**
- `id: int` - Status ID
- `name: str` - Status name
- `defaultFlag: bool` - Whether this is the default status
- `inactiveFlag: bool` - Whether inactive
- `notificationFlag: bool` - Whether notifications are enabled

---

### Board

Dataclass representing a ConnectWise service board.

**Attributes:**
- `id: int` - Board ID
- `name: str` - Board name
- `inactive: bool` - Whether inactive
- `projectFlag: bool` - Whether a project board

---

### BoardStatus

Dataclass representing a status on a service board.

**Attributes:**
- `id: int` - Status ID
- `name: str` - Status name
- `boardId: Optional[int]` - Parent board ID
- `closedStatus: bool` - Whether this status represents a closed ticket
- `defaultFlag: bool` - Whether this is the default status

---

### BoardType

Dataclass representing a type on a service board.

**Attributes:**
- `id: int` - Type ID
- `name: str` - Type name
- `boardId: Optional[int]` - Parent board ID
- `inactive: bool` - Whether inactive

---

### BoardSubtype

Dataclass representing a subtype on a service board.

**Attributes:**
- `id: int` - Subtype ID
- `name: str` - Subtype name
- `boardId: Optional[int]` - Parent board ID
- `inactive: bool` - Whether inactive

---

### BoardItem

Dataclass representing an item on a service board.

**Attributes:**
- `id: int` - Item ID
- `name: str` - Item name
- `boardId: Optional[int]` - Parent board ID
- `inactive: bool` - Whether inactive

---

### Priority

Dataclass representing a ConnectWise ticket priority.

**Attributes:**
- `id: int` - Priority ID
- `name: str` - Priority name
- `sortOrder: Optional[int]` - Sort order
- `defaultFlag: bool` - Whether this is the default priority
- `imageLink: Optional[str]` - URL to priority icon

---

### Source

Dataclass representing a ConnectWise ticket source.

**Attributes:**
- `id: int` - Source ID
- `name: str` - Source name
- `defaultFlag: bool` - Whether this is the default source
- `enteredByFlag: bool` - Whether restricted to entered-by usage

---

### Note

Dataclass representing a ticket note.

**Key Attributes:**
- `id: int` - Note ID
- `ticketId: int` - Associated ticket ID
- `text: str` - Note content
- `detailDescriptionFlag: bool` - Whether detail description
- `internalAnalysisFlag: bool` - Whether internal
- `externalFlag: bool` - Whether external
- `dateCreated: Optional[str]` - Creation date (ISO string)

**Properties:**
- `is_internal: bool` - Whether note is internal
- `is_external: bool` - Whether note is external
- `member_name: Optional[str]` - Member name
- `member_id: Optional[int]` - Member ID
- `contact_name: Optional[str]` - Contact name
- `contact_id: Optional[int]` - Contact ID
- `created_datetime: Optional[datetime]` - Parsed creation datetime

**Example:**

```python
note = cw.add_ticket_note(ticket_id=12345, note_text="...", internal=True)
print(f"Note #{note.id}")
print(f"Internal: {note.is_internal}")
print(f"Created: {note.created_datetime}")
```

---

### Agreement

Dataclass representing a ConnectWise finance agreement.

**Key Attributes:**
- `id: int` - Agreement ID
- `name: str` - Agreement name
- `company: dict` - Company dict
- `type: dict` - Agreement type dict
- `status: Optional[str]` - Status string (e.g. `"Active"`)
- `startDate: Optional[str]` - Start date (ISO string)
- `endDate: Optional[str]` - End date (ISO string)
- `cancelledFlag: bool` - Whether the agreement has been cancelled

**Properties:**
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `type_name: Optional[str]` - Agreement type name
- `is_active: bool` - `True` when `not cancelledFlag and status == "Active"`
- `start_datetime: Optional[datetime]` - Parsed start datetime
- `end_datetime: Optional[datetime]` - Parsed end datetime

---

### AgreementAddition

Dataclass representing an addition line on a finance agreement.

**Key Attributes:**
- `id: int` - Addition ID
- `agreementId: int` - Parent agreement ID
- `product: dict` - Product catalog dict
- `quantity: float` - Quantity
- `unitPrice: Optional[float]` - Unit price
- `billCustomer: str` - Billing option (`"Billable"`, `"DoNotBill"`, `"NoCharge"`)
- `effectiveDate: Optional[str]` - Effective date (ISO string)
- `cancelledDate: Optional[str]` - Cancellation date (ISO string)
- `cancelledFlag: bool` - Whether cancelled
- `taxableFlag: bool` - Whether taxable

**Properties:**
- `product_id: Optional[int]` - Product catalog ID
- `product_identifier: Optional[str]` - Product identifier/SKU
- `product_description: Optional[str]` - Product description
- `is_cancelled: bool` - Whether addition is cancelled
- `effective_datetime: Optional[datetime]` - Parsed effective datetime
- `cancelled_datetime: Optional[datetime]` - Parsed cancellation datetime

---

### TimeEntry

Dataclass representing a ConnectWise time entry.

**Key Attributes:**
- `id: int` - Time entry ID
- `company: dict` - Company dict
- `chargeToId: int` - ID of the ticket or project charged to
- `chargeToType: str` - `"ServiceTicket"`, `"ProjectTicket"`, `"ChargeCode"`, or `"Activity"`
- `member: Optional[dict]` - Member dict
- `actualHours: Optional[float]` - Hours logged
- `billableOption: str` - `"Billable"`, `"DoNotBill"`, `"NoCharge"`, or `"NoDefault"`
- `notes: Optional[str]` - Time entry notes
- `workType: Optional[dict]` - Work type dict
- `workRole: Optional[dict]` - Work role dict
- `agreement: Optional[dict]` - Agreement dict
- `timeStart: Optional[str]` - Start time (ISO string)
- `timeEnd: Optional[str]` - End time (ISO string)
- `dateEntered: Optional[str]` - Entry creation date (ISO string, from `_info`)

**Properties:**
- `member_name: Optional[str]` - Member name
- `member_id: Optional[int]` - Member ID
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `work_type_name: Optional[str]` - Work type name
- `work_role_name: Optional[str]` - Work role name
- `agreement_id: Optional[int]` - Agreement ID
- `agreement_name: Optional[str]` - Agreement name
- `is_billable: bool` - `True` when `billableOption == "Billable"`
- `time_start_datetime: Optional[datetime]` - Parsed start datetime
- `time_end_datetime: Optional[datetime]` - Parsed end datetime
- `date_entered_datetime: Optional[datetime]` - Parsed creation datetime

---

### Member

Dataclass representing a ConnectWise system member (internal staff).

**Key Attributes:**
- `id: int` - Member ID
- `identifier: str` - Login username
- `firstName: str` - First name
- `lastName: str` - Last name
- `inactiveFlag: bool` - Whether inactive
- `department: Optional[dict]` - Department dict
- `location: Optional[dict]` - Location dict

**Properties:**
- `full_name: str` - `"{firstName} {lastName}"`
- `is_active: bool` - `not inactiveFlag`
- `department_name: Optional[str]` - Department name
- `location_name: Optional[str]` - Location name

**Example:**

```python
member = cw.get_member(member_id=42)
print(f"{member.full_name} ({member.identifier})  active={member.is_active}")

# Hydrate owner from a ticket
member = cw.get_member(ticket.owner_id)
```

---

### Contact

Dataclass representing a ConnectWise company contact.

**Key Attributes:**
- `id: int` - Contact ID
- `firstName: str` - First name
- `lastName: str` - Last name (defaults to `""` when absent from API response)
- `company: dict` - Company dict
- `inactiveFlag: bool` - Whether inactive
- `communicationItems: Optional[list]` - List of communication method dicts

**Properties:**
- `full_name: str` - `"{firstName} {lastName}"` (stripped)
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `is_active: bool` - `not inactiveFlag`
- `primary_email: Optional[str]` - Default email from `communicationItems` (type name `"Email"`, `defaultFlag=True`)
- `primary_phone: Optional[str]` - Default phone from `communicationItems` (type name `"Direct"`, `"Cell"`, or `"Main"`, `defaultFlag=True`)

**Example:**

```python
contact = cw.get_ticket_contact(ticket_id=12345)
if contact:
    print(f"{contact.full_name}  {contact.primary_email}  {contact.primary_phone}")
```

---

### Invoice

Dataclass representing a ConnectWise finance invoice.

**Key Attributes:**
- `id: int` - Invoice ID
- `invoiceNumber: str` - Invoice number string
- `type: str` - Invoice type
- `status: dict` - Status dict (contains `isClosed` flag)
- `company: dict` - Company dict
- `date: Optional[str]` - Invoice date (ISO string)
- `dueDate: Optional[str]` - Due date (ISO string)
- `total: Optional[float]` - Invoice total
- `payments: Optional[float]` - Total payments received
- `balance: Optional[float]` - Current balance (returned directly by API)
- `agreement: Optional[dict]` - Associated agreement dict

**Properties:**
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `status_name: Optional[str]` - Status name
- `agreement_id: Optional[int]` - Agreement ID
- `agreement_name: Optional[str]` - Agreement name
- `is_closed: bool` - `status.get("isClosed", False)`
- `invoice_datetime: Optional[datetime]` - Parsed invoice datetime
- `due_datetime: Optional[datetime]` - Parsed due datetime

> **Note:** The API uses `date` (not `invoiceDate`), `total` (not `invoiceTotal`), and `payments` (not `paidAmount`). The `balance` field is returned directly — do not calculate it from `total - payments`.

---

### Project

Dataclass representing a ConnectWise project.

**Key Attributes:**
- `id: int` - Project ID
- `name: str` - Project name
- `company: dict` - Company dict
- `status: dict` - Status dict
- `type: Optional[dict]` - Project type dict
- `board: Optional[dict]` - Board dict
- `manager: Optional[dict]` - Manager (member) dict
- `closedFlag: bool` - Whether closed
- `estimatedStart: Optional[str]` - Estimated start date (ISO string)
- `estimatedEnd: Optional[str]` - Estimated end date (ISO string)
- `actualStart: Optional[str]` - Actual start date (ISO string)
- `actualEnd: Optional[str]` - Actual end date (ISO string)

**Properties:**
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `status_name: Optional[str]` - Status name
- `type_name: Optional[str]` - Type name
- `board_name: Optional[str]` - Board name
- `manager_name: Optional[str]` - Manager name
- `manager_id: Optional[int]` - Manager member ID
- `is_closed: bool` - `closedFlag`
- `estimated_start_datetime: Optional[datetime]` - Parsed estimated start
- `estimated_end_datetime: Optional[datetime]` - Parsed estimated end
- `actual_start_datetime: Optional[datetime]` - Parsed actual start
- `actual_end_datetime: Optional[datetime]` - Parsed actual end

---

### ProjectPhase

Dataclass representing a phase within a ConnectWise project.

**Key Attributes:**
- `id: int` - Phase ID
- `projectId: int` - Parent project ID
- `description: str` - Phase description/name
- `status: Optional[dict]` - Status dict
- `board: Optional[dict]` - Board dict
- `markAsClosedFlag: bool` - Whether marked as closed
- `startDate: Optional[str]` - Start date (ISO string)
- `endDate: Optional[str]` - End date (ISO string)
- `estimatedHours: Optional[float]` - Estimated hours

**Properties:**
- `status_name: Optional[str]` - Status name
- `board_name: Optional[str]` - Board name
- `is_closed: bool` - `markAsClosedFlag`
- `start_datetime: Optional[datetime]` - Parsed start datetime
- `end_datetime: Optional[datetime]` - Parsed end datetime

---

### Opportunity

Dataclass representing a ConnectWise sales opportunity.

**Key Attributes:**
- `id: int` - Opportunity ID
- `name: str` - Opportunity name
- `company: dict` - Company dict
- `status: Optional[dict]` - Status dict
- `stage: Optional[dict]` - Pipeline stage dict
- `type: Optional[dict]` - Opportunity type dict
- `primarySalesRep: Optional[dict]` - Sales rep (member) dict
- `probability: Optional[dict]` - Probability dict (contains `name` as a numeric string)
- `estimatedRevenue: Optional[float]` - Estimated revenue
- `estimatedCost: Optional[float]` - Estimated cost
- `expectedCloseDate: Optional[str]` - Expected close date (ISO string)
- `closedDate: Optional[str]` - Actual close date (ISO string, `null` when open)

**Properties:**
- `company_name: str` - Company name
- `company_id: Optional[int]` - Company ID
- `status_name: Optional[str]` - Status name
- `stage_name: Optional[str]` - Stage name
- `type_name: Optional[str]` - Type name
- `primary_sales_rep_name: Optional[str]` - Sales rep name
- `primary_sales_rep_id: Optional[int]` - Sales rep member ID
- `probability_value: Optional[int]` - Probability percentage (parsed from `probability.name`)
- `is_closed: bool` - `closedDate is not None`
- `margin: float` - `(estimatedRevenue or 0) - (estimatedCost or 0)`
- `forecast_close_datetime: Optional[datetime]` - Parsed expected close datetime
- `expected_close_datetime: Optional[datetime]` - Alias for `forecast_close_datetime`

---

### ScheduleEntry

Dataclass representing a ConnectWise schedule entry.

**Key Attributes:**
- `id: int` - Schedule entry ID
- `objectId: int` - ID of the scheduled object (ticket, project, etc.)
- `member: Optional[dict]` - Assigned member dict
- `status: Optional[dict]` - Status dict
- `type: Optional[dict]` - Schedule type dict
- `doneFlag: bool` - Whether marked as done
- `dateStart: Optional[str]` - Start datetime (ISO string)
- `dateEnd: Optional[str]` - End datetime (ISO string)
- `hours: Optional[float]` - Scheduled hours

**Properties:**
- `member_name: Optional[str]` - Member name
- `member_id: Optional[int]` - Member ID
- `status_name: Optional[str]` - Status name
- `type_name: Optional[str]` - Type name
- `is_done: bool` - `doneFlag`
- `date_start_datetime: Optional[datetime]` - Parsed start datetime
- `date_end_datetime: Optional[datetime]` - Parsed end datetime

**Example:**

```python
schedule = cw.get_ticket_schedule(ticket_id=12345)
for entry in schedule:
    print(f"{entry.member_name}: {entry.date_start_datetime} → {entry.date_end_datetime}  done={entry.is_done}")
```

---

## Utilities

### SecretString

Wrapper for sensitive strings that prevents accidental exposure.

**Methods:**
- `get_secret_value() -> str` - Explicitly retrieve the actual value

**Example:**

```python
from integrations.connectwise import SecretString

password = SecretString("my_secret_password")
print(password)  # Output: **********
print(repr(password))  # Output: SecretString('**********')

# Explicit access when needed
actual = password.get_secret_value()  # "my_secret_password"
```

### parse_cw_datetime

Parse a ConnectWise API datetime string into a `datetime` object.

```python
from connectwise.utils import parse_cw_datetime

dt = parse_cw_datetime(value: Optional[str]) -> Optional[datetime]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | `Optional[str]` | Yes | ISO 8601 datetime string from the API (e.g. `"2025-09-05T06:59:47Z"`) |

**Returns:** A timezone-aware `datetime` object, or `None` if `value` is falsy or unparseable.

**Notes:**
- Handles the trailing `Z` (UTC) used throughout the ConnectWise API.
- All datetime properties on `Ticket`, `Configuration`, `Note`, `Agreement`, `TimeEntry`, `Invoice`, `Project`, `ProjectPhase`, `Opportunity`, `ScheduleEntry`, and `AgreementAddition` delegate to this function — use those properties where possible rather than calling this directly.
- Use this helper when adding new datetime fields to models instead of inlining `fromisoformat` calls.

**Example:**

```python
from connectwise.utils import parse_cw_datetime

dt = parse_cw_datetime("2025-09-05T06:59:47Z")
# datetime(2025, 9, 5, 6, 59, 47, tzinfo=timezone.utc)

parse_cw_datetime(None)   # None
parse_cw_datetime("")     # None
```

---

## ConnectWise Conditions Syntax

ConnectWise uses a specific conditions syntax for filtering:

### Basic Operators

- `=` - Equals
- `!=` - Not equals
- `<` - Less than
- `>` - Greater than
- `<=` - Less than or equal
- `>=` - Greater than or equal

### Logical Operators

- `AND` - Logical AND
- `OR` - Logical OR

### String Operators

- `contains` - Contains substring
- `like` - SQL-like pattern matching

### Examples

```python
# Equals
conditions = "closedFlag=false"

# Multiple conditions
conditions = "closedFlag=false AND company/id=250"

# Contains
conditions = 'summary contains "server"'

# Like pattern
conditions = 'name like "PROD-%"'

# Nested properties
conditions = "company/id=250 AND status/name='Open'"

# Complex conditions
conditions = "(closedFlag=false AND priority/id>=8) OR summary contains 'urgent'"
```

---

## Performance Tips

1. **Use specific conditions** to limit results:
   ```python
   # ❌ Slow - fetches all tickets
   tickets = cw.get_tickets()

   # ✅ Fast - filtered query
   tickets = cw.get_tickets(conditions="company/id=250")
   ```

2. **Use fields parameter** for partial data:
   ```python
   # Only fetch needed fields
   result = cw.get("service/tickets", fields="id,summary,status")
   ```

3. **Use `limit` to cap results, not `pagesize`**:
   ```python
   # ❌ Wrong — pagesize controls internal pagination, not result count
   tickets = cw.get_tickets(pagesize=5)

   # ✅ Correct — limit makes a single request and returns at most 5
   tickets = cw.get_tickets(orderby="id desc", limit=5)
   ```

4. **Order by `id` not `dateEntered` on large datasets**:
   ```python
   # ❌ Slow — dateEntered is in _info and not indexed; will timeout on large envs
   tickets = cw.get_tickets(orderby="dateEntered desc", limit=5)

   # ✅ Fast — id is the primary key and always indexed
   tickets = cw.get_tickets(orderby="id desc", limit=5)
   ```

4. **Handle rate limits**:
   ```python
   try:
       tickets = cw.get_tickets(...)
   except ConnectWiseRateLimitError as e:
       time.sleep(e.retry_after or 60)
       tickets = cw.get_tickets(...)
   ```

---

## Complete Workflow Example

```python
from integrations.connectwise import (
    ConnectWiseClient,
    TicketDefaults,
    ConnectWiseAPIError,
    ConnectWiseRateLimitError
)

# Initialize client
defaults = TicketDefaults(
    company_id=250,
    board_id=1,
    priority_id=8,
    source_id=42
)

cw = ConnectWiseClient(
    base_url="https://connect.example.com",
    client="MyCompany",
    username="api_user",
    password="secret",
    client_id="uuid",
    ticket_defaults=defaults
)

# Find matching configuration
configs = cw.get_configurations(
    conditions='name="PROD-WEB-01" AND company/id=250'
)

if configs:
    config = configs[0]

    # Create ticket
    ticket = cw.create_ticket(
        summary=f"Server {config.name} Offline",
        body=f"Server is unreachable. IP: {config.ipAddress}"
    )
    print(f"Created ticket #{ticket.id}")

    # Attach configuration
    cw.attach_configuration(ticket.id, config.id)

    # Add internal note
    cw.add_ticket_note(
        ticket_id=ticket.id,
        note_text="Investigating connectivity",
        internal=True
    )

    # Later: resolve ticket
    resolved = cw.update_ticket_status(
        ticket_id=ticket.id,
        status_id=456
    )

    if resolved and resolved.is_closed:
        print(f"Ticket resolved at {resolved.closed_datetime}")
```

---

For AI agent-specific guidance, see [agents.md](agents.md).
