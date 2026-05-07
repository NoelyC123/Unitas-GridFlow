"""Tests for geometry issue span clustering."""

from __future__ import annotations

from app.span_generator import annotate_geometry_issue_clusters


def _span(validity: str) -> dict:
    return {"type": "Feature", "geometry": None, "properties": {"span_validity": validity}}


# ---------------------------------------------------------------------------
# Required spec tests
# ---------------------------------------------------------------------------


def test_three_consecutive_suspect_spans_form_one_cluster():
    spans = [_span("suspect"), _span("suspect"), _span("suspect")]
    annotate_geometry_issue_clusters(spans)
    for s in spans:
        assert s["properties"]["geometry_issue_cluster"] is True
        assert s["properties"]["cluster_size"] == 3


def test_mixed_spans_split_into_correct_clusters():
    # [invalid, invalid, valid] → cluster of 2, then no cluster
    spans = [_span("invalid"), _span("invalid"), _span("valid")]
    annotate_geometry_issue_clusters(spans)

    assert spans[0]["properties"]["geometry_issue_cluster"] is True
    assert spans[0]["properties"]["cluster_size"] == 2
    assert spans[1]["properties"]["geometry_issue_cluster"] is True
    assert spans[1]["properties"]["cluster_size"] == 2
    assert spans[2]["properties"]["geometry_issue_cluster"] is False
    assert spans[2]["properties"]["cluster_size"] is None


def test_valid_spans_have_no_cluster():
    spans = [_span("valid"), _span("valid")]
    annotate_geometry_issue_clusters(spans)
    for s in spans:
        assert s["properties"]["geometry_issue_cluster"] is False
        assert s["properties"]["cluster_size"] is None


def test_single_invalid_span_does_not_form_cluster():
    spans = [_span("invalid")]
    annotate_geometry_issue_clusters(spans)
    assert spans[0]["properties"]["geometry_issue_cluster"] is False
    assert spans[0]["properties"]["cluster_size"] is None


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------


def test_two_separate_clusters_of_size_one():
    # [invalid, valid, invalid] → no clusters because clusters require >=2 spans.
    spans = [_span("invalid"), _span("valid"), _span("invalid")]
    annotate_geometry_issue_clusters(spans)

    assert spans[0]["properties"]["geometry_issue_cluster"] is False
    assert spans[0]["properties"]["cluster_size"] is None
    assert spans[1]["properties"]["geometry_issue_cluster"] is False
    assert spans[2]["properties"]["geometry_issue_cluster"] is False
    assert spans[2]["properties"]["cluster_size"] is None


def test_cluster_at_end_of_list():
    spans = [_span("valid"), _span("invalid"), _span("invalid")]
    annotate_geometry_issue_clusters(spans)

    assert spans[0]["properties"]["geometry_issue_cluster"] is False
    assert spans[1]["properties"]["cluster_size"] == 2
    assert spans[2]["properties"]["cluster_size"] == 2


def test_cluster_at_start_of_list():
    spans = [_span("invalid"), _span("suspect"), _span("valid")]
    annotate_geometry_issue_clusters(spans)

    assert spans[0]["properties"]["cluster_size"] == 2
    assert spans[1]["properties"]["cluster_size"] == 2
    assert spans[2]["properties"]["geometry_issue_cluster"] is False


def test_span_validity_is_not_modified():
    spans = [_span("invalid"), _span("suspect"), _span("valid")]
    annotate_geometry_issue_clusters(spans)

    assert spans[0]["properties"]["span_validity"] == "invalid"
    assert spans[1]["properties"]["span_validity"] == "suspect"
    assert spans[2]["properties"]["span_validity"] == "valid"


def test_span_order_preserved():
    spans = [_span("valid"), _span("invalid"), _span("suspect"), _span("valid")]
    original_validities = [s["properties"]["span_validity"] for s in spans]
    annotate_geometry_issue_clusters(spans)
    after_validities = [s["properties"]["span_validity"] for s in spans]
    assert original_validities == after_validities


def test_empty_list_does_not_raise():
    annotate_geometry_issue_clusters([])


def test_mixed_invalid_and_suspect_in_same_cluster():
    spans = [_span("invalid"), _span("suspect"), _span("invalid")]
    annotate_geometry_issue_clusters(spans)
    for s in spans:
        assert s["properties"]["geometry_issue_cluster"] is True
        assert s["properties"]["cluster_size"] == 3


def test_longer_sequence_with_multiple_clusters():
    # [valid, invalid, invalid, valid, suspect, valid]
    # clusters: [invalid,invalid] size 2; single suspect is not a cluster.
    spans = [
        _span("valid"),
        _span("invalid"),
        _span("invalid"),
        _span("valid"),
        _span("suspect"),
        _span("valid"),
    ]
    annotate_geometry_issue_clusters(spans)

    assert spans[0]["properties"]["geometry_issue_cluster"] is False
    assert spans[1]["properties"]["cluster_size"] == 2
    assert spans[2]["properties"]["cluster_size"] == 2
    assert spans[3]["properties"]["geometry_issue_cluster"] is False
    assert spans[4]["properties"]["geometry_issue_cluster"] is False
    assert spans[4]["properties"]["cluster_size"] is None
    assert spans[5]["properties"]["geometry_issue_cluster"] is False
