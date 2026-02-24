from dataclasses import dataclass, field


@dataclass
class Drone:
    """
    Represents the state and route information of a drone.

    Attributes:
        id: Unique drone identifier.
        start_hub: Name of the starting hub.
        end_hub: Name of the destination hub.
        path_idx: Current index in the path.
        path: List of hubs representing the route.
        restricted: Turns remaining in restricted zone.

    The class tracks the drone's position, route, and restricted zone turns
    for simulation purposes.
    """
    id: str
    start_hub: str
    end_hub: str
    path_idx: int = 0
    path: list[str] = field(default_factory=list)
    restricted: int = 0

    @property
    def current_hub(self) -> str:
        if self.path:
            return self.path[self.path_idx]
        return self.start_hub
