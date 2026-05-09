"""Frontend checks for C2F review focus mode."""

from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_JS = REPO_ROOT / "app/static/js/map-viewer.js"
MAP_CSS = REPO_ROOT / "app/static/css/map-viewer.css"
MAP_HTML = REPO_ROOT / "app/templates/map_viewer.html"

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
        function fakeClassList() {{
          const classes = new Set();
          return {{
            classes,
            add(...names) {{ names.forEach((cls) => classes.add(cls)); }},
            remove(...names) {{ names.forEach((cls) => classes.delete(cls)); }},
            toggle(cls, on) {{
              if (on === undefined) {{
                classes.has(cls) ? classes.delete(cls) : classes.add(cls);
                return classes.has(cls);
              }}
              on ? classes.add(cls) : classes.delete(cls);
              return Boolean(on);
            }},
            contains(cls) {{ return classes.has(cls); }},
          }};
        }}
        function fakeLine() {{
          const classList = fakeClassList();
          const element = {{ classList }};
          return {{
            popupOpened: false,
            bounds: 'bounds',
            classList,
            setStyle() {{}},
            getBounds() {{ return this.bounds; }},
            openPopup() {{ this.popupOpened = true; }},
            bringToFront() {{ this.front = true; }},
            getElement() {{ return element; }},
          }};
        }}
        function fakeMarker() {{
          const classList = fakeClassList();
          const element = {{ classList }};
          return {{
            popupOpened: false,
            classList,
            getLatLng() {{ return [54.1, -3.1]; }},
            openPopup() {{ this.popupOpened = true; }},
            getElement() {{ return element; }},
          }};
        }}
        {extra_js}
        """
    )


def test_review_focus_static_wiring_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    css = MAP_CSS.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")

    for method in [
        "activateReviewFocusMode",
        "clearReviewFocusMode",
        "applyReviewFocusStyles",
        "getFocusTargetsForCategory",
        "buildReviewNavigationTargets",
        "focusReviewTarget",
        "focusNextReviewTarget",
        "focusPreviousReviewTarget",
        "releaseReviewNavigationMap",
        "togglePlannerAwarenessLayer",
    ]:
        assert method in js

    assert "activeFocusMode" in js
    assert "activeFocusCategory" in js
    assert "activeFocusTargetIds" in js
    assert 'data-review-focus-category="blockers"' in html
    assert 'data-review-focus-category="review"' in html
    assert 'data-review-focus-category="gaps"' in html
    assert 'data-review-focus-category="awareness"' in html
    assert "review-focus-clear" in html

    for css_class in [
        ".gf-focus-active",
        ".gf-focus-muted",
        ".gf-focus-target",
        ".gf-focus-current-target",
        ".gf-focus-awareness",
        ".gf-focus-clear-button",
    ]:
        assert css_class in css

    for truthful_string in [
        "Not measured (intermediate pole)",
        "Not measured — check survey notes",
        "Not recorded in survey",
    ]:
        assert truthful_string in js


@NODE_UNAVAILABLE
def test_review_focus_mode_dims_irrelevant_targets_and_cycles_with_navigation() -> None:
    _run_node(
        _viewer_harness(
            """
            const blockerLine = fakeLine();
            const reviewLine = fakeLine();
            const blockerRef = {
              props: {
                from_point_id: 'A',
                to_point_id: 'B',
                span_validity: 'invalid',
                distance_m: 2.5,
              },
              line: blockerLine,
              routeGroupIndex: 0,
            };
            const reviewRef = {
              props: {
                from_point_id: 'C',
                to_point_id: 'D',
                crossing_risk_level: 'medium',
                distance_m: 120,
              },
              line: reviewLine,
              routeGroupIndex: 1,
            };
            const targetMarker = fakeMarker();
            const mutedMarker = fakeMarker();
            viewer.mapEl = { classList: fakeClassList() };
            viewer.map = {
              fitBoundsArg: null,
              fitBounds(bounds) { this.fitBoundsArg = bounds; },
              hasLayer() { return true; },
            };
            viewer._spanLineRefs = [blockerRef, reviewRef];
            viewer._spanRouteGroups = [[blockerRef], [reviewRef]];
            viewer.featureData = [
              { marker: targetMarker, props: { pole_id: 'A' } },
              { marker: mutedMarker, props: { pole_id: 'X' } },
            ];

            viewer.activateReviewFocusMode('blockers');

            assert(viewer.activeFocusMode === 'review', 'review focus mode should be active');
            assert(viewer.activeFocusCategory === 'blockers', 'blocker focus should be active');
            assert(viewer.activeFocusTargetIds.length === 1, 'focus target ids should be recorded');
            assert(
              blockerLine.classList.contains('gf-focus-target'),
              'blocker span should be targeted',
            );
            assert(
              blockerLine.classList.contains('gf-focus-current-target'),
              'current target should be highlighted',
            );
            assert(
              reviewLine.classList.contains('gf-focus-muted'),
              'unrelated span should be muted',
            );
            assert(
              targetMarker.classList.contains('gf-focus-target'),
              'linked endpoint marker should be targeted',
            );
            assert(
              mutedMarker.classList.contains('gf-focus-muted'),
              'unrelated marker should be muted',
            );
            assert(blockerLine.popupOpened, 'focused blocker popup should open');

            viewer.focusNextReviewTarget();
            assert(
              viewer._activeReviewTargetIndex === 0,
              'single target next should wrap to itself',
            );

            viewer.clearReviewFocusMode();
            assert(viewer.activeFocusCategory === null, 'focus category should clear');
            assert(!blockerLine.classList.contains('gf-focus-target'), 'target class should clear');
            assert(!reviewLine.classList.contains('gf-focus-muted'), 'muted class should clear');
            assert(
              !targetMarker.classList.contains('gf-focus-target'),
              'marker target class should clear',
            );
          """
        )
    )


@NODE_UNAVAILABLE
def test_c2e2_popup_truthfulness_and_unavailable_fields_remain_protected() -> None:
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
              height: null,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
              material: null,
              pole_class: 'Medium',
              circuit_id: 'CIR-01',
              year_installed: '1975',
              cable_from_asset_id: 'C-A',
              cable_to_asset_id: 'C-B',
              equipment_categories: ['transformer'],
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.1, -3.1);

            for (const expected of [
              'Not measured — check survey notes',
              'Not recorded in survey',
            ]) {
              assert(html.includes(expected), `Expected popup HTML to include ${expected}`);
            }

            for (const forbidden of [
              'Pole Class',
              'Circuit ID',
              'Year Installed',
              'Equipment & pole-top',
              'Network links',
              'Cable from asset',
              'Cable to asset',
            ]) {
              assert(!html.includes(forbidden), `Popup HTML should not include ${forbidden}`);
            }
          """
        )
    )
