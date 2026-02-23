from dataclasses import dataclass, fields
from datetime import datetime
from typing import Optional
from connectwise.utils import parse_cw_datetime


@dataclass
class Configuration:
    """Represents a ConnectWise configuration (device/asset)."""
    id: int
    name: str
    company: dict
    type: dict
    status: dict

    # Optional fields
    location: Optional[dict] = None
    site: Optional[dict] = None
    contact: Optional[dict] = None
    department: Optional[dict] = None
    locationId: Optional[int] = None
    businessUnitId: Optional[int] = None
    companyLocationId: Optional[int] = None
    serialNumber: Optional[str] = None
    modelNumber: Optional[str] = None
    tagNumber: Optional[str] = None
    purchaseDate: Optional[str] = None
    installationDate: Optional[str] = None
    warrantyExpirationDate: Optional[str] = None
    vendorNotes: Optional[str] = None
    notes: Optional[str] = None
    macAddress: Optional[str] = None
    lastLoginName: Optional[str] = None
    billFlag: bool = False
    backupSuccesses: Optional[int] = None
    backupIncomplete: Optional[int] = None
    backupFailed: Optional[int] = None
    backupRestores: Optional[int] = None
    lastBackupDate: Optional[str] = None
    backupServerName: Optional[str] = None
    backupProtectedDeviceList: Optional[str] = None
    backupYear: Optional[int] = None
    backupMonth: Optional[int] = None
    ipAddress: Optional[str] = None
    defaultGateway: Optional[str] = None
    osType: Optional[str] = None
    osInfo: Optional[str] = None
    cpuSpeed: Optional[str] = None
    ram: Optional[str] = None
    localHardDrives: Optional[str] = None
    parentConfigurationId: Optional[int] = None
    vendor: Optional[dict] = None
    manufacturer: Optional[dict] = None
    questions: Optional[list] = None
    activeFlag: bool = True
    managementLink: Optional[str] = None
    remoteLink: Optional[str] = None
    sla: Optional[dict] = None
    mobileGuid: Optional[str] = None
    deviceIdentifier: Optional[str] = None
    showRemoteFlag: Optional[bool] = None
    showAutomateFlag: Optional[bool] = None
    needsRenewalFlag: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Configuration':
        """
        Create a Configuration instance from a dictionary.
        Handles partial data from API when using 'fields' parameter.

        Args:
            data: Dictionary containing configuration data from API

        Returns:
            Configuration: Configuration object
        """
        # Extract only fields that exist in the dataclass
        valid_fields = {field for field in cls.__dataclass_fields__.keys()}
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_fields
        }

        # Set required fields with defaults if missing (for partial data)
        if 'id' not in filtered_data:
            filtered_data['id'] = data.get('id', 0)
        if 'name' not in filtered_data:
            filtered_data['name'] = data.get('name', '')
        if 'company' not in filtered_data:
            filtered_data['company'] = data.get('company', {})
        if 'type' not in filtered_data:
            filtered_data['type'] = data.get('type', {})
        if 'status' not in filtered_data:
            filtered_data['status'] = data.get('status', {})

        return cls(**filtered_data)

    def to_dict(self, exclude_none: bool = True, exclude_id: bool = False) -> dict:
        """
        Convert Configuration to a dict suitable for CW API POST/PATCH.

        Args:
            exclude_none: If True, omit fields with None values.
            exclude_id: If True, omit the id field (useful for create operations).

        Returns:
            dict: API-compatible dictionary representation.
        """
        result = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if exclude_id and f.name == "id":
                continue
            if exclude_none and value is None:
                continue
            result[f.name] = value
        return result

    def set_question(self, question_id: int, answer: str):
        """Set or update a custom question answer by ID."""
        if self.questions is None:
            self.questions = []
        for q in self.questions:
            if q["questionId"] == question_id:
                q["answer"] = answer
                return
        self.questions.append({"questionId": question_id, "answer": answer})

    def set_question_by_name(self, name: str, answer: str, question_definitions: list):
        """
        Set or update a custom question answer by matching its label.

        Args:
            name: The question label to match (case-insensitive).
            answer: The answer value to set.
            question_definitions: List of question definition dicts from
                                  get_configuration_type_questions(), each
                                  containing 'questionId' and 'question' keys.

        Raises:
            ValueError: If no question matches the given name.
        """
        for qdef in question_definitions:
            if qdef.get("question", "").lower() == name.lower():
                qid = qdef.get("questionId") or qdef.get("id")
                self.set_question(qid, answer)
                return
        available = [q.get("question", "") for q in question_definitions]
        raise ValueError(
            f"No question matching '{name}'. "
            f"Available questions: {available}"
        )

    @property
    def company_name(self) -> str:
        """Get company name from nested dict."""
        return self.company.get("name", "") if self.company else ""

    @property
    def company_id(self) -> Optional[int]:
        """Get company ID from nested dict."""
        return self.company.get("id") if self.company else None

    @property
    def type_name(self) -> str:
        """Get type name from nested dict."""
        return self.type.get("name", "") if self.type else ""

    @property
    def status_name(self) -> str:
        """Get status name from nested dict."""
        return self.status.get("name", "") if self.status else ""

    @property
    def vendor_name(self) -> Optional[str]:
        """Get vendor name from nested dict."""
        return self.vendor.get("name") if self.vendor else None

    @property
    def manufacturer_name(self) -> Optional[str]:
        """Get manufacturer name from nested dict."""
        return self.manufacturer.get("name") if self.manufacturer else None

    @property
    def is_active(self) -> bool:
        """Check if configuration is active."""
        return self.activeFlag

    @property
    def purchase_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.purchaseDate)

    @property
    def installation_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.installationDate)

    @property
    def warranty_expiration_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.warrantyExpirationDate)

    @property
    def last_backup_datetime(self) -> Optional[datetime]:
        return parse_cw_datetime(self.lastBackupDate)

    def __str__(self) -> str:
        """String representation showing key configuration details."""
        return f"#{self.id} - {self.name} [{self.status_name}]"
