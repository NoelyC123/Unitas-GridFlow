"""Frontend Review Intelligence Layer contract tests."""

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
        {extra_js}
        """
    )


@NODE_UNAVAILABLE
def test_classify_span_issues_returns_expected_structure() -> None:
    _run_node(
        _viewer_harness(
            """
            const result = viewer.classifySpanIssues({
              span_validity: 'invalid',
              distance_m: 1.2,
              design_status: 'BLOCKED',
              design_blocker_reasons: [
                { type: 'geometry', severity: 'blocker', message: 'Invalid span distance' },
              ],
            });
            assert(Array.isArray(result.categories), 'categories should be an array');
            assert(result.categories.includes('GEOMETRY'), 'geometry category expected');
            assert(result.severity === 'BLOCKER', 'invalid geometry should block');

            const review = viewer.classifySpanIssues({
              crossing_risk_level: 'medium',
              designer_suggested_actions: [
                'Confirm conductor type and size for sag / tension design on this span.',
              ],
            });
            assert(review.categories.includes('CLEARANCE'), 'clearance category expected');
            assert(review.categories.includes('ELECTRICAL'), 'electrical category expected');
            assert(review.categories.includes('DATA'), 'data gap category expected');
            assert(review.severity === 'REVIEW', 'non-critical signals should need review');
            """
        )
    )


@NODE_UNAVAILABLE
def test_compute_review_summary_counts_mock_spans() -> None:
    _run_node(
        _viewer_harness(
            """
            viewer._plannerAwarenessItems = [
              {
                related_span_id: 'B->C',
                severity: 'REVIEW',
                category: 'access',
                message: 'Access note',
              },
            ];
            const summary = viewer.computeReviewSummary([
              { from_point_id: 'A', to_point_id: 'B', span_validity: 'invalid', distance_m: 2.5 },
              { from_point_id: 'B', to_point_id: 'C', span_validity: 'valid', distance_m: 80 },
              {
                from_point_id: 'C',
                to_point_id: 'D',
                span_validity: 'valid',
                distance_m: 90,
                designer_suggested_actions: [
                  'Confirm phase configuration for electrical loading on this span.',
                ],
              },
              { from_point_id: 'D', to_point_id: 'E', span_validity: 'valid', distance_m: 90 },
            ]);
            assert(summary.blockers === 1, 'one blocker expected');
            assert(summary.review === 2, 'two review spans expected');
            assert(summary.gaps === 1, 'one evidence gap expected');
            assert(summary.verdict === 'NOT READY', 'blockers should make the route not ready');
            """
        )
    )


@NODE_UNAVAILABLE
def test_review_summary_empty_and_missing_fields_are_safe() -> None:
    _run_node(
        _viewer_harness(
            """
            const empty = viewer.computeReviewSummary([]);
            assert(empty.blockers === 0, 'empty blockers should be zero');
            assert(empty.review === 0, 'empty review should be zero');
            assert(empty.gaps === 0, 'empty gaps should be zero');
            assert(empty.verdict === 'PARTIALLY READY', 'empty route should not claim ready');

            const minimal = viewer.classifySpanIssues({});
            assert(Array.isArray(minimal.categories), 'minimal categories should be an array');
            assert(minimal.categories.length === 0, 'minimal span should have no categories');
            assert(minimal.severity === 'INFO', 'minimal span should be informational');
            """
        )
    )


def test_review_intelligence_static_wiring_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    css = MAP_CSS.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")

    assert "classifySpanIssues" in js
    assert "computeReviewSummary" in js
    assert "workspace-gap-count" in html
    assert "workspace-readiness-verdict" in html
    assert ".gf-span-review" in css
    assert ".gf-span-blocker" in css
