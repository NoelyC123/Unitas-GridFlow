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
            assertExcludes(html, 'Lifecycle / relationships');
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
              {
                ...base,
                structure_type: 'EXpole',
                height: 9.2,
                height_source: 'legacy map data',
                source_confidence_detail: {
                  confidence: 'low',
                  provenance: 'legacy_map_data',
                },
              },
              'PASS',
              54.1,
              -3.1,
            );
            assertIncludes(capturedHtml, '9.2m');
            assertIncludes(
              capturedHtml,
              [
                'Height source: legacy map data',
                'field verification required before clearance calculations',
              ].join(' — '),
            );
            assertExcludes(capturedHtml, 'Not measured — check survey notes');
            assertExcludes(capturedHtml, 'Existing pole height is missing survey evidence');
            assertExcludes(capturedHtml, 'height is missing survey evidence');
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
              circuit_id: 'CIR-01',
              year_installed: '1975',
              equipment_categories: ['transformer'],
              equipment_primary_category: 'transformer',
              from_support_id: '29',
              to_support_id: '30',
              parent_support_id: '28',
              parent_structure_id: 'S-1',
              cable_from_asset_id: 'C-A',
              cable_to_asset_id: 'C-B',
              gnss_accuracy: '1m',
              elevation: 123.4,
              match_offset_m: 4.2,
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.1, -3.1);

            for (const forbidden of [
              'Pole Class',
              'Circuit ID',
              'Year Installed',
              'Equipment & pole-top',
              'Network links',
              'Cable from asset',
              'Cable to asset',
              'Parent pole',
              'Parent structure',
              'GNSS Accuracy',
              'Elevation',
              'Match Offset',
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
