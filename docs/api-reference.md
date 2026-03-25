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

## Tickets

### get_ticket

Retrieve a specific ticket by ID.

```python
ticket = client.get_ticket(ticket_id: int) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to retrieve |

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
    limit: int = None
) -> List[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `pagesize` | `int` | No | Results per page when paginating all records (default: 1000). **Do not use this to cap results** — use `limit` instead. |
| `orderby` | `str` | No | Order by clause. **Use `id desc` rather than `dateEntered desc`** on large environments — `dateEntered` is not indexed and will cause a server timeout. |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |

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
    conditions: str = ""
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |

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
    config_ids: List[int] = None
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
    status_id: int
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `status_id` | `int` | Yes | New status ID |

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
    priority_id: int
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `priority_id` | `int` | Yes | New priority ID |

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
    company_id: int
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `company_id` | `int` | Yes | New company ID |

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
    value: any
) -> Optional[Ticket]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID to update |
| `field_path` | `str` | Yes | Field path (e.g., "/summary", "/customField") |
| `value` | `any` | Yes | New value for the field |

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
    child_status_id: int
) -> dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `child_ticket_id` | `int` | Yes | Child ticket ID |
| `parent_ticket_id` | `int` | Yes | Parent ticket ID |
| `child_status_id` | `int` | Yes | Status to set on child ticket |

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
    internal: bool = True
) -> Note
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `note_text` | `str` | Yes | Note content |
| `internal` | `bool` | No | Whether note is internal (default: True) |

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
notes = client.get_ticket_notes(ticket_id: int) -> List[Note]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |

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

---

## Configurations

### get_configuration

Get details of a specific configuration.

```python
config = client.get_configuration(config_id: int) -> Optional[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_id` | `int` | Yes | Configuration ID |

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
    pagesize: int = 1000
) -> List[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string |
| `pagesize` | `int` | No | Results per page (default: 1000) |

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
    company_id: int
) -> List[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID |

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
    ticket_id: int
) -> List[Configuration]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |

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
    config_id: int
) -> Configuration
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `config_id` | `int` | Yes | Configuration ID to attach |

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
    config_id: int
) -> bool
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ticket_id` | `int` | Yes | Ticket ID |
| `config_id` | `int` | Yes | Configuration ID to detach |

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
    config: Configuration
) -> Configuration
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config` | `Configuration` | Yes | Configuration object with fields populated. The `id` field is ignored (CW assigns it). |

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
    config: Configuration
) -> Configuration
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_id` | `int` | Yes | ID of the configuration to update |
| `config` | `Configuration` | Yes | Configuration object with fields to update. Only non-None optional fields generate patch operations. |

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
    config_id: int
) -> bool
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config_id` | `int` | Yes | Configuration ID to delete |

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
    conditions: str = ""
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |

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
    type_id: int
) -> List[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type_id` | `int` | Yes | Configuration type ID |

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
    limit: int = None
) -> List[Company]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `orderby` | `str` | No | Order by clause (e.g., `"id desc"`) |
| `limit` | `int` | No | Cap the number of results. When set, makes a single page request instead of paginating all records. |

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
company = client.get_company(company_id: int) -> Optional[Company]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `int` | Yes | Company ID to retrieve |

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
count = client.get_company_count(conditions: str = "") -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |

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
statuses = client.get_company_statuses() -> List[CompanyStatus]
```

**Returns:** List of `CompanyStatus` objects

**Example:**

```python
for s in cw.get_company_statuses():
    print(f"{s}  default={s.defaultFlag}")
```

---

## Boards

### get_boards

Get all service boards.

```python
boards = client.get_boards(active_only: bool = True) -> List[Board]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `active_only` | `bool` | No | Only return active (non-inactive) boards (default: `True`) |

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
count = client.get_board_count(conditions: str = "") -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `conditions` | `str` | No | ConnectWise conditions string for filtering |

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
statuses = client.get_board_statuses(board_id: int) -> List[BoardStatus]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |

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
types = client.get_board_types(board_id: int) -> List[BoardType]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |

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
subtypes = client.get_board_subtypes(board_id: int) -> List[BoardSubtype]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |

**Returns:** List of `BoardSubtype` objects

---

### get_board_items

Get all items for a specific board.

```python
items = client.get_board_items(board_id: int) -> List[BoardItem]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | `int` | Yes | Board ID |

**Returns:** List of `BoardItem` objects

---

## Lookups

General service reference data (priorities, sources).

### get_priorities

Get all ticket priorities.

```python
priorities = client.get_priorities() -> List[Priority]
```

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
sources = client.get_sources() -> List[Source]
```

**Returns:** List of `Source` objects

**Example:**

```python
for s in cw.get_sources():
    print(f"{s}  default={s.defaultFlag}")
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
    orderby: str = ""
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
    orderby: str = ""
) -> list
```

**Parameters:** Same as `get()` but without `page` parameter

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
    childconditions: str = ""
) -> Optional[int]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint (e.g., `"service/tickets"`) |
| `conditions` | `str` | No | ConnectWise conditions string for filtering |
| `childconditions` | `str` | No | Child conditions string for filtering |

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
    data: dict
) -> dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `data` | `dict` | Yes | JSON payload for new record |

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
    operations: list
) -> Optional[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `record_id` | `int` | Yes | Record ID to update |
| `operations` | `list` | Yes | List of patch operations |

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
    data: dict
) -> Optional[dict]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `record_id` | `int` | Yes | Record ID to update |
| `data` | `dict` | Yes | Complete JSON payload |

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
    record_id: int
) -> bool
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | API endpoint |
| `record_id` | `int` | Yes | Record ID to delete |

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
- All datetime properties on `Ticket`, `Configuration`, and `Note` delegate to this function — use those properties where possible rather than calling this directly.
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
