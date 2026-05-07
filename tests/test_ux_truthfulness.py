"""UX truthfulness checks: geometry trust banner, span distance formatting, cluster messaging.

Follows the same static-inspection pattern as test_map_static_truthfulness.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_JS = REPO_ROOT / "app/static/js/map-viewer.js"
MAP_HTML = REPO_ROOT / "app/templates/map_viewer.html"


@pytest.fixture(scope="module")
def js() -> str:
    return MAP_JS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def html() -> str:
    return MAP_HTML.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# HTML template: geometry trust banner element exists
# ---------------------------------------------------------------------------


def test_geometry_trust_banner_element_in_template(html: str) -> None:
    assert 'id="geometry-trust-banner"' in html


# ---------------------------------------------------------------------------
# JS: new functions exist
# ---------------------------------------------------------------------------


def test_format_span_distance_function_defined(js: str) -> None:
    assert "formatSpanDistance" in js


def test_render_geometry_trust_banner_function_defined(js: str) -> None:
    assert "renderGeometryTrustBanner" in js


# ---------------------------------------------------------------------------
# JS: geometry trust banner messages
# ---------------------------------------------------------------------------


def test_low_trust_banner_message_present(js: str) -> None:
    assert "Geometry reliability LOW" in js


def test_low_trust_banner_uses_fail_class(js: str) -> None:
    assert "issue-note-fail" in js


def test_medium_trust_banner_message_present(js: str) -> None:
    assert "Geometry may contain inconsistencies" in js


def test_medium_trust_banner_uses_warn_class(js: str) -> None:
    assert "issue-note-warn" in js


# ---------------------------------------------------------------------------
# JS: distance formatting precision per trust level
# ---------------------------------------------------------------------------


def test_low_trust_uses_tilde_and_integer_rounding(js: str) -> None:
    assert "Math.round(d)" in js


def test_medium_trust_uses_tilde_and_one_decimal(js: str) -> None:
    # ~${d.toFixed(1)} m  or equivalent
    assert "toFixed(1)" in js


def test_high_trust_uses_two_decimal_places(js: str) -> None:
    assert "toFixed(2)" in js


def test_low_trust_distance_prefixed_with_tilde(js: str) -> None:
    # The LOW branch must produce a ~ prefix
    assert "`~${Math.round(d)} m`" in js


def test_high_trust_distance_has_no_tilde(js: str) -> None:
    # HIGH branch: toFixed(2) without ~
    assert "`${d.toFixed(2)} m`" in js


# ---------------------------------------------------------------------------
# JS: _geometryTrust stored from metadata in loadData
# ---------------------------------------------------------------------------


def test_geometry_trust_read_from_metadata(js: str) -> None:
    assert "_geometryTrust" in js


def test_geometry_trust_defaults_to_high(js: str) -> None:
    assert "geometry_trust || 'HIGH'" in js


# ---------------------------------------------------------------------------
# JS: cluster messaging in span popup
# ---------------------------------------------------------------------------


def test_geometry_issue_cluster_handled_in_span_popup(js: str) -> None:
    assert "geometry_issue_cluster" in js


def test_multiple_short_spans_message_present(js: str) -> None:
    assert "Multiple short spans detected in this section" in js


def test_cluster_section_included_in_span_popup_return(js: str) -> None:
    assert "clusterSection" in js


def test_cluster_uses_warning_status(js: str) -> None:
    # clusterSection row must use 'warning' status, not 'info' or 'ok'
    assert "'warning'" in js


def test_design_reasons_are_sorted_by_severity(js: str) -> None:
    assert "sortedDesignReasons" in js
    assert "designReasonSeverityRank" in js
    assert "blocker: 0" in js
    assert "high: 1" in js
    assert "medium: 2" in js


def test_design_reason_severity_label_displayed(js: str) -> None:
    assert "Reason (${String(r.severity || 'info').toUpperCase()})" in js
    assert "designReasonStatus" in js


def test_design_reason_renderer_keeps_legacy_string_compatibility(js: str) -> None:
    assert "return { type: 'legacy', severity: 'info', message: String(reason || '') }" in js
    assert "if (reason && typeof reason === 'object') return reason" in js


def test_geometry_warning_condition_excludes_legacy_shortcut(js: str) -> None:
    snippet = js[js.index("const showGeometryWarning") : js.index("const warningBanner")]
    assert "trust === 'unverified'" in snippet
    assert "confidence === 'low'" in snippet
    assert "isLegacy" not in snippet
    assert "unknown" not in snippet
