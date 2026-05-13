"""
Route reconstruction and pole sequencing.

Infers pole routes from geographic proximity and assigns sequence numbers.
"""

import logging
import math
from typing import Dict, List

from gridflow.baseline.models import BaselineDataset, BaselinePole

logger = logging.getLogger(__name__)


class RouteReconstructor:
    """
    Reconstruct routes and sequence poles by proximity.

    When route_id is missing, uses spatial clustering and nearest-neighbor
    ordering to assign poles to synthetic routes and determine their sequence.
    """

    # Maximum distance between consecutive poles (meters)
    MAX_DISTANCE_BETWEEN_POLES = 500

    def reconstruct_sequences(self, dataset: BaselineDataset) -> BaselineDataset:
        """
        Fill missing route_id and pole_sequence values using spatial clustering.

        Args:
            dataset: BaselineDataset with partial or missing route/sequence info

        Returns:
            BaselineDataset with route_id and pole_sequence populated
        """
        logger.info("Reconstructing pole sequences")

        poles_by_route = self._group_poles_by_route(dataset.poles)
        logger.info(f"Grouped {len(dataset.poles)} poles into {len(poles_by_route)} routes")

        # Process each route
        for route_id, poles in poles_by_route.items():
            ordered_poles = self.order_poles_by_proximity(poles)
            for seq, pole in enumerate(ordered_poles, 1):
                pole.route_id = route_id
                pole.pole_sequence = seq

        dataset.poles = [p for route_poles in poles_by_route.values() for p in route_poles]
        logger.info(f"Assigned sequence to {len(dataset.poles)} poles")

        return dataset

    def _group_poles_by_route(self, poles: List[BaselinePole]) -> Dict[str, List[BaselinePole]]:
        """Group poles into routes using existing route_id or spatial clustering."""
        poles_with_route = []
        poles_without_route = []

        # Separate poles with/without route_id
        for pole in poles:
            if pole.route_id:
                poles_with_route.append(pole)
            else:
                poles_without_route.append(pole)

        # Start with existing route assignments
        grouped = {}
        for pole in poles_with_route:
            if pole.route_id not in grouped:
                grouped[pole.route_id] = []
            grouped[pole.route_id].append(pole)

        # Cluster poles without route assignments
        if poles_without_route:
            clustered = self.detect_routes(poles_without_route)
            for cluster_id, cluster_poles in enumerate(clustered, 1):
                route_id = f"SYNTHETIC_ROUTE_{cluster_id}"
                grouped[route_id] = cluster_poles

        return grouped

    def detect_routes(self, poles: List[BaselinePole]) -> List[List[BaselinePole]]:
        """
        Detect distinct routes using spatial clustering.

        Uses simple nearest-neighbor clustering: start with a pole,
        find all nearby poles, remove them, repeat.

        Args:
            poles: List of poles to cluster

        Returns:
            List of routes (each route is a list of poles)
        """
        if not poles:
            return []

        remaining = set(range(len(poles)))
        routes = []

        while remaining:
            # Start new route from any remaining pole
            current_idx = remaining.pop()
            route = [poles[current_idx]]
            visited = {current_idx}

            # Expand route using nearest neighbors
            changed = True
            while changed:
                changed = False
                current_pole = route[-1]

                # Find nearest unvisited pole
                nearest_idx = None
                nearest_dist = float("inf")

                for idx in remaining:
                    dist = self._haversine_distance(current_pole, poles[idx])
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_idx = idx

                # Add if within threshold
                if nearest_idx is not None and nearest_dist <= self.MAX_DISTANCE_BETWEEN_POLES:
                    remaining.remove(nearest_idx)
                    route.append(poles[nearest_idx])
                    visited.add(nearest_idx)
                    changed = True

            routes.append(route)
            logger.debug(f"Found route with {len(route)} poles")

        return routes

    def order_poles_by_proximity(self, poles: List[BaselinePole]) -> List[BaselinePole]:
        """
        Order poles in route by geographic proximity.

        Uses nearest-neighbor ordering: start from one pole, always move to
        the nearest unvisited pole.

        Args:
            poles: Poles in a single route

        Returns:
            Poles ordered by proximity
        """
        if not poles:
            return []

        if len(poles) == 1:
            return poles

        # Start from southernmost pole (smallest northing)
        start_idx = min(range(len(poles)), key=lambda i: poles[i].northing)
        ordered = [poles[start_idx]]
        remaining_indices = set(range(len(poles))) - {start_idx}

        while remaining_indices:
            current_pole = ordered[-1]

            # Find nearest remaining pole
            nearest_idx = min(
                remaining_indices, key=lambda i: self._haversine_distance(current_pole, poles[i])
            )

            ordered.append(poles[nearest_idx])
            remaining_indices.remove(nearest_idx)

        return ordered

    def validate_route_continuity(self, poles: List[BaselinePole]) -> List[Dict]:
        """
        Check for gaps in route (poles far apart).

        Args:
            poles: Ordered list of poles in a route

        Returns:
            List of gaps found (each gap has pole_ids and distance)
        """
        gaps = []

        for i in range(len(poles) - 1):
            current = poles[i]
            next_pole = poles[i + 1]
            distance = self._haversine_distance(current, next_pole)

            if distance > self.MAX_DISTANCE_BETWEEN_POLES:
                gaps.append(
                    {
                        "from": current.pole_id,
                        "to": next_pole.pole_id,
                        "distance": distance,
                    }
                )

        if gaps:
            logger.warning(f"Found {len(gaps)} gaps in route continuity")

        return gaps

    @staticmethod
    def _haversine_distance(pole1: BaselinePole, pole2: BaselinePole) -> float:
        """
        Calculate distance between two poles using Haversine formula.

        Uses OSGB36 coordinates directly (meters) for simple Euclidean distance
        since poles are close together and UK-based.

        Args:
            pole1: First pole
            pole2: Second pole

        Returns:
            Distance in meters
        """
        # Use Euclidean distance on OSGB36 grid (good enough for local distances)
        de = pole2.easting - pole1.easting
        dn = pole2.northing - pole1.northing
        return math.sqrt(de**2 + dn**2)
