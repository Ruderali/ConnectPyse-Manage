from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Configuration:
    """Represents a ConnectWise configuration (device/asset)."""
    id: int
    name: str
    company: dict
    type: dict
    status: dict

    # Optional fields
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
    billFlag: bool = True
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
        """Parse purchaseDate as a datetime object."""
        if not self.purchaseDate:
            return None
        try:
            return datetime.fromisoformat(self.purchaseDate.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    @property
    def installation_datetime(self) -> Optional[datetime]:
        """Parse installationDate as a datetime object."""
        if not self.installationDate:
            return None
        try:
            return datetime.fromisoformat(self.installationDate.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    @property
    def warranty_expiration_datetime(self) -> Optional[datetime]:
        """Parse warrantyExpirationDate as a datetime object."""
        if not self.warrantyExpirationDate:
            return None
        try:
            return datetime.fromisoformat(self.warrantyExpirationDate.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    @property
    def last_backup_datetime(self) -> Optional[datetime]:
        """Parse lastBackupDate as a datetime object."""
        if not self.lastBackupDate:
            return None
        try:
            return datetime.fromisoformat(self.lastBackupDate.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def __str__(self) -> str:
        """String representation showing key configuration details."""
        return f"#{self.id} - {self.name} [{self.status_name}]"
