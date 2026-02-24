import difflib
from dataclasses import dataclass
from domain.entities import Zones
from utils import Palette


@dataclass
class Hub:
    """
    Represents a hub in the drone route network.

    Attributes:
        name: Hub name.
        coord: Coordinates (x, y).
        color: Hub color name or None.
        max_drones: Maximum drones allowed in the hub.
        zone: Zone type (normal, restricted, etc.).

    Used to store hub properties for simulation and routing.
    """
    name: str
    coord: tuple[int, int]
    color: str | None = None
    max_drones: int = 1
    zone: Zones = Zones.NORMAL

    def set_metadata(self, metadata: dict[str, str]) -> None:
        if 'color' in metadata:
            for color in Palette:
                if color.value in metadata['color']:
                    self.color = color.value
                    break

        if 'zone' in metadata:
            for zone in Zones:
                if zone.value == metadata['zone']:
                    self.zone = zone
                    break
            else:
                valid_zones: list[str] = [z.value for z in Zones]
                suggestion = difflib.get_close_matches(
                    metadata['zone'], valid_zones, n=1
                )
                if suggestion:
                    template = "'{}' is an invalid zone. Did you mean '{}'?"
                    raise ValueError(template.format(
                                     metadata['zone'],
                                     suggestion[0]))
                else:
                    template = f"'{metadata['zone']}' is an invalid zone."
                    raise ValueError(template)

        if 'max_drones' in metadata:
            self.max_drones = int(metadata['max_drones'])
