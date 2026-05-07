"""Frontend route-highlight interaction checks for C2D map spans."""

from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_JS = REPO_ROOT / "app/static/js/map-viewer.js"
MAP_CSS = REPO_ROOT / "app/static/css/map-viewer.css"


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
          }},
          L: {{}},
        }};
        vm.runInNewContext(source, context);
        const viewer = new context.__MapViewer();
        function assert(condition, message) {{
          if (!condition) throw new Error(message);
        }}
        function fakeLine() {{
          const classState = new Set();
          return {{
            styles: [],
            frontCount: 0,
            classState,
            setStyle(style) {{ this.styles.push(style); }},
            getElement() {{
              return {{
                classList: {{
                  toggle: (cls, on) => on ? classState.add(cls) : classState.delete(cls),
                }},
              }};
            }},
            bringToFront() {{ this.frontCount += 1; }},
          }};
        }}
        function ref(from, to) {{
          return {{
            props: {{ from_point_id: from, to_point_id: to }},
            line: fakeLine(),
            routeGroupIndex: null,
          }};
        }}
        {extra_js}
        """
    )


@NODE_UNAVAILABLE
def test_route_grouping_uses_endpoint_continuity() -> None:
    _run_node(
        _viewer_harness(
            """
            const refs = [ref('A', 'B'), ref('B', 'C'), ref('X', 'Y'), ref('C', 'D')];
            viewer._spanLineRefs = refs;
            viewer.initialiseSpanRouteGroups();
            assert(viewer._spanRouteGroups.length === 2, 'expected two continuous route groups');
            const sizes = viewer._spanRouteGroups.map((group) => group.length).sort();
            assert(JSON.stringify(sizes) === JSON.stringify([1, 3]), 'unexpected group sizes');
            assert(refs[0].routeGroupIndex === refs[1].routeGroupIndex, 'A-B and B-C should group');
            assert(refs[1].routeGroupIndex === refs[3].routeGroupIndex, 'B-C and C-D should group');
            assert(refs[2].routeGroupIndex !== refs[0].routeGroupIndex, 'X-Y should be separate');
            """
        )
    )


@NODE_UNAVAILABLE
def test_route_highlight_toggle_and_switching_logic() -> None:
    _run_node(
        _viewer_harness(
            """
            const refs = [ref('A', 'B'), ref('B', 'C'), ref('X', 'Y')];
            viewer._spanLineRefs = refs;
            viewer.initialiseSpanRouteGroups();

            viewer.toggleSpanRouteHighlight(refs[0]);
            assert(viewer._activeRouteGroupIndex === refs[0].routeGroupIndex, 'first route active');
            assert(refs[0].line.classState.has('gf-route-highlight'), 'first span highlighted');
            assert(refs[1].line.classState.has('gf-route-highlight'), 'connected span highlighted');
            assert(!refs[2].line.classState.has('gf-route-highlight'), 'other route plain');
            assert(refs[2].line.styles.at(-1).opacity === 0.24, 'non-selected span dimmed');

            viewer.toggleSpanRouteHighlight(refs[0]);
            assert(viewer._activeRouteGroupIndex === null, 'second click clears highlight');
            assert(!refs[0].line.classState.has('gf-route-highlight'), 'highlight class removed');

            viewer.toggleSpanRouteHighlight(refs[2]);
            assert(viewer._activeRouteGroupIndex === refs[2].routeGroupIndex, 'new route active');
            assert(refs[2].line.classState.has('gf-route-highlight'), 'new route highlighted');
            assert(!refs[0].line.classState.has('gf-route-highlight'), 'old route plain');
            """
        )
    )


def test_route_highlight_click_binding_and_css_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    css = MAP_CSS.read_text(encoding="utf-8")

    assert "line.on('click', () => this.toggleSpanRouteHighlight(ref));" in js
    assert "buildSpanRouteGroups" in js
    assert "initialiseSpanRouteGroups" in js
    assert ".gf-route-highlight" in css
