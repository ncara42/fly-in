"""
[Fly in]

Route simulator for drones in a network of hubs and connections.
Optimizes movements and visualizes turns with restrictions and capacities.
"""

import sys
from infrastructure.parsers import MapParser
from domain.services import RoutingService, SimulationService, DroneFactory
from utils import Color


def main() -> None:
    """
    Entry point for the drone route simulator.
    Validates command-line arguments, loads the map file, and starts the
    simulation. Shows error and usage instructions if arguments are missing.

    Args:
        None. Reads from sys.argv.

    Returns:
        None. Exits on error.
    """
    if len(sys.argv) < 2:
        print(f"{Color.ERROR}Error{Color.RESET}: Missing map file")
        print("Execute: make run <maps/map.txt>")
        sys.exit(1)

    map_path = sys.argv[1]
    print(f"Loading map: {map_path}")

    routing = RoutingService()
    simulation = SimulationService()
    factory = DroneFactory()
    parser = MapParser(routing, simulation, factory)
    try:
        parser.parse_map(map_path)
    except Exception as e:
        print(f"Error during map parsing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
