from typing import Any
from domain.entities import Zones, Drone, Hub
from domain.services import RoutingService
from utils import Color, COLOR_MAP


class SimulationService:
    """
    Service class for simulating drone movements and turns.

    Manages occupancy, restricted zones, link capacities, and outputs
    simulation steps in the required format with color feedback.
    """
    routing_service = RoutingService()

    def simulate_turns(
        self,
        drones: list[Drone],
        adjacencies: dict[str, list[str]],
        hubs: dict[str, Hub],
        link_capacity: dict[tuple[str, str], int],
    ) -> None:
        """
        Simulates drone movements turn by turn, applying all zone and link
        restrictions. Manages occupancy, restricted zones, link capacities, and
        displays each turn's movements in the required format
        with color feedback.

        Args:
            drones: List of drone objects.
            adjacencies: Graph structure of hub connections.
            hubs: Dictionary of hub properties.
            link_capacity: Dictionary of connection capacities.
            max_turns: Maximum number of simulation turns.

        Returns:
            None. Prints simulation output per turn.
        """

        goal_logs: dict[str, int] = {}
        t = 0
        while True:
            occupancy: dict[str, int] = {}
            movements: list[str] = []
            logs: dict[str, dict[str, Any]] = {}
            link_usage: dict[tuple[str, str], int] = {}

            goal = [d for d in drones if d.path[d.path_idx] == d.end_hub]
            for d in goal:
                goal_logs[d.end_hub] = goal_logs.get(d.end_hub, 0) + 1

            # In each turn, check the drones that have reached their goal.
            # If they have reached their goal, we don't count them anymore.
            drones = [d for d in drones if d.path[d.path_idx] != d.end_hub]

            # If there are no drones, all have arrived
            if not drones:
                print(f"Turns: {t}")
                break

            # Movement loop
            for d in drones:
                actual_hub = d.current_hub
                actual_hub_obj = hubs[actual_hub]
                text_color_actual_hub: str = COLOR_MAP.get(str(
                    actual_hub_obj.color), Color.RESET
                )

                # If I am stationary, print my position and skip
                if d.restricted > 0:
                    movements.append(
                        f"{d.id}-{text_color_actual_hub}"
                        f"{actual_hub}{Color.RESET}"
                    )

                    d.restricted -= 1
                    continue

                # Instantiate next_hub, its color, and current occupancy
                next_hub = d.path[d.path_idx + 1]
                next_hub_obj = hubs[next_hub]
                text_color_next_hub = COLOR_MAP.get(str(
                    next_hub_obj.color), Color.RESET
                )
                current_occupancy = occupancy.get(next_hub, 0)

                # If the next hub is full, do not advance or replan
                if current_occupancy >= hubs[next_hub].max_drones:
                    occupied_hubs = {hub for hub, occ in occupancy.items()
                                     if occ >= hubs[hub].max_drones}
                    alt_path: list[str] = self.routing_service.find_path(
                        hubs, adjacencies, hubs[d.current_hub],
                        hubs[d.end_hub], occupied_hubs
                    )
                    if not alt_path:
                        continue
                    d.path = alt_path
                    next_hub = d.path[d.path_idx + 1]
                    continue

                # What is the current link?
                actual_link: tuple[str, str] = (actual_hub, next_hub)
                # What is the current capacity of this link?
                max_link = link_capacity.get(actual_link, float('inf'))
                # Does the current usage of this link exceed the maximum?
                if link_usage.get(actual_link, 0) >= max_link:
                    # No? I wait
                    continue

                # If I don't wait, increment link and node usage and advance
                link_usage[actual_link] = link_usage.get(actual_link, 0) + 1
                occupancy[next_hub] = current_occupancy + 1

                # Check capacity via logs
                logs.setdefault(next_hub, {
                    'next_hub': next_hub,
                    'next_hub_occ': 0,
                    'next_hub_max_occ': hubs[next_hub].max_drones,
                    'link_usage': 0,
                    'max_link_capacity': max_link
                })
                # Update the occupancy for both hub and link
                logs[next_hub]['next_hub_occ'] = occupancy[next_hub]
                logs[next_hub]['link_usage'] = link_usage[actual_link]

                d.path_idx += 1

                # If the next zone is restricted, penalize and print
                # log according to zone
                if hubs[next_hub].zone == Zones.RESTRICTED:
                    d.restricted = 1
                    movements.append(
                        f"{d.id}-{text_color_actual_hub}{actual_hub}-"
                        f"{text_color_next_hub}{next_hub}{Color.RESET}"
                    )
                else:
                    movements.append(
                        f"{d.id}-{text_color_next_hub}{next_hub}{Color.RESET}"
                    )

            t += 1
            # Print logs for this turn
            if movements:
                print(' '.join(movements))
