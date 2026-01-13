"""Commodity type definitions and color mappings for Wyoming state leases."""

from enum import Enum
from typing import Dict, Tuple


class CommodityType(Enum):
    """Enumeration of commodity types for Wyoming state leases."""

    OIL = "Oil"
    GAS = "Gas"
    OIL_AND_GAS = "Oil & Gas"
    COAL = "Coal"
    TRONA = "Trona"
    URANIUM = "Uranium"
    BENTONITE = "Bentonite"
    SAND_GRAVEL = "Sand & Gravel"
    LIMESTONE = "Limestone"
    GYPSUM = "Gypsum"
    OTHER_MINERALS = "Other Minerals"
    GEOTHERMAL = "Geothermal"
    HELIUM = "Helium"
    UNKNOWN = "Unknown"

    @classmethod
    def from_string(cls, value: str) -> 'CommodityType':
        """Convert a string to a CommodityType enum value."""
        value_lower = value.lower().strip()

        # Direct matches
        for commodity in cls:
            if commodity.value.lower() == value_lower:
                return commodity

        # Fuzzy matching for common variations
        if 'oil' in value_lower and 'gas' in value_lower:
            return cls.OIL_AND_GAS
        elif 'oil' in value_lower or 'petroleum' in value_lower or 'crude' in value_lower:
            return cls.OIL
        elif 'gas' in value_lower or 'natural gas' in value_lower:
            return cls.GAS
        elif 'coal' in value_lower:
            return cls.COAL
        elif 'trona' in value_lower or 'soda ash' in value_lower:
            return cls.TRONA
        elif 'uranium' in value_lower:
            return cls.URANIUM
        elif 'bentonite' in value_lower:
            return cls.BENTONITE
        elif 'sand' in value_lower or 'gravel' in value_lower:
            return cls.SAND_GRAVEL
        elif 'limestone' in value_lower:
            return cls.LIMESTONE
        elif 'gypsum' in value_lower:
            return cls.GYPSUM
        elif 'geothermal' in value_lower:
            return cls.GEOTHERMAL
        elif 'helium' in value_lower:
            return cls.HELIUM

        return cls.UNKNOWN


# Color mappings for each commodity type (hex colors)
# Colors chosen for distinctiveness and accessibility
COMMODITY_COLORS: Dict[CommodityType, str] = {
    CommodityType.OIL: "#2E4057",           # Dark blue-gray (petroleum)
    CommodityType.GAS: "#FF6B35",           # Orange (natural gas flame)
    CommodityType.OIL_AND_GAS: "#048A81",   # Teal (combination)
    CommodityType.COAL: "#1C1C1C",          # Near black (coal)
    CommodityType.TRONA: "#9B59B6",         # Purple (mineral)
    CommodityType.URANIUM: "#F1C40F",       # Yellow (radioactive symbol)
    CommodityType.BENTONITE: "#A0522D",     # Sienna brown (clay)
    CommodityType.SAND_GRAVEL: "#D4AC6E",   # Sandy tan
    CommodityType.LIMESTONE: "#BDC3C7",     # Light gray
    CommodityType.GYPSUM: "#ECF0F1",        # Off-white
    CommodityType.OTHER_MINERALS: "#7F8C8D", # Gray
    CommodityType.GEOTHERMAL: "#E74C3C",    # Red (heat)
    CommodityType.HELIUM: "#85C1E9",        # Light blue (gas)
    CommodityType.UNKNOWN: "#95A5A6",       # Neutral gray
}

# Text colors for legend (to ensure readability on colored backgrounds)
COMMODITY_TEXT_COLORS: Dict[CommodityType, str] = {
    CommodityType.OIL: "#FFFFFF",
    CommodityType.GAS: "#FFFFFF",
    CommodityType.OIL_AND_GAS: "#FFFFFF",
    CommodityType.COAL: "#FFFFFF",
    CommodityType.TRONA: "#FFFFFF",
    CommodityType.URANIUM: "#000000",
    CommodityType.BENTONITE: "#FFFFFF",
    CommodityType.SAND_GRAVEL: "#000000",
    CommodityType.LIMESTONE: "#000000",
    CommodityType.GYPSUM: "#000000",
    CommodityType.OTHER_MINERALS: "#FFFFFF",
    CommodityType.GEOTHERMAL: "#FFFFFF",
    CommodityType.HELIUM: "#000000",
    CommodityType.UNKNOWN: "#FFFFFF",
}


def get_commodity_color(commodity: CommodityType) -> Tuple[str, str]:
    """
    Get the background and text colors for a commodity type.

    Args:
        commodity: The CommodityType to get colors for

    Returns:
        Tuple of (background_color, text_color) as hex strings
    """
    bg_color = COMMODITY_COLORS.get(commodity, "#95A5A6")
    text_color = COMMODITY_TEXT_COLORS.get(commodity, "#FFFFFF")
    return bg_color, text_color


def get_all_commodities() -> list:
    """Return a list of all commodity types (excluding UNKNOWN)."""
    return [c for c in CommodityType if c != CommodityType.UNKNOWN]
