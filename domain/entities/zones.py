from enum import Enum


class Zones(Enum):
    """
    Enumeration for zone types in the network:
    - NORMAL:     Standard zone, costs 1 turn.
    - BLOCKED:    Inaccessible zone, cannot be entered.
    - RESTRICTED: Dangerous zone, costs 2 turns.
    - PRIORITY:   Preferred zone, costs 1 turn and is
                  prioritized in route calculation.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
