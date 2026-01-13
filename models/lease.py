"""Lease data model for Wyoming state leases."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from .commodity import CommodityType


class LeaseStatus(Enum):
    """Status of a state lease."""

    ACTIVE = "Active"
    EXPIRED = "Expired"
    TERMINATED = "Terminated"
    PENDING = "Pending"
    SUSPENDED = "Suspended"
    PRODUCING = "Producing"
    HELD_BY_PRODUCTION = "Held by Production"
    UNKNOWN = "Unknown"

    @classmethod
    def from_string(cls, value: str) -> 'LeaseStatus':
        """Convert a string to a LeaseStatus enum value."""
        value_lower = value.lower().strip()

        for status in cls:
            if status.value.lower() == value_lower:
                return status

        # Common variations
        if 'active' in value_lower or 'current' in value_lower:
            return cls.ACTIVE
        elif 'expire' in value_lower:
            return cls.EXPIRED
        elif 'terminat' in value_lower or 'cancel' in value_lower:
            return cls.TERMINATED
        elif 'pending' in value_lower or 'application' in value_lower:
            return cls.PENDING
        elif 'suspend' in value_lower:
            return cls.SUSPENDED
        elif 'produc' in value_lower:
            return cls.PRODUCING
        elif 'hbp' in value_lower or 'held' in value_lower:
            return cls.HELD_BY_PRODUCTION

        return cls.UNKNOWN


# Status colors for visual indicators
STATUS_COLORS: Dict[LeaseStatus, str] = {
    LeaseStatus.ACTIVE: "#27AE60",          # Green
    LeaseStatus.EXPIRED: "#95A5A6",         # Gray
    LeaseStatus.TERMINATED: "#E74C3C",      # Red
    LeaseStatus.PENDING: "#F39C12",         # Orange
    LeaseStatus.SUSPENDED: "#9B59B6",       # Purple
    LeaseStatus.PRODUCING: "#2ECC71",       # Bright green
    LeaseStatus.HELD_BY_PRODUCTION: "#1ABC9C",  # Turquoise
    LeaseStatus.UNKNOWN: "#BDC3C7",         # Light gray
}


@dataclass
class Lease:
    """Represents a Wyoming state mineral lease."""

    lease_number: str
    commodity_type: CommodityType
    status: LeaseStatus
    county: str
    acres: float
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    lessee_name: str = ""
    township: str = ""
    range_str: str = ""
    section: str = ""
    legal_description: str = ""
    annual_rental: float = 0.0
    royalty_rate: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def location_str(self) -> str:
        """Return a formatted location string."""
        parts = []
        if self.township:
            parts.append(f"T{self.township}")
        if self.range_str:
            parts.append(f"R{self.range_str}")
        if self.section:
            parts.append(f"Sec {self.section}")
        return ", ".join(parts) if parts else self.legal_description or "N/A"

    @property
    def has_coordinates(self) -> bool:
        """Check if lease has valid coordinates."""
        return self.latitude is not None and self.longitude is not None

    @property
    def days_until_expiration(self) -> Optional[int]:
        """Calculate days until lease expiration."""
        if self.expiration_date is None:
            return None
        delta = self.expiration_date - date.today()
        return delta.days

    @property
    def is_expiring_soon(self) -> bool:
        """Check if lease expires within 90 days."""
        days = self.days_until_expiration
        return days is not None and 0 < days <= 90

    def to_dict(self) -> Dict[str, Any]:
        """Convert lease to dictionary representation."""
        return {
            'lease_number': self.lease_number,
            'commodity_type': self.commodity_type.value,
            'status': self.status.value,
            'county': self.county,
            'acres': self.acres,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'lessee_name': self.lessee_name,
            'township': self.township,
            'range': self.range_str,
            'section': self.section,
            'legal_description': self.legal_description,
            'annual_rental': self.annual_rental,
            'royalty_rate': self.royalty_rate,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'notes': self.notes,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lease':
        """Create a Lease instance from a dictionary."""
        effective_date = None
        expiration_date = None

        if data.get('effective_date'):
            try:
                effective_date = datetime.fromisoformat(data['effective_date']).date()
            except (ValueError, TypeError):
                pass

        if data.get('expiration_date'):
            try:
                expiration_date = datetime.fromisoformat(data['expiration_date']).date()
            except (ValueError, TypeError):
                pass

        return cls(
            lease_number=data.get('lease_number', ''),
            commodity_type=CommodityType.from_string(data.get('commodity_type', '')),
            status=LeaseStatus.from_string(data.get('status', '')),
            county=data.get('county', ''),
            acres=float(data.get('acres', 0)),
            effective_date=effective_date,
            expiration_date=expiration_date,
            lessee_name=data.get('lessee_name', ''),
            township=data.get('township', ''),
            range_str=data.get('range', ''),
            section=data.get('section', ''),
            legal_description=data.get('legal_description', ''),
            annual_rental=float(data.get('annual_rental', 0)),
            royalty_rate=float(data.get('royalty_rate', 0)),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            notes=data.get('notes', ''),
            metadata=data.get('metadata', {}),
        )


# Wyoming counties for validation/filtering
WYOMING_COUNTIES: List[str] = [
    "Albany", "Big Horn", "Campbell", "Carbon", "Converse",
    "Crook", "Fremont", "Goshen", "Hot Springs", "Johnson",
    "Laramie", "Lincoln", "Natrona", "Niobrara", "Park",
    "Platte", "Sheridan", "Sublette", "Sweetwater", "Teton",
    "Uinta", "Washakie", "Weston"
]
