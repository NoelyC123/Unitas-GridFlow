"""Runtime leakage prevention tests for Stage 4 structured capture.

These tests must pass on current master and must continue to pass after
Stage 4A, 4B, and until Stage 4C explicitly introduces upload routes.

Each test class guards a specific surface against premature Stage 4 exposure:

- MapViewerLeakage:    map-viewer.js popup renderer
- ApiIntakeLeakage:    Flask upload route (api_intake.py)
- QAEngineLeakage:     QA issue generation (qa_engine.py)
- ControllerLeakage:   controller intake pipeline
- C2E2PopupLeakage:    C2E2 field reference and popup sections
- FieldReferenceLeakage: field_reference source vocabulary

A test failure here means Stage 4 has leaked into a live surface before the
Stage 4C runtime integration task has been approved. Investigate and revert.

Reference: AI_CONTROL/48_STAGE4A_RUNTIME_LEAKAGE_GUARD.md
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _grep_file(path: Path, needle: str) -> list[int]:
    """Return line numbers where needle appears in path."""
    lines = []
    for i, line in enumerate(_read(path).splitlines(), start=1):
        if needle.lower() in line.lower():
            lines.append(i)
    return lines


# Tokens whose presence in a runtime file indicates Stage 4 leakage.
_STAGE4_LEAK_TOKENS = [
    "structured_capture",
    "stage4_future_capture",
    "pole_class",  # Stage 4 schema field — not in C2E2 popup
    "lean_direction",  # Stage 4 structural field
    "lean_severity",  # Stage 4 structural field
    "equipment_condition",  # Stage 4 equipment field (distinct from equipment_present)
    "capture_source",  # Stage 4 metadata field
    "captured_by",  # Stage 4 metadata field
    "capture_date",  # Stage 4 metadata field
]

# Tokens we allow in runtime files (they exist for Trimble/existing reasons).
_ALLOWED_IN_RUNTIME = {
    "equipment_present",  # C2E2 popup field from Trimble
}


# ---------------------------------------------------------------------------
# Map-viewer.js leakage guard
# ---------------------------------------------------------------------------


class TestMapViewerLeakage:
    """map-viewer.js must not reference Stage 4 fields, sources, or status tokens."""

    MAP_JS = REPO_ROOT / "app" / "static" / "js" / "map-viewer.js"

    def test_map_viewer_has_no_structured_capture_source(self) -> None:
        source = _read(self.MAP_JS)
        assert "structured_capture" not in source, (
            "map-viewer.js contains 'structured_capture'. "
            "Stage 4 source label must not appear in the map renderer before Stage 4D."
        )

    def test_map_viewer_has_no_stage4_future_capture_status(self) -> None:
        source = _read(self.MAP_JS)
        assert "stage4_future_capture" not in source, (
            "map-viewer.js contains 'stage4_future_capture'. "
            "Stage 4 status token must not appear in the popup renderer."
        )

    def test_map_viewer_has_no_stage4_metadata_fields(self) -> None:
        source = _read(self.MAP_JS)
        for token in ("capture_source", "captured_by", "capture_date"):
            assert token not in source, (
                f"map-viewer.js contains Stage 4 metadata field {token!r}. "
                "Structured capture metadata must not appear in popup rendering."
            )

    def test_map_viewer_has_no_stage4_metadata_fields_in_popup_functions(self) -> None:
        """Stage 4 capture metadata fields must not appear in popup-generating code.

        Note: lean_direction, lean_severity, pole_class, pole_strength already
        exist in map-viewer.js as part of the Review OS popup (added before Stage 4).
        They are NOT considered Stage 4 leakage. Only pure Stage 4 metadata fields
        (capture_source, captured_by, capture_date) are guarded here.
        """
        source = _read(self.MAP_JS)
        for token in ("capture_source", "captured_by", "capture_date"):
            assert token not in source, (
                f"map-viewer.js contains Stage 4 metadata field {token!r}. "
                "Capture metadata fields must not appear in popup rendering before Stage 4D."
            )

    def test_map_viewer_hasvalue_guard_count_not_reduced(self) -> None:
        """hasValue() guard count must not decrease — it protects popup truthfulness.

        This is a regression guard: if Stage 4 changes accidentally remove
        hasValue() checks that hide empty fields, C2E2 popup truthfulness
        degrades. The baseline count of 41 was captured on master at
        commit 857861e (confirmed by python source.count('hasValue(')).
        """
        source = _read(self.MAP_JS)
        count = source.count("hasValue(")
        baseline = 41
        assert count >= baseline, (
            f"map-viewer.js has {count} hasValue() guards, down from baseline {baseline}. "
            "Stage 4 changes must not remove popup truthfulness guards."
        )


# ---------------------------------------------------------------------------
# Flask upload route (api_intake.py) leakage guard
# ---------------------------------------------------------------------------


class TestApiIntakeLeakage:
    """api_intake.py must not accept, parse, or route Stage 4 structured capture data."""

    API_INTAKE = REPO_ROOT / "app" / "routes" / "api_intake.py"

    def test_api_intake_has_no_structured_capture_source_label(self) -> None:
        """api_intake.py must not reference the 'structured_capture' source label.

        Note: api_intake.py legitimately contains 'merge' (merge_equipment_fields_into_props
        etc.) and 'structured' (file_type='structured' classification). These are existing
        features — NOT Stage 4 leakage. Only the Stage 4 source label and library imports
        are guarded.
        """
        source = _read(self.API_INTAKE)
        assert "structured_capture" not in source, (
            "api_intake.py references 'structured_capture'. "
            "Stage 4 source label must not appear in the upload route before Stage 4C."
        )

    def test_api_intake_has_no_stage4_library_imports(self) -> None:
        """Stage 4 schema and validator modules must not be imported by the upload route."""
        source = _read(self.API_INTAKE)
        for token in ("structured_capture_schema", "structured_capture_validators"):
            assert token not in source, (
                f"api_intake.py imports {token!r}. "
                "Stage 4 library must not be wired into the upload route before Stage 4C."
            )


# ---------------------------------------------------------------------------
# QA engine leakage guard
# ---------------------------------------------------------------------------


class TestQAEngineLeakage:
    """qa_engine.py must not consume structured_capture values as QA evidence."""

    QA_ENGINE = REPO_ROOT / "app" / "qa_engine.py"

    def test_qa_engine_has_no_structured_capture_import(self) -> None:
        source = _read(self.QA_ENGINE)
        assert "structured_capture" not in source, (
            "qa_engine.py references 'structured_capture'. "
            "QA rules must not consume Stage 4 values before Stage 4C."
        )

    def test_qa_engine_has_no_stage4_schema_reference(self) -> None:
        source = _read(self.QA_ENGINE)
        for token in ("structured_capture_schema", "stage4_future_capture"):
            assert token not in source, (
                f"qa_engine.py contains {token!r}. "
                "QA engine must not reference Stage 4 status or schema."
            )


# ---------------------------------------------------------------------------
# Controller intake leakage guard
# ---------------------------------------------------------------------------


class TestControllerIntakeLeakage:
    """controller_intake.py must not parse or route Stage 4 columns."""

    CONTROLLER_INTAKE = REPO_ROOT / "app" / "controller_intake.py"

    def test_controller_intake_has_no_structured_capture_import(self) -> None:
        source = _read(self.CONTROLLER_INTAKE)
        assert "structured_capture" not in source, (
            "controller_intake.py references 'structured_capture'. "
            "The Trimble controller intake pipeline must not touch Stage 4 columns."
        )


# ---------------------------------------------------------------------------
# C2E2 popup field scope leakage guard
# ---------------------------------------------------------------------------


class TestC2E2PopupLeakage:
    """C2E2 popup field scope must not include Stage 4 fields.

    The C2E2 popup shows only reality-based Trimble/derived fields.
    Stage 4 fields must not appear as popup sections or rows.
    """

    def test_c2e2_popup_groups_contain_no_stage4_fields(self) -> None:
        from app.field_reference import POPUP_FIELD_GROUPS
        from app.structured_capture_schema import get_stage4_template_headers

        stage4_field_names = set(get_stage4_template_headers())
        popup_fields: set[str] = set()
        for fields in POPUP_FIELD_GROUPS.values():
            popup_fields.update(fields)

        # These field names appear in both the C2E2 popup (Trimble-sourced) and the Stage 4
        # schema (structured capture). They represent the same real-world concepts captured
        # at different stages. Their presence in Stage 4 schema does not constitute leakage.
        shared_names = {"pole_id", "structure_type", "asset_intent", "material"}
        leaked = (popup_fields & stage4_field_names) - shared_names

        assert not leaked, (
            f"Stage 4 fields appear in C2E2 popup groups: {sorted(leaked)}. "
            "C2E2 popup must only contain reality-based Trimble/derived fields."
        )

    def test_c2e2_field_definitions_contain_no_stage4_source(self) -> None:
        from app.field_reference import FIELD_DEFINITIONS

        for field_name, defn in FIELD_DEFINITIONS.items():
            assert defn.get("source") != "structured_capture", (
                f"C2E2 field {field_name!r} has source='structured_capture'. "
                "C2E2 popup fields must not use structured_capture as their source."
            )

    def test_c2e2_field_definitions_contain_no_stage4_status(self) -> None:
        from app.field_reference import FIELD_DEFINITIONS

        for field_name, defn in FIELD_DEFINITIONS.items():
            status = defn.get("current_status", "")
            assert status != "stage4_future_capture", (
                f"C2E2 field {field_name!r} has current_status='stage4_future_capture'. "
                "Stage 4 fields must not appear in the C2E2 field reference."
            )

    def test_c2e2_popup_rendering_tests_still_exist(self) -> None:
        """Regression guard: C2E2 popup rendering test file must exist.

        If someone deletes or moves the C2E2 popup rendering tests, this
        guard fires to prevent the safety net from silently disappearing.
        """
        popup_test = REPO_ROOT / "tests" / "test_c2e2_popup_rendering.py"
        assert popup_test.exists(), (
            "tests/test_c2e2_popup_rendering.py is missing. "
            "This file protects C2E2 popup truthfulness. Do not delete it."
        )
        content = popup_test.read_text(encoding="utf-8")
        assert len(content) > 200, (
            "tests/test_c2e2_popup_rendering.py appears to have been emptied."
        )


# ---------------------------------------------------------------------------
# Field reference source vocabulary guard
# ---------------------------------------------------------------------------


class TestFieldReferenceLeakage:
    """field_reference.py source vocabulary must not contain Stage 4 sources yet.

    Once VLD-3 is fixed, this test will need updating — but only the
    test_structured_capture_not_in_live_source_labels check should change,
    and only after Codex explicitly registers it as part of VLD-3 fix.
    """

    def test_live_field_source_labels_are_known_set(self) -> None:
        """Only survey, derived, trimble_attr are current live source labels."""
        from app.field_reference import FIELD_DEFINITIONS

        all_sources = {
            defn.get("source") for defn in FIELD_DEFINITIONS.values() if defn.get("source")
        }
        known_live_sources = {"survey", "derived", "trimble_attr"}
        unknown_sources = all_sources - known_live_sources - {"structured_capture"}

        assert not unknown_sources, (
            f"Unknown source labels in field_reference: {sorted(unknown_sources)}. "
            "Only survey, derived, and trimble_attr are currently valid live sources. "
            "structured_capture is pending VLD-3 registration."
        )

    def test_structured_capture_not_in_live_source_labels(self) -> None:
        """'structured_capture' must not yet appear in field_reference.

        This test guards against premature VLD-3 'registration' that adds
        structured_capture to the live C2E2 popup fields rather than merely
        registering the source label. It will need updating when VLD-3 is
        legitimately fixed — the fix must only add the source label, not
        add Stage 4 fields to the popup.

        NOTE: If Codex fixes VLD-3 correctly (source label registration only,
        no popup field additions), update this test to allow structured_capture
        in the source vocabulary while keeping the popup leakage guards above.
        """
        from app.field_reference import FIELD_DEFINITIONS

        for field_name, defn in FIELD_DEFINITIONS.items():
            assert defn.get("source") != "structured_capture", (
                f"field_reference field {field_name!r} has source='structured_capture'. "
                "This is unexpected — existing C2E2 fields are survey/derived/trimble_attr. "
                "If registering the structured_capture source label, do not change "
                "existing field source values."
            )


# ---------------------------------------------------------------------------
# Review OS leakage guard
# ---------------------------------------------------------------------------


class TestReviewOSLeakage:
    """Review OS template and routes must not reference Stage 4 structured capture."""

    REVIEW_TEMPLATES_DIR = REPO_ROOT / "templates"

    def test_review_templates_have_no_structured_capture(self) -> None:
        templates_dir = self.REVIEW_TEMPLATES_DIR
        if not templates_dir.exists():
            pytest.skip("templates directory not found")

        for template_path in templates_dir.rglob("*.html"):
            content = _read(template_path)
            assert "structured_capture" not in content.lower(), (
                f"Template {template_path.relative_to(REPO_ROOT)} references "
                "'structured_capture'. Stage 4 must not appear in HTML templates "
                "before Stage 4D."
            )
            assert "stage4_future_capture" not in content.lower(), (
                f"Template {template_path.relative_to(REPO_ROOT)} contains "
                "'stage4_future_capture' status token."
            )
