"""
[Fly-in]

This program simulates the routing of multiple drones through a network of hubs and connections.
It enforces zone types (normal, blocked, restricted, priority), zone and link capacities, and movement costs.
The simulation uses A* pathfinding to determine optimal routes, and outputs each turn's drone movements,
including colored terminal feedback for visual clarity. The parser reads map files with flexible metadata,
and the simulation is designed to be efficient, robust, and extensible for complex scenarios.
"""

import sys
from typing import TypedDict, Any, Generator
from enum import Enum
from src.Colors import Color, Palette, COLOR_MAP
import heapq


class Dron(TypedDict):
    """
    TypedDict representing the state and routing information for a drone.
    Includes unique ID, start/end hubs, current position, restricted turn counter,
    path index, and the computed path for simulation.
    """
    id: str
    start_hub: str
    end_hub: str
    current_hub: str
    restricted: int
    path_idx: int
    path: list[str]


class Hub(TypedDict):
    """
    TypedDict for hub properties including coordinates, color, maximum drone capacity,
    and zone type. Used to represent each node in the drone routing network.
    """
    coord: tuple[int, int]
    color: None | str
    max_drones: int
    zone: str


class Zones(Enum):
    """
    Enum for zone types in the network:
    - NORMAL: Standard zone, cost 1 turn.
    - BLOCKED: Inaccessible zone, cannot be entered.
    - RESTRICTED: Dangerous zone, cost 2 turns.
    - PRIORITY: Preferred zone, cost 1 turn, prioritized in pathfinding.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


def heuristic(hubs: dict[str, Hub], node: str, end: str) -> float:
    """
    Calculate the Manhattan distance between two hubs for A* pathfinding.
    This heuristic estimates the cost from a node to the goal, guiding the search
    towards the shortest path. Manhattan distance is the sum of absolute differences
    of the coordinates.

    Args:
        hubs: Dictionary mapping hub names to hub information including coordinates.
        node: Name of the current node.
        end: Name of the destination node.

    Returns:
        The Manhattan distance between the two nodes as a float.
    """
    (x1, y1) = hubs[node]['coord']
    (x2, y2) = hubs[end]['coord']

    return abs(x2 - x1) + abs(y2 - y1)


def find_path(hubs: dict[str, Hub], adjacencies: dict[str, list[str]],
              start: str, end: str) -> list[Any]:
    """
    Find the optimal path between two hubs using the A* algorithm.
    Considers zone types and movement costs, avoids blocked zones, and prioritizes
    preferred zones. Returns the sequence of hubs forming the shortest valid route.

    Args:
        hubs: Dictionary of hub names to hub information.
        adjacencies: Graph structure mapping each hub to its connected neighbors.
        start: Starting hub name.
        end: Destination hub name.

    Returns:
        List of hub names representing the optimal path from start to end.
        Returns empty list if no path exists.
    """

    queue: list[tuple[float, str]] = [(0.0, start)]

    came_from: dict[str, str] = {}
    cost_score: dict[str, float] = {node: float('inf') for node in hubs}
    cost_score[start] = 0.0

    while queue:
        _, current_hub = heapq.heappop(queue)

        if current_hub == end:
            path: list[str] = []
            while current_hub in came_from:
                path.append(current_hub)
                current_hub = came_from[current_hub]
            path.append(start)
            return path[::-1]

        for neighbor in adjacencies.get(current_hub, []):

            if hubs[neighbor]['zone'] == Zones.BLOCKED.value:
                continue

            turn_cost = 1
            if hubs[neighbor]['zone'] == Zones.RESTRICTED.value:
                turn_cost = 5
            elif hubs[neighbor]['zone'] == Zones.PRIORITY.value:
                turn_cost = 0.5

            new_cost = cost_score[current_hub] + turn_cost

            if new_cost < cost_score[neighbor]:
                came_from[neighbor] = current_hub
                cost_score[neighbor] = new_cost

                estimated_cost = new_cost + heuristic(hubs, neighbor, end)
                heapq.heappush(queue, (estimated_cost, neighbor))

    return []


def parse_metadata(metadata: str) -> dict[str, str]:
    """
    Parse a metadata string into a dictionary of key-value pairs.
    Metadata format: "key1=value1 key2=value2 ...". Used to extract hub properties
    like zone type, color, and capacities from map files.

    Args:
        metadata: Space-separated string of key=value pairs.

    Returns:
        Dictionary mapping metadata keys to their values.
    """
    result: dict[str, str] = {}
    for item in metadata.split():
        if '=' in item:
            key, value = item.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def generate_drones(nb_drones: int) -> Generator:
    """
    Generator for initialized drone objects with default fields.
    Each drone is assigned a unique ID and default state for simulation.

    Args:
        nb_drones: Number of drones to generate.

    Yields:
        Dictionary representing a drone with initialized fields.
    """

    for i in range(nb_drones):
        yield {
            'id': f"D{i + 1}",
            'start_hub': "",
            'end_hub': "",
            'current_hub': "",
            'restricted': 0,
            'priority': 0,
            'path_idx': 0,
            'path': []
        }


def simulate_turns(drones: list[Dron], adjacencies: dict[str, list[str]],
                   hubs: dict[str, Hub], link_capacity: dict[tuple[str, str], int],
                   max_turns: int = 100) -> None:

    """
    Simulate drone movements turn by turn, enforcing all zone and link constraints.
    Handles occupancy, restricted zones, link capacities, and outputs each turn's
    movements in the required format with color feedback.

    Args:
        drones: List of drone objects.
        adjacencies: Graph structure of hub connections.
        hubs: Dictionary of hub properties.
        link_capacity: Dictionary of connection capacities.
        max_turns: Maximum number of simulation turns.

    Returns:
        None. Prints simulation output per turn.
    """
    for t in range(max_turns):
        occupancy = {}
        link_usage = {}
        movements = []
        drones = [d for d in drones if d['path'][d['path_idx']] != d['end_hub']]
        if not drones:
            print(f"Turns: {t}")
            break

        # Bucle de movimientos
        for d in drones:
            actual_hub = d['path'][d['path_idx']]
            text_color_actual_hub = COLOR_MAP.get(hubs[actual_hub]['color'], Color.RESET)

            # Si estoy quieto, imprimo mi posicion, y paso
            if d['restricted'] > 0:
                movements.append(f"{d['id']}-{text_color_actual_hub}{actual_hub}{Color.RESET}")
                d['restricted'] -= 1
                continue

            next_hub = d['path'][d['path_idx'] + 1]
            text_color_next_hub = COLOR_MAP.get(hubs[next_hub]['color'], Color.RESET)
            current_occupancy = occupancy.get(next_hub, 0)

            # Si el siguiente está completo, no avanzo
            if current_occupancy >= hubs[next_hub]['max_drones']:
                continue

            actual_next_hub: tuple(str, str) = (actual_hub, next_hub)
            if actual_next_hub not in link_usage:
                link_usage[actual_next_hub] = 0
            link_usage[actual_next_hub] += 1

            # Avanzo si el siguiente no está completo
            if link_usage[actual_next_hub] <= link_capacity[actual_next_hub]:
                occupancy[next_hub] = current_occupancy + 1
                d['path_idx'] += 1

            if hubs[next_hub]['zone'] == Zones.RESTRICTED.value:
                d['restricted'] = 1
                movements.append(f"{d['id']}-{text_color_actual_hub}{actual_hub}-{text_color_next_hub}{next_hub}{Color.RESET}")
            else:
                movements.append(f"{d['id']}-{text_color_next_hub}{next_hub}{Color.RESET}")

        if movements:
            print(' '.join(movements))


def parse_map(map_path: str):
    """
    Parse map file, build hubs and connections, initialize drones, and start simulation.
    Handles all parsing rules, metadata extraction, and error handling for robust operation.

    Args:
        map_path: Path to the map file to parse.

    Returns:
        None. Initiates simulation after successful parsing.
    """

    start_name: str = ""
    end_name: str = ""
    hubs: dict[str, Hub] = {}
    adjacencies: dict[str, list[str]] = {}
    link_capacity: dict[tuple[str, str], int] = {}
    nb_drones: int = 0  # type: ignore
    try:
        with open(map_path, 'r') as file:
            print(f"Reading {map_path}")
            # Leer linea por linea del doc.
            for line in file:
                line: str = line.strip()

                # Ignorar lineas vacías y comentarios
                if not line or line.startswith('#'):
                    continue

                # Identificar variable 'nb_drones'
                if line.startswith('nb_drones'):
                    nb_drones: int = int(line.split(':')[1])  # type: ignore
                    dron: list[Dron] = list(generate_drones(nb_drones))

                # Identificar variable 'start_hub, end_hub', 'hub': Coordenadas
                elif line.startswith(('hub', 'start_hub', 'end_hub')):
                    parts: list[str] = line.split(':')
                    x_hub: str = parts[0]
                    data: list[str] = parts[1].split()

                    # Guardar path y coordenadas
                    path: str = data[0]
                    x: int = int(data[1])
                    y: int = int(data[2])

                    # Guardar el nombre del start/end hub
                    if x_hub == 'start_hub':
                        start_name = path
                    elif x_hub == 'end_hub':
                        end_name = path
                    # Crear dict con info del nodo
                    hub: Hub = {
                        'coord': (x, y),
                        'color': None,
                        'max_drones': 1,
                        'zone': 'normal'
                    }

                    # Identificar metadatos y guardarlos en el dict nodo
                    if '[' in line:
                        metadata = line.split('[')[1].split(']')[0]
                        result = parse_metadata(metadata)

                        if 'color' in result:
                            for color in Palette:
                                if color.value in result['color']:
                                    hub['color'] = result['color']

                        if 'zone' in result:
                            for zone in Zones:
                                if zone.value in result['zone']:
                                    hub['zone'] = result['zone']

                        if 'max_drones' in result:
                            hub['max_drones'] = int(result['max_drones'])

                    hubs[path] = hub

                elif line.startswith('connection'):
                    parts: list[str] = line.split(':')
                    data: list[str] = parts[1].split()
                    nodes: list[str] = data[0].split('-')

                    a: str = nodes[0].strip()
                    b: str = nodes[1].strip()

                    max_capacity = 1
                    if '[' in line:
                        metadata = line.split('[')[1].split(']')[0]
                        result = parse_metadata(metadata)
                        if 'max_link_capacity' in result:
                            max_capacity = int(result['max_link_capacity'])

                    link_key = tuple([a, b])
                    link_capacity[link_key] = max_capacity

                    if a not in adjacencies:
                        adjacencies[a] = []
                    if b not in adjacencies:
                        adjacencies[b] = []
                    adjacencies[a].append(b)
                    adjacencies[b].append(a)

        if not start_name or not end_name:
            return

        path_solved = find_path(hubs, adjacencies, start_name, end_name)
        for d in dron:
            d['start_hub'] = start_name
            d['end_hub'] = end_name
            d['current_hub'] = start_name
            d['path_idx'] = 0
            d['path'] = list(path_solved)

        simulate_turns(dron, adjacencies, hubs, link_capacity)

    except Exception as e:
        print(f"Error: {e}")


def main() -> None:
    """
    Entry point for the drone routing simulator.
    Validates command-line arguments, loads the map file, and starts the simulation.
    Prints error and usage instructions if arguments are missing.

    Args:
        None. Reads from sys.argv.

    Returns:
        None. Exits on error.
    """
    if len(sys.argv) < 2:
        print(f"{Color.ERROR}Error{Color.RESET}: Missing map file")
        print("Execute: make run MAP=<path>")
        sys.exit(1)

    map_path = sys.argv[1]
    print(f"Loading map: {map_path}")
    parse_map(map_path)


if __name__ == "__main__":
    main()
