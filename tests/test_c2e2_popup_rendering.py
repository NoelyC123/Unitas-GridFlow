"""Frontend rendering checks for C2E2 reality-based support popups."""

from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_JS = REPO_ROOT / "app/static/js/map-viewer.js"

NODE_UNAVAILABLE = pytest.mark.skipif(shutil.which("node") is None, reason="node is required")


def _run_node(script: str) -> None:
    subprocess.run(
        ["node", "-e", script],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def _viewer_harness(extra_js: str) -> str:
    return textwrap.dedent(
        f"""
        const fs = require('fs');
        const vm = require('vm');
        const source = fs.readFileSync({str(MAP_JS)!r}, 'utf8')
          + '\\nglobalThis.__MapViewer = MapViewer;';
        const context = {{
          console,
          localStorage: {{ getItem: () => null, setItem: () => {{}} }},
          document: {{
            querySelector: () => ({{ content: 'JOB' }}),
            getElementById: () => null,
            addEventListener: () => {{}},
            querySelectorAll: () => [],
          }},
          L: {{}},
        }};
        vm.runInNewContext(source, context);
        const viewer = new context.__MapViewer();
        function assert(condition, message) {{
          if (!condition) throw new Error(message);
        }}
        function assertIncludes(haystack, needle) {{
          assert(haystack.includes(needle), `Expected popup HTML to include: ${{needle}}`);
        }}
        function assertExcludes(haystack, needle) {{
          assert(!haystack.includes(needle), `Popup HTML should not include: ${{needle}}`);
        }}
        {extra_js}
        """
    )


@NODE_UNAVAILABLE
def test_c2e2_support_popup_groups_and_truthful_missing_wording() -> None:
    _run_node(
        _viewer_harness(
            """
            const props = {
              id: '42',
              pole_id: '42',
              structure_type: 'Pol',
              asset_intent: 'existing_support',
              record_role: 'structural',
              easting: 300000,
              northing: 400000,
              height: null,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
              name: null,
              material: null,
              relationship: null,
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.1, -3.1);

            for (const title of [
              'Identity and role',
              'Geometry and measured evidence',
              'QA and review status',
              'Survey context',
              'Lifecycle / relationships',
            ]) {
              assertIncludes(html, title);
            }

            assertIncludes(html, 'Point ID');
            assertIncludes(html, 'Feature Code');
            assertIncludes(html, 'Asset Intent');
            assertIncludes(html, 'Record Role');
            assertIncludes(html, 'Easting');
            assertIncludes(html, 'Northing');
            assertIncludes(html, 'Measured Height');
            assertIncludes(html, 'Not measured (intermediate pole)');
            assertIncludes(html, 'Survey Note');
            assertIncludes(html, 'Material');
            assertIncludes(html, 'Not recorded in survey');
            assertIncludes(html, 'Relationship');
            """
        )
    )


@NODE_UNAVAILABLE
def test_c2e2_height_wording_distinguishes_expole_angle_and_captured_height() -> None:
    _run_node(
        _viewer_harness(
            """
            const base = {
              id: '29',
              pole_id: '29',
              asset_intent: 'existing_support',
              record_role: 'structural',
              easting: 365155.028,
              northing: 643657.644,
              qa_status: 'WARN',
              issue_count: 0,
              warn_count: 1,
              material: null,
            };

            const exHtml = viewer.buildPopupHtml(
              { ...base, structure_type: 'EXpole', height: null },
              'WARN',
              54.1,
              -3.1,
            );
            assertIncludes(exHtml, 'Not measured — check survey notes');

            const angleHtml = viewer.buildPopupHtml(
              { ...base, structure_type: 'Angle', height: null },
              'WARN',
              54.1,
              -3.1,
            );
            assertIncludes(angleHtml, 'Not measured — check survey notes');

            const capturedHtml = viewer.buildPopupHtml(
              { ...base, structure_type: 'EXpole', height: 9.2 },
              'PASS',
              54.1,
              -3.1,
            );
            assertIncludes(capturedHtml, '9.2m');
            assertExcludes(capturedHtml, 'Not measured — check survey notes');
            """
        )
    )


@NODE_UNAVAILABLE
def test_c2e2_support_popup_does_not_render_theoretical_absent_fields() -> None:
    _run_node(
        _viewer_harness(
            """
            const props = {
              id: '50',
              pole_id: '50',
              structure_type: 'EXpole',
              asset_intent: 'existing_support',
              record_role: 'structural',
              easting: 301000,
              northing: 401000,
              height: 8.8,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
              pole_class: 'Medium',
              voltage_carried: '11kV',
              conductor_type: 'ABC',
              condition: 'Good',
              defect_type: 'split',
              equipment_type: 'transformer',
              lean_direction: 'north',
              stay_type: 'box',
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.1, -3.1);

            for (const forbidden of [
              'Pole Class',
              'Voltage Carried',
              'Conductor Type',
              'Condition',
              'Defects',
              'Equipment Type',
              'Lean',
              'Stay Type',
            ]) {
              assertExcludes(html, forbidden);
            }
            """
        )
    )


@NODE_UNAVAILABLE
def test_c2e2_support_popup_omits_unavailable_export_fields() -> None:
    _run_node(
        _viewer_harness(
            """
            const props = {
              id: '77',
              pole_id: '77',
              structure_type: 'EXpole',
              asset_intent: 'existing_support',
              record_role: 'structural',
              easting: 305000,
              northing: 405000,
              height: 9.5,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
              // Fields the current Trimble export does not provide. The
              // C2E2 popup must NOT render any of these — neither as a
              // value nor as a "MISSING" / "not recorded" placeholder.
              from_support_id: 'A',
              to_support_id: 'B',
              parent_pole_id: 'P1',
              parent_structure_id: 'S1',
              cable_from_asset_id: 'CF',
              cable_to_asset_id: 'CT',
              survey_job_ref: 'J123',
              surveyor: 'Jane',
              survey_date: '2026-01-01',
              equipment_used: 'TrimbleR12',
              survey_limitations: 'overhead canopy',
              gnss_accuracy: '0.05m H, 0.1m V',
              gnss_accuracy_summary: '0.05m / 0.1m',
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.1, -3.1);

            // Whole sections that must be absent.
            for (const sectionTitle of [
              'Network links',
              'Survey metadata',
              'Lifecycle / Design',
            ]) {
              assertExcludes(html, sectionTitle);
            }

            // Specific row labels that must be absent everywhere in the popup.
            for (const forbidden of [
              'From support',
              'To support',
              'Parent pole',
              'Parent structure',
              'Cable from asset',
              'Cable to asset',
              'Job / scheme ref',
              'Surveyor',
              'Surveyed By',
              'Survey date',
              'Survey Date',
              'Survey equipment',
              'Survey limitations',
              'GNSS / accuracy',
              'GNSS Accuracy',
            ]) {
              assertExcludes(html, forbidden);
            }

            // The "MISSING" / "not recorded" placeholder strings these
            // fields normally render must not appear either.
            for (const placeholder of [
              'not recorded in export',
              'not recorded - positional confidence unknown',
              'not recorded in current export',
            ]) {
              assertExcludes(html, placeholder);
            }
            """
        )
    )


@NODE_UNAVAILABLE
def test_c2e2_support_popup_skips_elevation_when_missing_and_renders_when_captured() -> None:
    _run_node(
        _viewer_harness(
            """
            const base = {
              id: '88',
              pole_id: '88',
              structure_type: 'EXpole',
              asset_intent: 'existing_support',
              record_role: 'structural',
              easting: 306000,
              northing: 406000,
              height: 9.0,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
            };

            const missing = viewer.buildPopupHtml(
              { ...base, elevation: null },
              'PASS',
              54.2,
              -3.2,
            );
            assertExcludes(missing, 'Elevation');

            const empty = viewer.buildPopupHtml(
              { ...base, elevation: '' },
              'PASS',
              54.2,
              -3.2,
            );
            assertExcludes(empty, 'Elevation');

            const present = viewer.buildPopupHtml(
              { ...base, elevation: 24.5 },
              'PASS',
              54.2,
              -3.2,
            );
            assertIncludes(present, 'Elevation');
            assertIncludes(present, '24.5m');
            """
        )
    )


@NODE_UNAVAILABLE
def test_c2e2_support_popup_keeps_truthful_sections() -> None:
    _run_node(
        _viewer_harness(
            """
            const props = {
              id: '99',
              pole_id: '99',
              structure_type: 'Pol',
              asset_intent: 'existing_support',
              record_role: 'structural',
              easting: 307000,
              northing: 407000,
              height: null,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
              material: null,
              source_confidence_detail: {
                provenance: 'field_observed_rtk',
                confidence: 'high',
                geometry_trust: 'high',
              },
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.3, -3.3);

            for (const kept of [
              'Identity and role',
              'Geometry and measured evidence',
              'QA and review status',
              'Survey context',
              'Lifecycle / relationships',
              'Location',
              // The section title contains an ampersand which is
              // HTML-escaped in the rendered output.
              'Source &amp; Confidence',
            ]) {
              assertIncludes(html, kept);
            }

            // Truthful height wording for an intermediate pole.
            assertIncludes(html, 'Not measured (intermediate pole)');
            // Truthful material wording.
            assertIncludes(html, 'Not recorded in survey');
            """
        )
    )


def test_c2e2_static_methods_and_navigation_hooks_remain_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")

    for method in [
        "usesC2E2SupportPopup",
        "c2e2SupportPopupSections",
        "c2e2FieldLabels",
        "c2e2MissingWording",
        "buildReviewNavigationTargets",
        "focusReviewTarget",
        "focusNextReviewTarget",
        "focusPreviousReviewTarget",
        "togglePlannerAwarenessLayer",
        "clearCurrentReviewTargetSpan",
        "releaseReviewNavigationMap",
        "handleSpanPopupClose",
    ]:
        assert method in js

    assert "Not measured (intermediate pole)" in js
    assert "Not measured — check survey notes" in js
    assert "Not recorded in survey" in js
