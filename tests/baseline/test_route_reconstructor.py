"""Tests for route reconstructor."""

import pytest

from gridflow.baseline import (
    BaselineDataset,
    BaselinePole,
    RouteReconstructor,
)


@pytest.fixture
def reconstructor():
    """Return reconstructor instance."""
    return RouteReconstructor()


@pytest.fixture
def simple_route_poles():
    """Return poles in a simple linear route."""
    return [
        BaselinePole(
            pole_id="POLE_001",
            easting=354123.45,
            northing=456789.12,
        ),
        BaselinePole(
            pole_id="POLE_002",
            easting=354223.45,  # 100m north
            northing=456889.12,
        ),
        BaselinePole(
            pole_id="POLE_003",
            easting=354323.45,  # 100m north
            northing=456989.12,
        ),
    ]


@pytest.fixture
def two_route_poles():
    """Return poles in two separate routes."""
    return [
        # Route 1: Cluster at 354000
        BaselinePole(
            pole_id="POLE_001",
            easting=354123.45,
            northing=456789.12,
        ),
        BaselinePole(
            pole_id="POLE_002",
            easting=354223.45,
            northing=456889.12,
        ),
        # Route 2: Cluster at 365000 (far away)
        BaselinePole(
            pole_id="POLE_101",
            easting=365123.45,
            northing=467789.12,
        ),
        BaselinePole(
            pole_id="POLE_102",
            easting=365223.45,
            northing=467889.12,
        ),
    ]


class TestRouteOrdering:
    """Test pole ordering within a route."""

    def test_order_simple_route(self, reconstructor, simple_route_poles):
        """Test ordering poles in simple linear route."""
        ordered = reconstructor.order_poles_by_proximity(simple_route_poles)

        assert len(ordered) == 3
        # All poles should be present
        ids = {p.pole_id for p in ordered}
        assert ids == {"POLE_001", "POLE_002", "POLE_003"}

    def test_order_single_pole(self, reconstructor):
        """Test ordering single pole."""
        poles = [
            BaselinePole(
                pole_id="POLE_001",
                easting=354123.45,
                northing=456789.12,
            )
        ]
        ordered = reconstructor.order_poles_by_proximity(poles)
        assert len(ordered) == 1
        assert ordered[0].pole_id == "POLE_001"

    def test_order_empty_list(self, reconstructor):
        """Test ordering empty list."""
        ordered = reconstructor.order_poles_by_proximity([])
        assert ordered == []


class TestRouteDetection:
    """Test detection of multiple routes."""

    def test_detect_single_route(self, reconstructor, simple_route_poles):
        """Test detection of single route."""
        routes = reconstructor.detect_routes(simple_route_poles)

        assert len(routes) == 1
        assert len(routes[0]) == 3

    def test_detect_multiple_routes(self, reconstructor, two_route_poles):
        """Test detection of two separate routes."""
        routes = reconstructor.detect_routes(two_route_poles)

        assert len(routes) >= 2
        # Total poles should be preserved
        total = sum(len(route) for route in routes)
        assert total == 4

    def test_detect_empty_routes(self, reconstructor):
        """Test detection with empty poles."""
        routes = reconstructor.detect_routes([])
        assert routes == []


class TestContinuityValidation:
    """Test route continuity checks."""

    def test_validate_continuous_route(self, reconstructor, simple_route_poles):
        """Test validation of continuous route."""
        ordered = reconstructor.order_poles_by_proximity(simple_route_poles)
        gaps = reconstructor.validate_route_continuity(ordered)

        # Should have no large gaps
        assert all(gap["distance"] <= reconstructor.MAX_DISTANCE_BETWEEN_POLES for gap in gaps)


class TestSequenceReconstruction:
    """Test full sequence reconstruction."""

    def test_reconstruct_sequences(self, reconstructor, simple_route_poles):
        """Test reconstructing sequences for simple route."""
        dataset = BaselineDataset(poles=simple_route_poles)

        assert not dataset.has_routes
        assert not dataset.has_sequences

        dataset = reconstructor.reconstruct_sequences(dataset)

        assert dataset.has_routes
        assert dataset.has_sequences
        # Sequences should be 1, 2, 3
        sequences = sorted([p.pole_sequence for p in dataset.poles])
        assert sequences == [1, 2, 3]

    def test_reconstruct_preserves_existing_routes(self, reconstructor):
        """Test that existing route assignments are preserved."""
        poles = [
            BaselinePole(
                pole_id="POLE_001",
                route_id="ROUTE_A",
                easting=354123.45,
                northing=456789.12,
            ),
            BaselinePole(
                pole_id="POLE_002",
                route_id="ROUTE_A",
                easting=354223.45,
                northing=456889.12,
            ),
        ]
        dataset = BaselineDataset(poles=poles)
        dataset = reconstructor.reconstruct_sequences(dataset)

        # Route assignments should be preserved
        assert all(p.route_id == "ROUTE_A" for p in dataset.poles)
