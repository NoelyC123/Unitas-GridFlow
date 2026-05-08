"""Frontend Review Intelligence navigation layer checks."""

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
            add(cls) {{ classes.add(cls); }},
            remove(cls) {{ classes.delete(cls); }},
            toggle(cls, on) {{ on ? classes.add(cls) : classes.delete(cls); }},
          }};
        }}
        function fakeLine() {{
          const classList = fakeClassList();
          return {{
            styles: [],
            popupOpened: false,
            bounds: 'bounds',
            classList,
            setStyle(style) {{ this.styles.push(style); }},
            getBounds() {{ return this.bounds; }},
            openPopup() {{ this.popupOpened = true; }},
            bringToFront() {{ this.front = true; }},
            getElement() {{ return {{ classList }}; }},
          }};
        }}
        function fakeMarker() {{
          const classList = fakeClassList();
          return {{
            popupOpened: false,
            classList,
            getLatLng() {{ return [54.1, -3.1]; }},
            openPopup() {{ this.popupOpened = true; }},
            getElement() {{ return {{ classList }}; }},
          }};
        }}
        {extra_js}
        """
    )


def test_review_navigation_static_wiring_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    css = MAP_CSS.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")

    for method in [
        "buildReviewNavigationTargets",
        "focusReviewTarget",
        "focusNextReviewTarget",
        "focusPreviousReviewTarget",
    ]:
        assert method in js

    assert 'data-review-nav-group="blockers"' in html
    assert 'data-review-nav-group="review"' in html
    assert 'data-review-nav-group="gaps"' in html
    assert 'data-review-nav-group="awareness"' in html
    assert "review-nav-prev" in html
    assert "review-nav-next" in html
    assert ".gf-review-card-active" in css
    assert ".gf-review-card-disabled" in css
    assert ".gf-review-nav-controls" in css
    assert "togglePlannerAwarenessLayer" in js
    assert "this.togglePlannerAwarenessLayer(input.checked)" in js
    assert "Design blockers (" not in html
    assert "_reviewNavigationTargets?.blockers?.length" in js
    assert "smartPopupOffsetForLayer" in js
    assert "bindSmartPopup(line, this.buildSpanPopupHtml(props)" in js
    assert "autoPanPaddingTopLeft" in js
    assert "popup.options.offset = this.smartPopupOffsetForLayer(layer)" in js
    assert "#00a3ff" in css
    assert "stroke-width: 9 !important" in css
    assert "max-height: min(52vh, 430px)" in html


@NODE_UNAVAILABLE
def test_build_review_navigation_targets_and_empty_groups_are_safe() -> None:
    _run_node(
        _viewer_harness(
            """
            const blockerRef = {
              props: {
                from_point_id: 'A',
                to_point_id: 'B',
                span_validity: 'invalid',
                distance_m: 2.5,
              },
              line: fakeLine(),
              routeGroupIndex: 0,
            };
            const reviewRef = {
              props: { from_point_id: 'B', to_point_id: 'C', crossing_risk_level: 'medium' },
              line: fakeLine(),
              routeGroupIndex: 0,
            };
            const gapRef = {
              props: { from_point_id: 'C', to_point_id: 'D', missing_fields: ['conductor'] },
              line: fakeLine(),
              routeGroupIndex: 0,
            };
            viewer._spanLineRefs = [blockerRef, reviewRef, gapRef];
            viewer._plannerAwarenessItems = [
              { id: 'aw_1', related_span_id: 'B->C', severity: 'REVIEW', message: 'Access note' },
            ];
            viewer._awarenessMarkerRefs = [
              { item: viewer._plannerAwarenessItems[0], marker: fakeMarker(), index: 0 },
            ];

            const targets = viewer.buildReviewNavigationTargets();
            assert(targets.blockers.length === 1, 'one blocker target expected');
            assert(targets.review.length === 2, 'review and linked awareness span expected');
            assert(targets.gaps.length === 1, 'one evidence gap expected');
            assert(targets.awareness.length === 1, 'one awareness target expected');
            assert(targets.awareness[0].spanRef === reviewRef, 'awareness should link to span ref');

            viewer._spanLineRefs = [];
            viewer._awarenessMarkerRefs = [];
            viewer._plannerAwarenessItems = [];
            const empty = viewer.buildReviewNavigationTargets();
            assert(empty.blockers.length === 0, 'empty blockers should be safe');
            viewer.selectReviewNavigationGroup('blockers');
            viewer.focusNextReviewTarget();
            viewer.focusPreviousReviewTarget();
            assert(viewer._activeReviewTargetIndex === -1, 'empty selection index should be -1');
            """
        )
    )


@NODE_UNAVAILABLE
def test_planner_awareness_toggle_reuses_existing_layer_and_marker_refs() -> None:
    _run_node(
        _viewer_harness(
            """
            function fakeLayer() {
              const members = new Set();
              return {
                addCount: 0,
                members,
                addTo(map) { this.addCount += 1; map.layers.add(this); return this; },
                hasLayer(marker) { return members.has(marker); },
              };
            }
            function layerMarker() {
              return {
                addTo(layer) { layer.members.add(this); return this; },
              };
            }
            const layer = fakeLayer();
            const marker = layerMarker();
            const strayMarker = layerMarker();
            layer.members.add(marker);
            viewer.plannerAwarenessLayer = layer;
            viewer._awarenessMarkerRefs = [{ marker }, { marker: strayMarker }];
            viewer.map = {
              layers: new Set([layer, marker, strayMarker]),
              hasLayer(item) { return this.layers.has(item); },
              removeLayer(item) { this.layers.delete(item); },
            };

            viewer.togglePlannerAwarenessLayer(false);
            assert(!viewer.map.layers.has(layer), 'awareness layer should be removed');
            assert(!viewer.map.layers.has(marker), 'marker refs should be removed defensively');
            assert(!viewer.map.layers.has(strayMarker), 'stray marker refs should be removed');

            viewer.togglePlannerAwarenessLayer(true);
            assert(viewer.map.layers.has(layer), 'awareness layer should be restored');
            assert(layer.members.has(marker), 'existing marker should remain in layer group');
            assert(layer.members.has(strayMarker), 'missing marker should be restored to group');
            """
        )
    )


@NODE_UNAVAILABLE
def test_focus_review_target_reuses_route_highlight_and_opens_popups() -> None:
    _run_node(
        _viewer_harness(
            """
            const line = fakeLine();
            const ref = {
              props: {
                from_point_id: 'A',
                to_point_id: 'B',
                span_validity: 'invalid',
                distance_m: 2.5,
              },
              line,
              routeGroupIndex: 0,
            };
            const marker = fakeMarker();
            viewer._spanLineRefs = [ref];
            viewer._spanRouteGroups = [[ref]];
            viewer.map = {
              fitBoundsArg: null,
              setViewArg: null,
              zoom: 13,
              fitBounds(bounds) { this.fitBoundsArg = bounds; },
              setView(latLng, zoom) { this.setViewArg = [latLng, zoom]; },
              getZoom() { return this.zoom; },
            };

            viewer.focusReviewTarget({ type: 'span', spanIndex: 0, spanRef: ref });
            assert(viewer.map.fitBoundsArg === 'bounds', 'span target should fit bounds');
            assert(viewer._activeRouteGroupIndex === 0, 'span focus should activate route group');
            assert(line.popupOpened, 'span popup should open');
            assert(
              line.classList.classes.has('gf-route-highlight'),
              'route highlight class expected',
            );
            assert(
              line.classList.classes.has('gf-review-target-focused'),
              'focused span class expected',
            );

            viewer.focusReviewTarget({
              type: 'awareness',
              markerRef: { marker, item: { id: 'aw_1' } },
              spanRef: ref,
            });
            assert(marker.popupOpened, 'awareness popup should open');
            assert(viewer.map.setViewArg[1] === 16, 'awareness target should zoom in');
            assert(
              marker.classList.classes.has('gf-review-target-focused'),
              'focused marker class expected',
            );
            """
        )
    )


def test_navigation_reuses_existing_route_highlight_method() -> None:
    js = MAP_JS.read_text(encoding="utf-8")

    assert "ensureSpanRouteHighlighted" in js
    assert "this.toggleSpanRouteHighlight(spanRef)" in js
    assert "L.layerGroup().addLayer" not in js


def test_no_backend_validation_geometry_or_span_generation_files_modified() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    changed = set(result.stdout.splitlines())
    forbidden = {
        "app/span_generator.py",
        "app/geometry_pipeline.py",
        "app/routes/map_preview.py",
    }
    assert not changed.intersection(forbidden)
