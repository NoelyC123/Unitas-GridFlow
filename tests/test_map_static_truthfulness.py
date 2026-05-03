"""Static and template checks for map truthfulness / UX hooks (P2–P8, map viewer)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_JS = REPO_ROOT / "app/static/js/map-viewer.js"
MAP_CSS = REPO_ROOT / "app/static/css/map-viewer.css"


@pytest.fixture(scope="module")
def map_view_html() -> str:
    app = create_app()
    client = app.test_client()
    res = client.get("/map/view/J_MAP_HOOKS")
    assert res.status_code == 200
    return res.data.decode("utf-8")


@pytest.fixture(scope="module")
def map_js_source() -> str:
    return MAP_JS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def map_css_source() -> str:
    return MAP_CSS.read_text(encoding="utf-8")


def test_map_view_links_map_viewer_css_v8(map_view_html: str) -> None:
    assert 'href="/static/css/map-viewer.css?v=8"' in map_view_html


def test_map_view_layer_toggle_data_keys(map_view_html: str) -> None:
    for key in (
        "existing",
        "proposed",
        "angle",
        "stays",
        "thirdparty",
        "context",
        "spans",
        "cables",
        "matches",
    ):
        assert f'data-layer-key="{key}"' in map_view_html


def test_map_view_layer_toggle_caption_class(map_view_html: str) -> None:
    assert "layer-toggle-caption" in map_view_html


def test_map_view_focus_filter_captions(map_view_html: str) -> None:
    assert "focus-filter-caption" in map_view_html


def test_map_view_focus_clearance_crossings(map_view_html: str) -> None:
    assert 'data-focus="clearance-crossings"' in map_view_html


def test_map_view_focus_span_anomalies(map_view_html: str) -> None:
    assert 'data-focus="span-anomalies"' in map_view_html


def test_map_view_focus_span_crossing_risk(map_view_html: str) -> None:
    assert 'data-focus="span-crossing-risk"' in map_view_html


def test_map_view_focus_replacement_proximity(map_view_html: str) -> None:
    assert 'data-focus="replacement-proximity"' in map_view_html


def test_map_view_span_label_mode_control(map_view_html: str) -> None:
    assert 'id="span-label-mode"' in map_view_html


def test_map_view_span_panel(map_view_html: str) -> None:
    assert 'id="span-panel"' in map_view_html
    assert 'id="span-list"' in map_view_html


def test_map_view_lifecycle_match_toggle(map_view_html: str) -> None:
    assert 'id="lifecycle-match-toggle"' in map_view_html


def test_map_js_zero_count_layer_truthfulness(map_js_source: str) -> None:
    assert "applyZeroCountLayerTruthfulness" in map_js_source
    assert "cable_feature_count" in map_js_source
    assert "layer-toggle-disabled" in map_js_source


def test_map_js_clearance_crossings_filter(map_js_source: str) -> None:
    assert "clearance-crossings" in map_js_source
    assert "span_crossing_links" in map_js_source


def test_map_js_layer_and_filter_counts(map_js_source: str) -> None:
    assert "applyLayerAndFilterCounts" in map_js_source
    assert "focus-filter-caption" in map_js_source


def test_map_js_span_electrical_scope_wording(map_js_source: str) -> None:
    assert "Electrical scope" in map_js_source
    assert "includeEquipment" in map_js_source


def test_map_js_classify_route_span_anomaly(map_js_source: str) -> None:
    assert "classifyRouteSpanAnomaly" in map_js_source


def test_map_js_crossing_weighted_context_labels(map_js_source: str) -> None:
    assert "Crossing-weighted context" in map_js_source
    assert "Route proximity" in map_js_source


def test_map_js_context_span_corridor_links(map_js_source: str) -> None:
    assert "Span corridor links" in map_js_source
    assert "Correlation confidence" in map_js_source


def test_map_js_legacy_provenance_banners(map_js_source: str) -> None:
    assert "Source cue — legacy map data" in map_js_source
    assert "Source cue — DNO GIS import" in map_js_source
    assert "Source cue — digitised drawing / plan" in map_js_source


def test_map_js_replacement_cluster_hint(map_js_source: str) -> None:
    assert "lifecycle-cluster-hint" in map_js_source
    assert "lifecycle-conf-high" in map_js_source


def test_map_js_disabled_layer_toggle_guard(map_js_source: str) -> None:
    assert "input.disabled" in map_js_source


def test_map_css_layer_toggle_disabled(map_css_source: str) -> None:
    assert "layer-toggle-disabled" in map_css_source


def test_map_css_span_list_anomaly(map_css_source: str) -> None:
    assert "span-list-anomaly" in map_css_source


def test_map_css_lifecycle_confidence(map_css_source: str) -> None:
    assert "lifecycle-conf-high" in map_css_source
    assert "lifecycle-conf-med" in map_css_source
    assert "lifecycle-conf-low" in map_css_source


def test_map_js_has_span_anomaly_uses_classifier(map_js_source: str) -> None:
    assert "hasSpanAnomaly(props) {" in map_js_source
    assert "classifyRouteSpanAnomaly(props).causes.length" in map_js_source


def test_map_js_filter_label_clearance_crossings(map_js_source: str) -> None:
    assert "'clearance-crossings':" in map_js_source


def test_map_js_map_meta_copy(map_js_source: str) -> None:
    assert "_mapMeta" in map_js_source


def test_map_js_popup_contract_renderer_and_fallback(map_js_source: str) -> None:
    assert "popup_schema_contract" in map_js_source
    assert "buildContractPopupHtml" in map_js_source
    assert "legacyPointPopupSections" in map_js_source
    assert "buildLegacyPointPopupHtml" in map_js_source


def test_map_js_popup_review_polish_hooks(map_js_source: str) -> None:
    assert "gridflow-asset-popup" in map_js_source
    assert "popup-section-chip" in map_js_source
    assert 'data-popup-label="${this.escapeHtml(label)}"' in map_js_source
    assert "keepInView: true" in map_js_source


def test_map_js_popup_blank_state_detection(map_js_source: str) -> None:
    assert "popupSectionMeta(rows)" in map_js_source
    assert 'data-popup-label="Summary"' in map_js_source
    assert "isEmptyPopupDisplay(display)" in map_js_source


def test_map_js_primary_layer_key(map_js_source: str) -> None:
    assert "primaryLayerKey" in map_js_source


def test_map_view_meta_map_data_url(map_view_html: str) -> None:
    assert 'name="map-data-url"' in map_view_html


def test_map_view_job_id_meta(map_view_html: str) -> None:
    assert 'name="job-id"' in map_view_html


def test_map_js_span_list_anomaly_chip(map_js_source: str) -> None:
    assert "span-list-anomaly" in map_js_source


def test_map_js_electrical_rows_default_includes_equipment(map_js_source: str) -> None:
    assert "includeEquipment !== false" in map_js_source


def test_map_view_provisional_route_spans_caption(map_view_html: str) -> None:
    assert "Provisional route spans (line)" in map_view_html


def test_map_view_span_panel_heading_id(map_view_html: str) -> None:
    assert 'id="span-panel-heading"' in map_view_html


def test_map_view_legend_span_caption_id(map_view_html: str) -> None:
    assert 'id="legend-span-line-caption"' in map_view_html


def test_map_view_review_focus_polish_labels(map_view_html: str) -> None:
    assert "Replacement pairing signals" in map_view_html
    assert "Span crossing / context review" in map_view_html
    assert "UG cable records missing spec" in map_view_html


def test_map_view_legend_truthful_review_wording(map_view_html: str) -> None:
    assert "Suggested Existing/Proposed Match (map evidence only)" in map_view_html
    assert "Design blocker — issue prevents design-readiness" in map_view_html
    assert "click for span review detail, or pin labels for QA scanning" in map_view_html


def test_map_js_span_label_pin_modes(map_js_source: str) -> None:
    assert "isSpanPinCritical" in map_js_source
    assert "isSpanPinCrossing" in map_js_source
    assert "isSpanPinReview" in map_js_source


def test_map_js_replacement_drawable_line_count(map_js_source: str) -> None:
    assert "_replacementDrawableLineCount" in map_js_source


def test_map_js_short_span_cause_classifier(map_js_source: str) -> None:
    assert "classifyShortLikelySpanCause" in map_js_source


def test_map_js_filter_span_designer_actions(map_js_source: str) -> None:
    assert "filterSpanDesignerActions" in map_js_source


def test_map_js_condense_vacuous_popup_rows(map_js_source: str) -> None:
    assert "condenseVacuousPopupRows" in map_js_source
    assert "isVacuousPopupRowHtml" in map_js_source


def test_map_js_span_layer_origin_sync(map_js_source: str) -> None:
    assert "syncSpanPanelHeading" in map_js_source
    assert "span_layer_origin" in map_js_source


def test_span_generator_sets_span_layer_origin() -> None:
    from app.span_generator import attach_span_features_to_collection

    data: dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                "properties": {"pole_id": "A"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.01, 54.51]},
                "properties": {"pole_id": "B"},
            },
        ],
        "metadata": {"rulepack_id": "SPEN_11kV"},
    }
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "A", "lat": 54.5, "lon": -3.0, "span_to_next_m": 77},
            {"point_id": "B", "lat": 54.51, "lon": -3.01},
        ],
    }
    attach_span_features_to_collection(data, seq)
    assert data["metadata"].get("span_layer_origin") == "provisional_route"


def test_span_generator_preserves_explicit_survey_circuit_origin() -> None:
    from app.span_generator import attach_span_features_to_collection

    data: dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                "properties": {"pole_id": "A"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.01, 54.51]},
                "properties": {"pole_id": "B"},
            },
        ],
        "metadata": {"rulepack_id": "SPEN_11kV", "span_layer_origin": "survey_circuit"},
    }
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "A", "lat": 54.5, "lon": -3.0, "span_to_next_m": 50},
            {"point_id": "B", "lat": 54.51, "lon": -3.01},
        ],
    }
    attach_span_features_to_collection(data, seq)
    assert data["metadata"].get("span_layer_origin") == "survey_circuit"
