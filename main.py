import sys
from typing import TypedDict, Any
from enum import Enum
from src.Colors import *

class Dron(TypedDict):
    id: str
    start_hub: str
    end_hub: str
    path: list[Any]


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


def find_path(adjacencies: dict[str, list[str]], start: str, end: str) -> list[Any]:
    queue: list[list[str]] = [[start]]
    visited: set[Any] = set()

    while queue:
        path: list[str] = queue.pop(0)
        node = path[-1]

        if node == end:
            return path

        if node not in visited:
            for neighbor in adjacencies.get(node, []):
                if neighbor not in path:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
            visited.add(node)
    return []


def parse_metadata(metadata: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for item in metadata.split():
           if '=' in item:
               key, value = item.split('=', 1)
               result[key.strip()] = value.strip()
        return result


def parse_map(map_path: str):

    hubs: dict[str, Hub] = {}
    adjacencies: dict[str, list[str]] = {}
    nb_drones: int = 0  # type: ignore

    dron: Dron = {
        'id': "G01",
        'start_hub': "",
        'end_hub': "",
        'path': []
    }

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
            
            # Identificar variable 'start_hub, end_hub': Coordenadas
            elif line.startswith(('start_hub', 'end_hub')):
                parts: list[str] = line.split(':')
                x_hub: str = parts[0]
                data: list[str] = parts[1].split()

                # Guardar path y coordenadas
                path: str = data[0]
                x: int = int(data[1])
                y: int = int(data[2])

                # Guardar el nodo inicial y final en el dict dron
                if x_hub == 'start_hub':
                    dron['start_hub'] = path
                elif x_hub == 'end_hub':
                    dron['end_hub'] = path
        
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
                    for color in Palette:
                        if color.value in metadata:
                            hub['color'] = result['color']
                    for zone in Zones:
                        if zone.value in metadata:
                            hub['zone'] = result['zone']
                    if 'max_drones' in metadata:
                        hub['max_drones'] = int(result['max_drones'])

                # IA??? Tengo mis dudas sobre esto honestamente:
                # Me lo hizo por un error de tipado con hubs (bloque de arriba)
                # pero no tengo claro por qué tomó la decision de guardar esta info
                # Store the parsed hub in the hubs mapping
                hubs[path] = hub
                print(hubs)

            # Crear una lista de nodos conectados:
            # Dónde pueden acceder (por eso usamos .append()!)
            elif line.startswith('connection'):
                nodes: list[str] = line.split(':')[1].strip().split('-')
                u: str = nodes[0]
                v: str = nodes[1]
                if u not in adjacencies:
                    adjacencies[u] = []
                if v not in adjacencies:
                    adjacencies[v] = []
                adjacencies[u].append(v)
                adjacencies[v].append(u)

    # Aquí ocurre la solución
    path_solved = find_path(adjacencies, dron['start_hub'], dron['end_hub'])
    dron['path'] = path_solved
    print(adjacencies)
    print(path_solved)

def main() -> None:
    if len(sys.argv) < 2:
        print(f"{Color.ERROR}Error{Color.RESET}: Missing map file")
        print("Execute: make run MAP=<path>")
        sys.exit(1)

    map_path = sys.argv[1]
    print(f"Loading map: {map_path}")
    parse_map(map_path)


if __name__ == "__main__":
    main()
