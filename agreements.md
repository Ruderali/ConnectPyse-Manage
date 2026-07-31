# ConnectPyse-Manage — Full API Expansion Plan

Reference implementation for schemas/endpoints (use for field names and nesting structure, not code style):
https://github.com/HealthITAU/pyconnectwise/tree/main/src/pyconnectwise/endpoints/manage
https://github.com/HealthITAU/pyconnectwise/tree/main/src/pyconnectwise/models/manage

---

## Library conventions (maintain throughout)

- Models are `@dataclass` with `from_dict(cls, data)` classmethod
- Nested API objects (company, status, type, etc.) stored as raw `dict`, exposed via `@property` convenience accessors (`company_name`, `company_id`, etc.)
- Date strings stored as-is, exposed via `@property` returning `Optional[datetime]` using `parse_cw_datetime()`
- Boolean API flags stored as-is (`activeFlag`, `closedFlag`), exposed via `@property` with a clean name (`is_active`, `is_closed`)
- `from_dict` uses `valid_fields` filter to ignore unknown API fields — new fields can be added to the dataclass without breaking existing calls
- `to_dict(exclude_none=True, exclude_id=False)` on models that support write operations
- Methods that live on a parent resource (time entries on a ticket, additions on an agreement) go in the parent's mixin as `get_ticket_time_entries(ticket_id)`, `get_agreement_additions(agreement_id)` etc. — NOT as methods on the model object itself
- Models are imported into `models/__init__.py` and added to `__all__`
- Mixins are imported into `ConnectWiseClient`'s inheritance chain in `client.py`

---

## Phase 1 — Finance: Agreements + Additions

**Why first:** Highest MSP value. Recurring revenue reporting is a core use case.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/FinanceAgreements*
API base: finance/agreements
API sub: finance/agreements/{id}/additions
```

### New file: `models/agreement.py`

```python
@dataclass
class Agreement:
    id: int
    name: str
    company: dict
    type: dict                       # agreementType
    status: Optional[str] = None     # "Active" | "Inactive" | "Cancelled"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    noEndingDateFlag: bool = False
    billAmount: Optional[float] = None
    billCycleId: Optional[int] = None
    billOneTimeFlag: bool = False
    invoiceDescription: Optional[str] = None
    cancelledFlag: bool = False
    reasonCancelled: Optional[str] = None
    contactName: Optional[str] = None
    sla: Optional[dict] = None
    location: Optional[dict] = None
    department: Optional[dict] = None
    opportunity: Optional[dict] = None
    workOrder: Optional[str] = None
    internalNotes: Optional[str] = None
    applicationUnits: Optional[str] = None  # "Amount" | "Hours" | "Incidents"
    applicationLimit: Optional[float] = None
    applicationCycle: Optional[str] = None
    applicationUnlimitedFlag: bool = False
    taxable: Optional[bool] = None
    prorateFlag: bool = False
    invoiceTemplateSetupId: Optional[int] = None
    billToCompany: Optional[dict] = None
    billToSite: Optional[dict] = None
    billToContact: Optional[dict] = None

    # Convenience properties
    # company_name, company_id
    # type_name (from type dict)
    # is_active → not cancelledFlag and status == "Active"
    # start_datetime, end_datetime → parse_cw_datetime()
```

### New file: `models/agreement_addition.py`

```python
@dataclass
class AgreementAddition:
    id: int
    agreementId: int
    product: dict                    # {"id": ..., "identifier": ..., "description": ...}
    quantity: float
    unitPrice: Optional[float] = None
    unitCost: Optional[float] = None
    extPrice: Optional[float] = None   # computed: quantity * unitPrice
    extCost: Optional[float] = None
    taxableFlag: bool = False
    billCustomer: str = "Billable"   # "Billable" | "DoNotBill" | "NoCharge"
    effectiveDate: Optional[str] = None
    cancelledDate: Optional[str] = None
    cancelledFlag: bool = False
    invoiceDescription: Optional[str] = None
    purchaseItemFlag: bool = False
    specialOrderFlag: bool = False
    description: Optional[str] = None
    uom: Optional[str] = None        # unit of measure: "Each" | "Monthly" | "Yearly" etc.
    sequenceNumber: Optional[float] = None
    lessIncluded: Optional[float] = None
    adjustedQuantity: Optional[float] = None
    adjustedUnitPrice: Optional[float] = None
    adjustedExtPrice: Optional[float] = None
    serialNumber: Optional[str] = None

    # Convenience properties
    # product_id, product_identifier, product_description
    # is_cancelled
    # effective_datetime, cancelled_datetime
```

### New file: `mixins/agreements_mixin.py`

```python
class AgreementsMixin:
    def get_agreements(self, conditions="", orderby="", limit=None) -> List[Agreement]
        # GET finance/agreements

    def get_agreement(self, agreement_id) -> Optional[Agreement]
        # GET finance/agreements/{id}

    def get_agreement_count(self, conditions="") -> Optional[int]
        # GET finance/agreements/count

    def get_company_agreements(self, company_id) -> List[Agreement]
        # get_agreements(conditions=f"company/id={company_id} AND cancelledFlag=false")

    def get_agreement_additions(self, agreement_id, conditions="") -> List[AgreementAddition]
        # GET finance/agreements/{id}/additions

    def get_agreement_addition(self, agreement_id, addition_id) -> Optional[AgreementAddition]
        # GET finance/agreements/{id}/additions/{addition_id}

    def create_agreement_addition(self, agreement_id, product_id, quantity, unit_price=None, ...) -> AgreementAddition
        # POST finance/agreements/{id}/additions

    def update_agreement_addition(self, agreement_id, addition_id, operations) -> Optional[AgreementAddition]
        # PATCH finance/agreements/{id}/additions/{addition_id}

    def delete_agreement_addition(self, agreement_id, addition_id) -> bool
        # DELETE finance/agreements/{id}/additions/{addition_id}
```

---

## Phase 2 — Time Entries

**Why:** Time entries per ticket/member are essential for utilisation and billing reports.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/TimeEntries*
API base: time/entries
```

### New file: `models/time_entry.py`

```python
@dataclass
class TimeEntry:
    id: int
    company: dict
    chargeToId: int                  # ticket ID, project ID etc.
    chargeToType: str                # "ServiceTicket" | "ProjectTicket" | "ChargeCode" | "Activity"
    member: Optional[dict] = None
    locationId: Optional[int] = None
    businessUnitId: Optional[int] = None
    workType: Optional[dict] = None
    workRole: Optional[dict] = None
    agreement: Optional[dict] = None
    timeStart: Optional[str] = None
    timeEnd: Optional[str] = None
    hoursDeduct: Optional[float] = None
    actualHours: Optional[float] = None
    billableOption: str = "Billable"  # "Billable" | "DoNotBill" | "NoCharge" | "NoDefault"
    notes: Optional[str] = None
    internalNotes: Optional[str] = None
    addToDetailDescriptionFlag: bool = False
    addToInternalAnalysisFlag: bool = False
    addToResolutionFlag: bool = False
    emailResourceFlag: bool = False
    emailContactFlag: bool = False
    emailCcFlag: bool = False
    hoursBilled: Optional[float] = None
    enteredBy: Optional[str] = None
    dateEntered: Optional[str] = None
    invoiceId: Optional[int] = None
    mobileGuid: Optional[str] = None
    hourlyRate: Optional[float] = None
    ticket: Optional[dict] = None    # populated when chargeToType is ServiceTicket

    # Convenience properties
    # member_name, member_id
    # company_name, company_id
    # work_type_name, work_role_name
    # agreement_id, agreement_name
    # time_start_datetime, time_end_datetime, date_entered_datetime
    # is_billable → billableOption == "Billable"
```

### Additions to `TicketMixin`

```python
def get_ticket_time_entries(self, ticket_id, conditions="") -> List[TimeEntry]
    # GET time/entries?conditions=chargeToId={ticket_id} AND chargeToType="ServiceTicket"
```

### New file: `mixins/time_mixin.py`

```python
class TimeMixin:
    def get_time_entries(self, conditions="", orderby="", limit=None) -> List[TimeEntry]
        # GET time/entries

    def get_time_entry(self, entry_id) -> Optional[TimeEntry]
        # GET time/entries/{id}

    def get_time_entry_count(self, conditions="") -> Optional[int]

    def get_member_time_entries(self, member_id, conditions="") -> List[TimeEntry]
        # get_time_entries(conditions=f"member/id={member_id} AND {conditions}")

    def create_time_entry(self, charge_to_id, charge_to_type, member_id,
                          actual_hours, notes="", billable="Billable", ...) -> TimeEntry
        # POST time/entries

    def update_time_entry(self, entry_id, operations) -> Optional[TimeEntry]
        # PATCH time/entries/{id}

    def delete_time_entry(self, entry_id) -> bool
        # DELETE time/entries/{id}
```

---

## Phase 3 — Members + Contacts

**Why:** Attribution, resource reporting. Members = CW internal staff. Contacts = company-side contacts.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/SystemMembers*
pyconnectwise: src/pyconnectwise/endpoints/manage/CompanyContacts*
API base: system/members
API base: company/contacts
```

### New file: `models/member.py`

```python
@dataclass
class Member:
    id: int
    identifier: str                  # login username
    firstName: str
    lastName: str
    email: Optional[str] = None
    officeEmail: Optional[str] = None
    mobileEmail: Optional[str] = None
    title: Optional[str] = None
    reportsTo: Optional[dict] = None
    location: Optional[dict] = None
    department: Optional[dict] = None
    defaultEmail: str = "Office"
    inactiveFlag: bool = False
    calendarId: Optional[int] = None
    type: Optional[dict] = None       # member type
    mobileGuid: Optional[str] = None
    photo: Optional[dict] = None

    # Convenience properties
    # full_name → f"{firstName} {lastName}"
    # is_active → not inactiveFlag
    # department_name, location_name
```

### New file: `models/contact.py`

```python
@dataclass
class Contact:
    id: int
    firstName: str
    lastName: str
    company: dict
    title: Optional[str] = None
    email: Optional[str] = None      # from communicationItems — see note below
    site: Optional[dict] = None
    inactiveFlag: bool = False
    defaultPhoneType: Optional[str] = None
    defaultPhoneNbr: Optional[str] = None
    defaultBillingFlag: bool = False
    defaultContactFlag: bool = False
    communicationItems: Optional[list] = None   # list of {type, value, defaultFlag}
    department: Optional[dict] = None
    managerId: Optional[int] = None
    mobileGuid: Optional[str] = None

    # Convenience properties
    # full_name → f"{firstName} {lastName}"
    # company_name, company_id
    # is_active → not inactiveFlag
    # primary_email → first communicationItem where type.name=="Email" and defaultFlag==True
    # primary_phone → first communicationItem where type.name in ("Direct","Cell","Main") and defaultFlag==True
```

Note: Contact email/phone comes back nested in `communicationItems` list in the API response. The `from_dict` should handle this — store the raw list, expose clean helpers as properties.

### Additions to `CompaniesMixin`

```python
def get_company_contacts(self, company_id, conditions="") -> List[Contact]
    # GET company/contacts?conditions=company/id={company_id} AND {conditions}
```

### Additions to `TicketMixin`

```python
def get_ticket_members(self, ticket_id) -> List[Member]
    # GET service/tickets/{id}/members (returns assigned resources)

def get_ticket_contacts(self, ticket_id) -> List[Contact]
    # The API doesn't have a direct sub-resource for this;
    # fetch ticket, get contact dict, then get_contact(contact_id)
    # Document this clearly in the docstring
```

### New file: `mixins/members_mixin.py`

```python
class MembersMixin:
    def get_members(self, conditions="", orderby="", limit=None) -> List[Member]
        # GET system/members

    def get_member(self, member_id) -> Optional[Member]
        # GET system/members/{id}

    def get_member_by_identifier(self, identifier) -> Optional[Member]
        # get_members(conditions=f'identifier="{identifier}"', limit=1)[0] if results else None

    def get_member_count(self, conditions="") -> Optional[int]
```

### New file: `mixins/contacts_mixin.py`

```python
class ContactsMixin:
    def get_contacts(self, conditions="", orderby="", limit=None) -> List[Contact]
        # GET company/contacts

    def get_contact(self, contact_id) -> Optional[Contact]
        # GET company/contacts/{id}

    def get_contact_count(self, conditions="") -> Optional[int]

    def create_contact(self, first_name, last_name, company_id, email=None, ...) -> Contact
        # POST company/contacts

    def update_contact(self, contact_id, operations) -> Optional[Contact]
        # PATCH company/contacts/{id}

    def delete_contact(self, contact_id) -> bool
        # DELETE company/contacts/{id}
```

---

## Phase 4 — Finance: Invoices

**Why:** Billing history and invoice reconciliation against agreements.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/FinanceInvoices*
API base: finance/invoices
```

### New file: `models/invoice.py`

```python
@dataclass
class Invoice:
    id: int
    invoiceNumber: str
    type: str                        # "Standard" | "Agreement" | "CreditMemo" | "DownPayment"
    status: dict                     # {id, name} — "Draft" | "Sent" | "Paid" etc.
    company: dict
    invoiceDate: Optional[str] = None
    dueDate: Optional[str] = None
    billingDelivery: Optional[str] = None   # "Mail" | "Email" | "None"
    billingStatus: Optional[str] = None
    billingTerms: Optional[dict] = None
    reference: Optional[str] = None
    customerPO: Optional[str] = None
    dueAmount: Optional[float] = None
    paidAmount: Optional[float] = None
    invoiceTotal: Optional[float] = None
    taxTotal: Optional[float] = None
    currency: Optional[dict] = None
    locationId: Optional[int] = None
    departmentId: Optional[int] = None
    territory: Optional[dict] = None
    agreement: Optional[dict] = None
    billToCompany: Optional[dict] = None
    billToContact: Optional[dict] = None
    billToSite: Optional[dict] = None
    remitToName: Optional[str] = None
    internalNotes: Optional[str] = None
    topComment: Optional[str] = None
    bottomComment: Optional[str] = None
    closedFlag: bool = False
    sentFlag: bool = False

    # Convenience properties
    # company_name, company_id
    # status_name
    # agreement_id, agreement_name
    # invoice_datetime, due_datetime
    # is_closed, is_sent
    # balance → dueAmount - paidAmount
```

### New file: `mixins/invoices_mixin.py`

```python
class InvoicesMixin:
    def get_invoices(self, conditions="", orderby="", limit=None) -> List[Invoice]
        # GET finance/invoices

    def get_invoice(self, invoice_id) -> Optional[Invoice]
        # GET finance/invoices/{id}

    def get_invoice_count(self, conditions="") -> Optional[int]

    def get_company_invoices(self, company_id, conditions="") -> List[Invoice]
        # get_invoices(conditions=f"company/id={company_id} AND {conditions}")

    def get_agreement_invoices(self, agreement_id) -> List[Invoice]
        # get_invoices(conditions=f"agreement/id={agreement_id}")
```

---

## Phase 5 — Projects

**Why:** Project ticket reporting, resourcing, budget vs actual. Needed for project-heavy MSPs.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/ProjectProjects*
pyconnectwise: src/pyconnectwise/endpoints/manage/ProjectPhases*
pyconnectwise: src/pyconnectwise/endpoints/manage/ProjectTickets*
API base: project/projects
API base: project/projects/{id}/phases
API base: project/projects/{id}/phases/{id}/tickets  (or project/tickets)
```

### New file: `models/project.py`

```python
@dataclass
class Project:
    id: int
    name: str
    company: dict
    status: dict                     # {id, name} — "Open" | "Closed" etc.
    type: Optional[dict] = None
    board: Optional[dict] = None
    manager: Optional[dict] = None
    estimatedStart: Optional[str] = None
    estimatedEnd: Optional[str] = None
    actualStart: Optional[str] = None
    actualEnd: Optional[str] = None
    estimatedHours: Optional[float] = None
    actualHours: Optional[float] = None
    budgetFlag: bool = False
    budgetHours: Optional[float] = None
    billingAmount: Optional[float] = None
    billingMethod: Optional[str] = None   # "ActualRates" | "FixedFee" | "NotToExceed" | "OverrideRate"
    billingRateType: Optional[str] = None
    percentComplete: Optional[float] = None
    description: Optional[str] = None
    closedFlag: bool = False
    agreement: Optional[dict] = None
    site: Optional[dict] = None
    opportunity: Optional[dict] = None

    # Convenience properties
    # company_name, company_id
    # status_name, type_name, board_name
    # manager_name, manager_id
    # is_closed
    # estimated_start_datetime, estimated_end_datetime
    # actual_start_datetime, actual_end_datetime
```

### New file: `models/project_phase.py`

```python
@dataclass
class ProjectPhase:
    id: int
    projectId: int
    description: str
    status: Optional[dict] = None
    board: Optional[dict] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    wbsCode: Optional[str] = None
    billTime: Optional[str] = None
    billExpenses: Optional[str] = None
    billProducts: Optional[str] = None
    markAsClosedFlag: bool = False
    estimatedHours: Optional[float] = None
    scheduledHours: Optional[float] = None
    actualHours: Optional[float] = None
    parentPhaseId: Optional[int] = None

    # Convenience properties
    # status_name, board_name
    # is_closed → markAsClosedFlag
    # start_datetime, end_datetime
```

### New file: `mixins/projects_mixin.py`

```python
class ProjectsMixin:
    def get_projects(self, conditions="", orderby="", limit=None) -> List[Project]
        # GET project/projects

    def get_project(self, project_id) -> Optional[Project]
        # GET project/projects/{id}

    def get_project_count(self, conditions="") -> Optional[int]

    def get_company_projects(self, company_id, conditions="") -> List[Project]
        # get_projects(conditions=f"company/id={company_id} AND {conditions}")

    def get_project_phases(self, project_id) -> List[ProjectPhase]
        # GET project/projects/{id}/phases

    def get_project_phase(self, project_id, phase_id) -> Optional[ProjectPhase]
        # GET project/projects/{id}/phases/{phase_id}

    def get_project_tickets(self, project_id, conditions="") -> List[Ticket]
        # GET project/tickets?conditions=project/id={project_id} AND {conditions}
        # Returns Ticket objects (same model, chargeToType="ProjectTicket")

    def get_project_time_entries(self, project_id, conditions="") -> List[TimeEntry]
        # GET time/entries?conditions=chargeToId={project_id} AND chargeToType="ProjectTicket"
        # Requires TimeMixin

    def create_project(self, name, company_id, status_id, ...) -> Project
        # POST project/projects

    def update_project(self, project_id, operations) -> Optional[Project]
        # PATCH project/projects/{id}

    def delete_project(self, project_id) -> bool
        # DELETE project/projects/{id}
```

---

## Phase 6 — Sales: Opportunities

**Why:** Pipeline visibility. Less essential than the above but rounds out the API surface.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/SalesOpportunities*
API base: sales/opportunities
```

### New file: `models/opportunity.py`

```python
@dataclass
class Opportunity:
    id: int
    name: str
    company: dict
    status: dict
    type: Optional[dict] = None
    stage: Optional[dict] = None
    source: Optional[dict] = None
    location: Optional[dict] = None
    department: Optional[dict] = None
    primarySalesRep: Optional[dict] = None
    secondarySalesRep: Optional[dict] = None
    contact: Optional[dict] = None
    probability: Optional[dict] = None
    rating: Optional[dict] = None
    forecastClose: Optional[str] = None
    closedDate: Optional[str] = None
    closedBy: Optional[str] = None
    expectedCloseDate: Optional[str] = None
    pipelineChangeDate: Optional[str] = None
    dateBecameLead: Optional[str] = None
    estimatedRevenue: Optional[float] = None
    estimatedCost: Optional[float] = None
    estimatedDays: Optional[int] = None
    forecastRevenue: Optional[float] = None
    closedRevenue: Optional[float] = None
    wonFlag: bool = False
    lostFlag: bool = False
    closedFlag: bool = False
    notes: Optional[str] = None
    campaign: Optional[dict] = None
    customerPO: Optional[str] = None

    # Convenience properties
    # company_name, company_id
    # status_name, stage_name, type_name
    # primary_sales_rep_name, primary_sales_rep_id
    # probability_value → probability.get("probability") if probability else None
    # is_won, is_lost, is_closed
    # forecast_close_datetime, expected_close_datetime
    # margin → (estimatedRevenue or 0) - (estimatedCost or 0)
```

### New file: `mixins/opportunities_mixin.py`

```python
class OpportunitiesMixin:
    def get_opportunities(self, conditions="", orderby="", limit=None) -> List[Opportunity]
        # GET sales/opportunities

    def get_opportunity(self, opportunity_id) -> Optional[Opportunity]
        # GET sales/opportunities/{id}

    def get_opportunity_count(self, conditions="") -> Optional[int]

    def get_company_opportunities(self, company_id, conditions="") -> List[Opportunity]
        # get_opportunities(conditions=f"company/id={company_id} AND {conditions}")

    def get_open_opportunities(self, conditions="") -> List[Opportunity]
        # get_opportunities(conditions=f"closedFlag=false AND {conditions}")

    def create_opportunity(self, name, company_id, status_id, type_id=None, ...) -> Opportunity
        # POST sales/opportunities

    def update_opportunity(self, opportunity_id, operations) -> Optional[Opportunity]
        # PATCH sales/opportunities/{id}

    def close_opportunity_won(self, opportunity_id, closed_date=None) -> Optional[Opportunity]
        # PATCH wonFlag=true + closedDate

    def close_opportunity_lost(self, opportunity_id, closed_date=None) -> Optional[Opportunity]
        # PATCH lostFlag=true + closedDate
```

---

## Phase 7 — Schedule Entries

**Why:** Resource scheduling visibility — who's booked where, capacity planning.

### Endpoint reference
```
pyconnectwise: src/pyconnectwise/endpoints/manage/ScheduleEntries*
API base: schedule/entries
```

### New file: `models/schedule_entry.py`

```python
@dataclass
class ScheduleEntry:
    id: int
    objectId: int                    # ticket/project/activity ID
    name: str
    member: Optional[dict] = None
    where: Optional[dict] = None
    dateStart: Optional[str] = None
    dateEnd: Optional[str] = None
    reminder: Optional[dict] = None
    status: Optional[dict] = None
    type: Optional[dict] = None      # scheduleType: "S" (Service), "P" (Project), "A" (Activity) etc.
    span: Optional[dict] = None
    doneFlag: bool = False
    acknowledgedFlag: bool = False
    allowScheduleConflictsFlag: bool = False
    addMemberToProjectFlag: bool = False
    projectRoleId: Optional[int] = None
    mobileGuid: Optional[str] = None
    closeDate: Optional[str] = None
    hours: Optional[float] = None
    moveRemainingBudgetFlag: bool = False

    # Convenience properties
    # member_name, member_id
    # status_name, type_name
    # date_start_datetime, date_end_datetime
    # is_done → doneFlag
```

### New file: `mixins/schedule_mixin.py`

```python
class ScheduleMixin:
    def get_schedule_entries(self, conditions="", orderby="", limit=None) -> List[ScheduleEntry]
        # GET schedule/entries

    def get_schedule_entry(self, entry_id) -> Optional[ScheduleEntry]
        # GET schedule/entries/{id}

    def get_schedule_entry_count(self, conditions="") -> Optional[int]

    def get_member_schedule(self, member_id, conditions="") -> List[ScheduleEntry]
        # get_schedule_entries(conditions=f"member/id={member_id} AND {conditions}")

    def get_ticket_schedule(self, ticket_id) -> List[ScheduleEntry]
        # get_schedule_entries(conditions=f"objectId={ticket_id} AND type/identifier='S'")

    def create_schedule_entry(self, object_id, type_identifier, member_id,
                               date_start, date_end, hours=None, ...) -> ScheduleEntry
        # POST schedule/entries

    def delete_schedule_entry(self, entry_id) -> bool
        # DELETE schedule/entries/{id}
```

---

## `client.py` — final inheritance chain

Add new mixins in this order (maintains grouping by domain):

```python
class ConnectWiseClient(
    # Existing
    TicketMixin,
    ConfigurationMixin,
    CompaniesMixin,
    BoardsMixin,
    LookupMixin,
    # New — Finance
    AgreementsMixin,
    InvoicesMixin,
    # New — Time & Resources
    TimeMixin,
    MembersMixin,
    ContactsMixin,
    # New — Projects & Sales
    ProjectsMixin,
    OpportunitiesMixin,
    ScheduleMixin,
):
```

---

## `models/__init__.py` additions

Add in phase order:
```python
from .agreement import Agreement
from .agreement_addition import AgreementAddition
from .time_entry import TimeEntry
from .member import Member
from .contact import Contact
from .invoice import Invoice
from .project import Project
from .project_phase import ProjectPhase
from .opportunity import Opportunity
from .schedule_entry import ScheduleEntry
```

---

## LLM prompt docs to update (app/routes/generate.py `_CW_DOCS`)

Each phase that adds user-facing query capability needs a corresponding docs block added to `_CW_DOCS` in this repo's `generate.py` and to the `cw_cache.get_context()` reference data if it's cacheable.

**After Phase 1 (Agreements):** Document `cw.get_agreements()`, `cw.get_company_agreements(company_id)`, `cw.get_agreement_additions(agreement_id)`. Add agreement types to cached reference data.

**After Phase 2 (Time):** Document `cw.get_time_entries(conditions=...)`, `cw.get_ticket_time_entries(ticket_id)`.

**After Phase 3 (Members/Contacts):** Document `cw.get_members()`, `cw.get_company_contacts(company_id)`.

**After Phase 4 (Invoices):** Document `cw.get_invoices()`, `cw.get_company_invoices(company_id)`.

**After Phase 5 (Projects):** Document `cw.get_projects()`, `cw.get_project_phases(project_id)`, `cw.get_project_tickets(project_id)`.

**After Phase 6 (Opportunities):** Document `cw.get_opportunities()`, `cw.get_open_opportunities()`.

---

## Implementation order rationale

1. **Agreements** — highest MSP value, self-contained, no dependencies
2. **Time entries** — needed for billing/utilisation, depends on nothing new
3. **Members + Contacts** — enables attribution on time entries and tickets; contacts needed for project work too
4. **Invoices** — references agreements; read-mostly, straightforward
5. **Projects** — complex (phases + tickets + time), benefits from Time and Members being done first
6. **Opportunities** — standalone, can be done anytime after the pattern is established
7. **Schedule** — useful but least urgent; depends on Members being done

Each phase is independent enough to ship and use in widget code as soon as it's merged.
