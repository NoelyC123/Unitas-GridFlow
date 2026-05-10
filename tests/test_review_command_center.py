"""Frontend checks for the Review Workspace command center."""

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
            getBounds() {{ return {{ getCenter() {{ return [54.1, -3.1]; }} }}; }},
            openPopup() {{ this.popupOpened = true; }},
            bringToFront() {{ this.front = true; }},
            setStyle(style) {{ this.style = style; }},
            getElement() {{ return element; }},
          }};
        }}
        function fakeMarker() {{
          const classList = fakeClassList();
          const element = {{ classList }};
          return {{
            getLatLng() {{ return [54.1, -3.1]; }},
            openPopup() {{ this.popupOpened = true; }},
            getElement() {{ return element; }},
          }};
        }}
        {extra_js}
        """
    )


def test_review_command_center_static_surface_present() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    css = MAP_CSS.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")

    for text in [
        "Design-readiness command center",
        "Review queue",
        "Design Blockers",
        "Review Required",
        "Evidence Gaps",
        "Planner Awareness",
        "Route / Span Checks",
        "Lifecycle / Replacement Checks",
        "Evidence quality",
        "Review operating system",
        "Active issue queue",
        "Unresolved only",
    ]:
        assert text in html

    for element_id in [
        "review-decision-banner",
        "review-total-records",
        "review-mapped-records",
        "review-route-issue-count",
        "review-measured-height-count",
        "review-missing-height-count",
        "review-material-missing-count",
        "review-low-confidence-count",
        "review-readiness-score",
        "review-progress-count",
        "review-remaining-blockers",
        "review-active-issue-queue",
        "review-filter-unresolved",
    ]:
        assert element_id in html

    assert 'data-review-nav-group="route"' in html
    assert 'data-review-command-action="lifecycle"' in html
    for filter_name in ["severity", "category", "lifecycle", "evidence", "confidence", "route"]:
        assert f'data-review-filter="{filter_name}"' in html

    for css_class in [
        ".gf-review-decision-banner",
        ".gf-review-queue",
        ".gf-review-queue-item",
        ".gf-evidence-quality",
        ".gf-review-os-panel",
        ".gf-review-filter-grid",
        ".gf-active-issue-item",
        ".gf-review-risk-high",
        ".gf-review-risk-medium",
        ".gf-review-risk-muted",
        ".severity-blocker",
        ".severity-review",
        ".severity-info",
        ".severity-pass",
    ]:
        assert css_class in css

    for method in [
        "computeReviewCommandCenterState",
        "renderReviewCommandCenter",
        "severityLabel",
        "severityClass",
        "designReadinessDecision",
        "routeReviewTargets",
        "lifecycleReviewTargets",
        "computeReviewOperatingSystemState",
        "buildReviewIssueModel",
        "matchesReviewOpsFilters",
        "markCurrentReviewIssueReviewed",
        "applyReviewOperatingSystemOverlays",
        "jumpToReviewIssue",
    ]:
        assert method in js

    for label in [
        "Ready for design review",
        "Partially ready — review required",
        "Blocked — field evidence needed",
        "Legacy/low-confidence data — verify before design",
    ]:
        assert label in js


@NODE_UNAVAILABLE
def test_review_command_center_uses_existing_map_signals_only() -> None:
    _run_node(
        _viewer_harness(
            """
            viewer._mapMeta = { pole_count: 4 };
            viewer.featureData = [
              {
                marker: fakeMarker(),
                props: {
                  id: 'EX1',
                  pole_id: 'EX1',
                  structure_type: 'EXpole',
                  asset_intent: 'existing',
                  height: '9.2',
                  material: '',
                },
              },
              {
                marker: fakeMarker(),
                props: {
                  id: 'PR1',
                  pole_id: 'PR1',
                  structure_type: 'PRpole',
                  asset_intent: 'proposed',
                  material: 'wood',
                  relationship: 'replacement_pair',
                  replacing: 'EX1',
                },
              },
            ];
            viewer._spanLineRefs = [
              {
                props: {
                  from_point_id: 'EX1',
                  to_point_id: 'PR1',
                  span_validity: 'invalid',
                  distance_m: 2.5,
                },
                line: fakeLine(),
                routeGroupIndex: 0,
              },
              {
                props: { from_point_id: 'PR1', to_point_id: 'P2', crossing_risk_level: 'medium' },
                line: fakeLine(),
                routeGroupIndex: 0,
              },
              {
                props: { from_point_id: 'P2', to_point_id: 'P3', missing_fields: ['height'] },
                line: fakeLine(),
                routeGroupIndex: 0,
              },
            ];
            viewer._awarenessMarkerRefs = [
              {
                item: {
                  id: 'aw1',
                  related_span_id: 'PR1->P2',
                  severity: 'INFO',
                  message: 'Check access',
                },
                marker: fakeMarker(),
              },
            ];
            viewer._reviewNavigationTargets = viewer.buildReviewNavigationTargets();

            const state = viewer.computeReviewCommandCenterState();
            assert(state.totalRecords === 4, 'metadata total should be used');
            assert(state.mappedRecords === 2, 'mapped feature count should be used');
            assert(state.queue.blockers === 1, 'blocker span should be counted');
            assert(state.queue.review >= 1, 'review spans should be counted');
            assert(state.queue.gaps === 1, 'evidence gap should be counted');
            assert(state.queue.awareness === 1, 'planner awareness should be counted');
            assert(
              state.queue.route === 2,
              'route checks should count geometry and clearance spans',
            );
            assert(state.queue.lifecycle === 1, 'replacement relationship should be counted');
            assert(state.evidence.measuredHeights === 1, 'measured height should be counted');
            assert(state.evidence.missingHeights === 1, 'missing support height should be counted');
            assert(state.evidence.missingMaterials === 1, 'missing material should be counted');
            assert(
              state.readiness.label === 'Blocked — field evidence needed',
              'blocker verdict expected',
            );
            assert(
              viewer.severityLabel('pass') === 'PASS',
              'PASS severity label should be supported',
            );
            assert(
              viewer.severityClass('warning') === 'severity-warning',
              'WARNING severity class should be supported',
            );
            assert(state.ops.total >= 3, 'operating issue model should aggregate targets');
            assert(
              state.ops.filteredIssues.length === state.ops.total,
              'default filters show all issues',
            );
            assert(state.ops.remainingBlockers === 1, 'remaining blocker should be counted');
            assert(state.ops.readinessScore < 100, 'open review issues reduce readiness score');
            assert(
              state.ops.breakdowns.severity.BLOCKER === 1,
              'severity breakdown should count blockers',
            );
            assert(
              state.ops.breakdowns.lifecycleRisk.replacement === 1,
              'lifecycle risk should count pairs',
            );
            """
        )
    )


@NODE_UNAVAILABLE
def test_review_operating_system_filters_progress_and_overlays() -> None:
    _run_node(
        _viewer_harness(
            """
            const blockerLine = fakeLine();
            const reviewLine = fakeLine();
            const lifecycleMarker = fakeMarker();
            viewer.featureData = [
              {
                marker: lifecycleMarker,
                props: {
                  id: 'PR1',
                  pole_id: 'PR1',
                  structure_type: 'PRpole',
                  asset_intent: 'proposed',
                  material: 'wood',
                  relationship: 'replacement_pair',
                  replacing: 'EX1',
                },
              },
            ];
            viewer._spanLineRefs = [
              {
                props: {
                  from_point_id: 'EX1',
                  to_point_id: 'PR1',
                  span_validity: 'invalid',
                  missing_fields: ['height'],
                },
                line: blockerLine,
                routeGroupIndex: 0,
              },
              {
                props: {
                  from_point_id: 'PR1',
                  to_point_id: 'P2',
                  crossing_risk_level: 'medium',
                  geometry_trust: 'low',
                },
                line: reviewLine,
                routeGroupIndex: 0,
              },
            ];
            viewer._reviewNavigationTargets = viewer.buildReviewNavigationTargets();
            viewer._reviewOpsFilters.severity = 'BLOCKER';
            let ops = viewer.computeReviewOperatingSystemState();
            assert(ops.filteredIssues.length === 1, 'severity filter should isolate blocker issue');
            const blockerIssue = ops.filteredIssues[0];
            assert(blockerIssue.severity === 'BLOCKER', 'filtered issue should be blocker');

            viewer.applyReviewOperatingSystemOverlays(ops);
            assert(
              blockerLine.getElement().classList.contains('gf-review-risk-high'),
              'blocker span should receive high-risk overlay',
            );
            assert(
              reviewLine.getElement().classList.contains('gf-review-risk-muted'),
              'non-filtered review span should be muted',
            );

            viewer._activeReviewTargetGroup = blockerIssue.groups[0];
            const blockerGroupTargets = viewer._reviewNavigationTargets[blockerIssue.groups[0]];
            viewer._activeReviewTargetIndex = blockerGroupTargets.findIndex((target, index) => (
              viewer.targetIssueId(target, index) === blockerIssue.id
            ));
            viewer.markCurrentReviewIssueReviewed();
            viewer._reviewOpsFilters.unresolvedOnly = true;
            ops = viewer.computeReviewOperatingSystemState();
            assert(ops.reviewed === 1, 'reviewed issue count should update');
            assert(
              ops.filteredIssues.every((issue) => !issue.reviewed),
              'unresolved-only filter should hide reviewed issues',
            );

            viewer.clearReviewedReviewIssues();
            ops = viewer.computeReviewOperatingSystemState();
            assert(ops.reviewed === 0, 'clearing reviewed state should reset progress');
            viewer.jumpToReviewIssue(blockerIssue.id);
            assert(viewer._focusedReviewTarget, 'quick-jump should focus a map target');
            """
        )
    )


def test_review_command_center_preserves_c2e2_popup_truthfulness_strings() -> None:
    js = MAP_JS.read_text(encoding="utf-8")

    for truthful_string in [
        "Not measured (intermediate pole)",
        "Not measured — check survey notes",
        "Not recorded in survey",
    ]:
        assert truthful_string in js
