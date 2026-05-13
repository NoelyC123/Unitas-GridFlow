"""
Support number normalization and validation.

Standardizes support numbers across different DNO formats and detects variants.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class SupportNumberNormalizer:
    """
    Normalize and validate support numbers from various DNO formats.

    Handles:
    - Pure numeric: "903203"
    - With prefix: "SP903203"
    - With suffix: "903201A"
    - With separators: "90-3203"
    - Whitespace/case variations
    """

    # Patterns for common support number formats
    PATTERNS = {
        "numeric_only": r"^(\d+)$",
        "with_prefix": r"^([A-Z]+)(\d+)$",
        "with_suffix": r"^(\d+)([A-Z]+)$",
        "with_separator": r"^(\d+)[-\s](\d+)$",
        "sp_format": r"^SP(\d+)$",
    }

    UNKNOWN_PATTERNS = [
        "unknown",
        "null",
        "none",
        "n/a",
        "na",
        "tbd",
        "?",
        "",
    ]

    def normalize(self, support_no: Optional[str]) -> Optional[str]:
        """
        Normalize a support number to standard format.

        Args:
            support_no: Raw support number from source

        Returns:
            Normalized support number or None if unknown
        """
        if not support_no:
            return None

        # Convert to string and strip whitespace
        support_no = str(support_no).strip()

        # Check for unknown patterns
        if support_no.lower() in self.UNKNOWN_PATTERNS:
            return None

        # Convert to uppercase for processing
        support_no_upper = support_no.upper()

        # Try to extract numeric component
        numeric = self.extract_numeric(support_no_upper)
        if numeric:
            # Return the numeric portion as normalized form
            return numeric

        # If no numeric extracted, return original (normalized case)
        return support_no_upper

    def extract_numeric(self, support_no: str) -> Optional[str]:
        """
        Extract numeric component from support number.

        Args:
            support_no: Support number (should be uppercase)

        Returns:
            Numeric portion or None if no digits found
        """
        # Extract all digits
        digits = re.sub(r"[^0-9]", "", support_no)
        if digits:
            return digits
        return None

    def detect_variant(self, support_no: Optional[str]) -> Optional[str]:
        """
        Detect variant format (suffix, prefix, etc).

        Args:
            support_no: Support number to analyze

        Returns:
            Variant description or None if pure numeric
        """
        if not support_no:
            return None

        support_no = str(support_no).strip().upper()

        # Check SP prefix
        if match := re.match(self.PATTERNS["sp_format"], support_no):
            return "SP_PREFIX"

        # Check generic prefix
        if match := re.match(self.PATTERNS["with_prefix"], support_no):
            return f"PREFIX_{match.group(1)}"

        # Check suffix
        if match := re.match(self.PATTERNS["with_suffix"], support_no):
            return f"SUFFIX_{match.group(2)}"

        # Check separator
        if match := re.match(self.PATTERNS["with_separator"], support_no):
            return "WITH_SEPARATOR"

        # Check pure numeric
        if match := re.match(self.PATTERNS["numeric_only"], support_no):
            return None  # Pure numeric, no variant

        return "UNKNOWN_FORMAT"

    def is_valid_format(self, support_no: Optional[str]) -> bool:
        """
        Check if support number follows expected format.

        Args:
            support_no: Support number to validate

        Returns:
            True if format is recognized
        """
        if not support_no:
            return False

        support_no = str(support_no).strip()

        # Check unknown patterns
        if support_no.lower() in self.UNKNOWN_PATTERNS:
            return False

        support_no_upper = support_no.upper()

        # Check against known patterns
        for pattern in self.PATTERNS.values():
            if re.match(pattern, support_no_upper):
                return True

        return False

    def normalize_batch(self, support_numbers: list[str]) -> dict[str, Optional[str]]:
        """
        Normalize multiple support numbers.

        Args:
            support_numbers: List of support numbers

        Returns:
            Dict mapping original to normalized
        """
        result = {}
        for sno in support_numbers:
            result[sno] = self.normalize(sno)
        return result

    def find_duplicates(self, support_numbers: list[str]) -> dict[str, list[str]]:
        """
        Find support numbers that normalize to same value.

        Args:
            support_numbers: List of support numbers

        Returns:
            Dict of normalized value -> list of originals that map to it
        """
        groups = {}
        for sno in support_numbers:
            normalized = self.normalize(sno)
            if normalized:
                if normalized not in groups:
                    groups[normalized] = []
                groups[normalized].append(sno)

        # Return only groups with duplicates
        return {k: v for k, v in groups.items() if len(v) > 1}
