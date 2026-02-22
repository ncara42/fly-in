import sys
from typing import TypedDict, Any, Generator
from enum import Enum
from src.Colors import Color, Palette, COLOR_MAP
import heapq
import math


class Dron(TypedDict):
    id: str
    start_hub: str
    end_hub: str
    current_hub: str
    restricted: int
    path_idx: int
    path: list[str]


class Hub(TypedDict):
    coord: tuple[int, int]
    color: None | str
    max_drones: int
    zone: str

class Zones(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


def heuristic(hubs: dict[str, Hub], node: str, end: str) -> float:
    """
    Calculate the Manhattan distance heuristic between two nodes.
    
    Used as part of the A* algorithm to estimate the cost from a node
    to the goal. Manhattan distance is the sum of absolute differences
    of their coordinates.
    
    Args:
        hubs: Dictionary mapping hub names to hub information including coordinates.
        node: Name of the current node.
        end: Name of the destination node.
        
    Returns:
        The Manhattan distance between the two nodes as a float.
        
    Example:
        >>> heuristic({'A': {'coord': (0,0)}, 'B': {'coord': (3,4)}}, 'A', 'B')
        7.0
    """
    (x1, y1) = hubs[node]['coord']
    (x2, y2) = hubs[end]['coord']

    return abs(x2 - x1) + abs(y2 - y1)

def find_path(hubs: dict[str, Hub], adjacencies: dict[str, list[str]],
              start: str, end: str) -> list[Any]:
    """
    Find the shortest path between two hubs using the A* algorithm.
    
    Implements A* pathfinding with Manhattan distance heuristic. Takes into
    account different zone costs:
    - Normal zones: cost 1 turn
    - Restricted zones: cost 2 turns
    - Priority zones: cost 0.5 turns (preferred)
    - Blocked zones: avoided completely
    
    Args:
        hubs: Dictionary of hub names to hub information.
        adjacencies: Graph structure mapping each hub to its connected neighbors.
        start: Starting hub name.
        end: Destination hub name.
        
    Returns:
        List of hub names representing the optimal path from start to end.
        Returns empty list if no path exists.
        
    Example:
        >>> find_path(hubs, adjacencies, 'start', 'goal')
        ['start', 'hub1', 'hub2', 'goal']
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
    Parse metadata string into a dictionary of key-value pairs.
    
    Metadata format: "key1=value1 key2=value2 ..."
    Used to extract hub properties like zone type, color, and capacities.
    
    Args:
        metadata: Space-separated string of key=value pairs.
        
    Returns:
        Dictionary mapping metadata keys to their values.
        
    Example:
        >>> parse_metadata("zone=restricted color=red max_drones=2")
        {'zone': 'restricted', 'color': 'red', 'max_drones': '2'}
    """
    result: dict[str, str] = {}
    for item in metadata.split():
        if '=' in item:
            key, value = item.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def generate_drones(nb_drones: int) -> Generator:
    """
    Generate initialized drone objects.
    
    Creates drone dictionaries with default values. Each drone is assigned
    a unique ID starting from D1.
    
    Args:
        nb_drones: Number of drones to generate.
        
    Yields:
        Dictionary representing a drone with initialized fields:
        - id: Unique drone identifier (D1, D2, ...)
        - start_hub: Starting hub name (empty initially)
        - end_hub: Destination hub name (empty initially)
        - current_hub: Current position (empty initially)
        - restricted: Turns remaining in restricted zone transit
        - priority: Priority level for movement ordering
        - path_idx: Current position in the path
        - path: List of hubs forming the route
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

def search_color(color: str) -> str:
    return COLOR_MAP.get(str, 0)

def simulate_turns(drones: list[Dron], adjacencies: dict[str, list[str]],
                   hubs: dict[str, Hub], link_capacity: dict[tuple[str, str], int],
                   max_turns: int = 100) -> None:

    
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
            final_hub = d['end_hub']
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
    Parse a map file and initialize the drone simulation.
    
    Reads and parses the map file format containing:
    - Number of drones (nb_drones)
    - Hub definitions (start_hub, end_hub, hub) with coordinates and metadata
    - Connections between hubs with optional capacity constraints
    - Metadata includes: zone type, color, max_drones, max_link_capacity
    
    After parsing, initializes all drones with the optimal path and starts
    the simulation.
    
    Args:
        map_path: Path to the map file to parse.
        
    Returns:
        None. Initiates simulation after successful parsing.
        
    Raises:
        FileNotFoundError: If map file doesn't exist.
        ValueError: If map format is invalid or missing required fields.
        
    """

    start_name: str = ""
    end_name: str = ""
    hubs: dict[str, Hub] = {}
    adjacencies: dict[str, list[str]] = {}
    link_capacity: dict[tuple[str, str], int] = {}
    nb_drones: int = 0  # type: ignore
    drones: list[dict[str, Any]]
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
    Main entry point for the drone routing simulator.
    
    Validates command-line arguments and initiates the map parsing
    and simulation process.
    
    Command-line usage:
        python main.py <map_file_path>
        
    Args:
        None. Reads from sys.argv.
        
    Returns:
        None.
        
    Exits:
        1 if map file argument is missing.
        
    Example:
        $ python main.py maps/01_maze_nightmare.txt
        Loading map: maps/01_maze_nightmare.txt
        ...
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
