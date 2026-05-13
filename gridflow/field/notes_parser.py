"""
Parser for field identity notes files.

Extracts structured data from semi-structured notes text captured
during field surveys. Designed to be permissive — never crash on
malformed input.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NotesParser:
    """
    Parse structured sections from field notes text.

    Notes may use section headers (POLE IDENTITY, EQUIPMENT OBSERVED, etc.)
    or be entirely free-text. Parser handles both gracefully.
    """

    SECTION_HEADERS = {
        "POLE IDENTITY",
        "LOCATION",
        "CONDITION",
        "EQUIPMENT OBSERVED",
        "DEFECTS",
        "VERIFICATION REQUIRED",
    }

    def parse(self, notes_content: str) -> dict:
        """
        Parse notes content and return structured dict.

        Args:
            notes_content: Raw text of notes file

        Returns:
            Dict with keys: support_no, voltage, condition, access,
            equipment, defects, verification_flags, free_text
        """
        if not notes_content or not notes_content.strip():
            return self._empty_result()

        result = self._empty_result()

        try:
            lines = notes_content.splitlines()
            current_section = None
            free_lines = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # Detect section header
                if stripped.upper() in self.SECTION_HEADERS:
                    current_section = stripped.upper()
                    continue

                # Parse key: value lines
                if ":" in stripped:
                    parsed = self._parse_key_value(stripped, current_section, result)
                    if not parsed:
                        free_lines.append(stripped)
                elif current_section == "EQUIPMENT OBSERVED":
                    result["equipment"].append(stripped)
                elif current_section == "DEFECTS":
                    if stripped.lower() not in ("none observed", "none", "n/a"):
                        result["defects"].append(stripped)
                elif current_section == "VERIFICATION REQUIRED":
                    result["verification_flags"].append(stripped)
                else:
                    free_lines.append(stripped)

            result["free_text"] = "\n".join(free_lines)

        except Exception as e:
            logger.warning("Notes parse error: %s", e)

        return result

    def _parse_key_value(self, line: str, section: Optional[str], result: dict) -> bool:
        """
        Parse a key:value line into result dict.

        Returns True if line was consumed, False if not recognized.
        """
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        key_lower = key.lower()

        # Support number
        if key_lower in ("support no", "support_no", "support number"):
            result["support_no"] = value
            return True

        # Voltage
        if key_lower in ("voltage", "voltage level"):
            result["voltage"] = value
            return True

        # Condition
        if key_lower in ("overall", "condition", "overall condition"):
            result["condition"] = value
            return True

        # Access
        if key_lower in ("access", "access type"):
            result["access"] = value
            return True

        # Equipment lines (key: value format within EQUIPMENT OBSERVED)
        if section == "EQUIPMENT OBSERVED":
            if value:
                result["equipment"].append(f"{key}: {value}")
            else:
                result["equipment"].append(key)
            return True

        return False

    @staticmethod
    def _empty_result() -> dict:
        """Return empty result dict with all expected keys."""
        return {
            "support_no": None,
            "voltage": None,
            "condition": None,
            "access": None,
            "equipment": [],
            "defects": [],
            "verification_flags": [],
            "free_text": "",
        }
