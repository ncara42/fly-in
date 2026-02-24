import heapq
import itertools
from domain.entities import Hub, Zones


class RoutingService:
    """
    Service class for pathfinding and routing between hubs.

    Provides methods to find optimal paths considering zone types,
    movement costs, and blocked zones for drone simulation.
    """

    def _heuristic(self, node: Hub, end: Hub) -> float:
        """
        Calculates the Manhattan distance between two hubs for the A* algorithm
        This heuristic estimates the cost from a node to the goal, guiding the
        search toward the shortest path. Manhattan distance is the sum of the
        absolute differences of the coordinates.

        Args:
            node: Hub object representing the current location.
            end: Hub object representing the destination.

        Returns:
            The Manhattan distance between the two nodes as a float.
        """
        (x1, y1) = node.coord
        (x2, y2) = end.coord
        return abs(x2 - x1) + abs(y2 - y1)

    def find_path(
        self,
        hubs: dict[str, Hub],
        adjacencies: dict[str, list[str]],
        start: Hub,
        end: Hub,
        occupancy: set[str] | None = None
    ) -> list[str]:
        """
        Finds the optimal path between two hubs using the A* algorithm.
        Considers zone types and movement costs, avoids blocked zones, and
        prioritizes preferred zones. Returns the sequence of hubs forming the
        shortest valid route.

        Args:
            hubs: Dictionary of hub names to their information.
            adjacencies: Graph structure mapping each hub to its neighbors.
            start: Name of the starting hub.
            end: Name of the destination hub.

        Returns:
            List of hub *names* (strings) representing the optimal path from
            start to end. Returns an empty list if no path exists.
        """
        counter = itertools.count()
        queue: list[tuple[float, int, Hub]] = [(0.0, next(counter), start)]

        came_from: dict[str, str] = {}
        cost_score: dict[str, float] = {hub: float('inf')
                                        for hub in adjacencies}
        cost_score[start.name] = 0.0

        while queue:

            # heapq is a module for priority queues
            # Pop the hub with the lowest cost; in the
            # first iteration, it will pop start (predefined)
            _, _, current_hub = heapq.heappop(queue)

            # If the current hub is the end, we have found
            # the shortest path
            if current_hub == end:
                path: list[str] = []
                current_name = current_hub.name
                while current_name in came_from:
                    path.append(current_name)
                    current_name = came_from[current_name]
                # Finally, add start name
                path.append(start.name)
                return path[::-1]

            # Adjacencies is the graph of hubs {hub: neighbors}
            for neighbor in adjacencies.get(current_hub.name, []):
                neighbor_hub = hubs[neighbor]
                # If the zone is blocked, skip it
                if neighbor_hub.zone == Zones.BLOCKED:
                    continue
                if occupancy and neighbor in occupancy:
                    continue

                # Calculate cost according to zone. Not turns, just cost
                if neighbor_hub.zone == Zones.PRIORITY:
                    turn_cost = 1
                elif neighbor_hub.zone == Zones.RESTRICTED:
                    turn_cost = 5
                else:
                    turn_cost = 2

                # Calculate the cost for all
                new_cost = cost_score[current_hub.name] + turn_cost
                # Only enter those that are less than the previous
                if new_cost < cost_score[neighbor]:
                    came_from[neighbor] = current_hub.name
                    cost_score[neighbor] = new_cost

                    # Estimate what the cost is
                    estimated_cost = new_cost + self._heuristic(
                        neighbor_hub, end
                    )
                    # Add the hub with the lowest cost to the queue
                    heapq.heappush(
                        queue, (estimated_cost, next(counter), neighbor_hub)
                    )

        return []
