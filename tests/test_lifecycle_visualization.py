"""Frontend checks for C2G lifecycle replacement visualization."""

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
CHECKLIST = REPO_ROOT / "validation_checklists/lifecycle_visualization.yml"

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
            classList,
            front: false,
            bringToFront() {{ this.front = true; }},
            getElement() {{ return element; }},
          }};
        }}
        function fakeMarker() {{
          const classList = fakeClassList();
          const element = {{ classList }};
          return {{
            classList,
            getElement() {{ return element; }},
          }};
        }}
        {extra_js}
        """
    )


def test_lifecycle_visualization_static_wiring_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    css = MAP_CSS.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")

    for method in [
        "renderLifecycleRelationshipLayer",
        "buildLifecycleRelationshipConnectors",
        "activateLifecycleFocusMode",
        "clearLifecycleFocusMode",
        "applyLifecycleFocusStyles",
        "getLifecycleFocusTargets",
        "activateReviewFocusMode",
        "clearReviewFocusMode",
        "applyReviewFocusStyles",
        "buildReviewNavigationTargets",
        "focusReviewTarget",
        "focusNextReviewTarget",
        "focusPreviousReviewTarget",
        "releaseReviewNavigationMap",
        "togglePlannerAwarenessLayer",
        "toggleSpanRouteHighlight",
    ]:
        assert method in js

    for marker in [
        'data-lifecycle-focus="replacement-pairs"',
        'data-lifecycle-focus="existing-assets"',
        'data-lifecycle-focus="proposed-assets"',
        "lifecycle-focus-clear",
        "lifecycle relationships",
    ]:
        assert marker in html

    for css_class in [
        ".gf-lifecycle-connector",
        ".gf-lifecycle-existing",
        ".gf-lifecycle-proposed",
        ".gf-lifecycle-pair-highlight",
        ".gf-lifecycle-muted",
    ]:
        assert css_class in css

    for truthful_string in [
        "Not measured (intermediate pole)",
        "Not measured — check survey notes",
        "Not recorded in survey",
    ]:
        assert truthful_string in js

    for checklist_marker in [
        "lifecycle_focus_active",
        "route_highlight_active",
        "c2e2_support_popup_text_contains",
    ]:
        assert checklist_marker in checklist


@NODE_UNAVAILABLE
def test_lifecycle_focus_highlights_replacement_pairs_and_clears() -> None:
    _run_node(
        _viewer_harness(
            """
            const existingMarker = fakeMarker();
            const proposedMarker = fakeMarker();
            const unrelatedMarker = fakeMarker();
            const connectorLine = fakeLine();
            const spanLine = fakeLine();
            const existing = {
              marker: existingMarker,
              props: {
                pole_id: 'E1',
                structure_type: 'EXpole',
                relationship: 'replacement_pair',
              },
            };
            const proposed = {
              marker: proposedMarker,
              props: {
                pole_id: 'P1',
                structure_type: 'Pol',
                asset_intent: 'proposed_support',
                replacing: 'E1',
              },
            };
            const unrelated = {
              marker: unrelatedMarker,
              props: { pole_id: 'X1', structure_type: 'EXpole' },
            };
            viewer.featureData = [existing, proposed, unrelated];
            viewer._lifecycleConnectorRefs = [{
              line: connectorLine,
              existing,
              proposed,
              pairId: 'E1->P1',
              props: proposed.props,
            }];
            viewer._spanLineRefs = [{
              line: spanLine,
              props: { from_point_id: 'E1', to_point_id: 'P1' },
            }];

            const targets = viewer.activateLifecycleFocusMode('replacement-pairs');

            assert(
              viewer.activeLifecycleFocusMode === 'replacement-pairs',
              'lifecycle focus should activate',
            );
            assert(targets.features.length === 2, 'paired supports should be targets');
            assert(
              existingMarker.classList.contains('gf-lifecycle-pair-highlight'),
              'existing support highlighted',
            );
            assert(
              existingMarker.classList.contains('gf-lifecycle-existing'),
              'existing support class added',
            );
            assert(
              proposedMarker.classList.contains('gf-lifecycle-pair-highlight'),
              'proposed support highlighted',
            );
            assert(
              proposedMarker.classList.contains('gf-lifecycle-proposed'),
              'proposed support class added',
            );
            assert(
              unrelatedMarker.classList.contains('gf-lifecycle-muted'),
              'unrelated marker muted',
            );
            assert(
              connectorLine.classList.contains('gf-lifecycle-pair-highlight'),
              'connector highlighted',
            );
            assert(connectorLine.front, 'connector should be brought forward');
            assert(
              spanLine.classList.contains('gf-lifecycle-muted'),
              'route spans muted during lifecycle focus',
            );

            viewer.clearLifecycleFocusMode();
            assert(viewer.activeLifecycleFocusMode === null, 'lifecycle focus should clear');
            assert(
              !existingMarker.classList.contains('gf-lifecycle-pair-highlight'),
              'existing highlight clears',
            );
            assert(
              !connectorLine.classList.contains('gf-lifecycle-pair-highlight'),
              'connector highlight clears',
            );
            assert(!spanLine.classList.contains('gf-lifecycle-muted'), 'span mute clears');
            """
        )
    )


@NODE_UNAVAILABLE
def test_lifecycle_relationship_layer_draws_being_replaced_by_links() -> None:
    _run_node(
        _viewer_harness(
            """
            const createdLines = [];
            const addedLayers = [];
            context.L = {
              layerGroup() {
                return {
                  added: false,
                  clearLayers() {},
                  addTo(map) { this.added = true; map.layers.push(this); },
                };
              },
              polyline(latlngs, options) {
                const line = fakeLine();
                line.latlngs = latlngs;
                line.options = options;
                line.bindPopup = (html) => { line.popupHtml = html; };
                line.on = () => {};
                line.addTo = (layer) => { addedLayers.push(layer); };
                createdLines.push(line);
                return line;
              },
            };
            viewer.map = {
              layers: [],
              removeLayer() {},
            };
            viewer.featureData = [
              {
                lat: 54.1,
                lon: -3.1,
                marker: fakeMarker(),
                props: {
                  pole_id: 'E1',
                  structure_type: 'EXpole',
                  being_replaced_by: 'P1',
                },
              },
              {
                lat: 54.1002,
                lon: -3.1002,
                marker: fakeMarker(),
                props: {
                  pole_id: 'P1',
                  structure_type: 'Pol',
                  asset_intent: 'proposed_support',
                },
              },
            ];

            viewer.renderLifecycleRelationshipLayer();

            assert(
              createdLines.length === 1,
              'one explicit relationship connector should be drawn',
            );
            assert(
              viewer._replacementDrawableLineCount === 1,
              'drawable connector count should update',
            );
            assert(viewer._lifecycleConnectorRefs.length === 1, 'connector refs should be stored');
            assert(
              createdLines[0].options.className === 'gf-lifecycle-connector',
              'connector should carry lifecycle CSS class',
            );
            assert(
              createdLines[0].popupHtml.includes('Existing')
                && createdLines[0].popupHtml.includes('Proposed'),
              'connector popup should describe the pair',
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
              height: 9.2,
              qa_status: 'PASS',
              issue_count: 0,
              warn_count: 0,
              material: null,
              relationship: 'replacement_pair',
              being_replaced_by: '51',
              pole_class: 'Medium',
              circuit_id: 'CIR-01',
              year_installed: '1975',
              cable_from_asset_id: 'C-A',
              cable_to_asset_id: 'C-B',
              equipment_categories: ['transformer'],
            };
            const html = viewer.buildPopupHtml(props, 'PASS', 54.1, -3.1);

            for (const expected of [
              '9.2m',
              'Not recorded in survey',
              'Lifecycle / relationships',
              'Relationship',
              'Being Replaced By',
            ]) {
              assert(html.includes(expected), `Expected popup HTML to include ${expected}`);
            }

            for (const forbidden of [
              'height is missing survey evidence',
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
