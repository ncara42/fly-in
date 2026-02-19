import sys
from typing import TypedDict, Any
from enum import Enum
from src.Colors import Color, Palette
import heapq
import math


class Dron(TypedDict):
    id: str
    start_hub: str
    end_hub: str
    current_hub: str
    path_idx: int
    path: list[Any]


class Hub(TypedDict):
    coord: tuple[int, int]
    color: None | str
    max_drones: int
    zone: str


class Connection(TypedDict):
    nodes: list[str]
    max_link_capacity: int


class Zones(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


def heuristic(hubs: dict[str, Hub], node: str, end: str) -> float:
    # Distancias (euclidiana) entre coordenadas de cada nodo
    # Parte del algoritmo A*. Superior a BFS: Explora
    # todos los caminos al mismo tiempo
    # Superior A*: Calcula el coste de cada ruta
    # A* Elegirá entre la suma más baja
    (x1, y1) = hubs[node]['coord']
    (x2, y2) = hubs[end]['coord']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def find_path(hubs: dict[str, Hub], adjacencies: dict[str, list[str]],
              start: str, end: str) -> list[Any]:

    # Como Python siempre mira el primer elemento de una tupla
    # para decidir cual es menor, uso 0 al principio
    queue: list[tuple[float, str]] = [(0.0, start)]

    # came_from va a guardar el camino que se va a tomar desde el final
    # hasta el inicio. Luego se le dará la vuelta
    came_from: dict[str, str] = {}
    g_score: dict[str, float] = {node: float('inf') for node in hubs}
    g_score[start] = 0.0

    while queue:
        # Uso _ porque no usaré esta variable, solo
        # para desempaquetar el valor que me interesa en
        # current, que es justo la que uso
        # heapq.heappop saca el más pequeño de la lista
        # ej. queue = [(8.07, 'B'), (4.23, 'C')]
        # Resultado:
        # _ valdrá 4.23
        # current valdrá 'C'
        _, current = heapq.heappop(queue)


        # Ahora suponiendo que current vale C y end vale D
        # tengo que comprobar si C es el final. Cuando sea
        # el final, este bloque se ejecutará
        # Este bloque da la vuelta a came_from, por lo que
        # obtengo el path de inicio a fin
        if current == end:
            path: list[str] = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        # Aquí me quedo. Seguir comentando aquí
        for neighbor in adjacencies.get(current, []):
            if hubs[neighbor]['zone'] == Zones.BLOCKED.value:
                continue
            if hubs[neighbor]['zone'] == Zones.BLOCKED.value:
                continue

            tentative_g = g_score[current] + 1

            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(hubs, neighbor, end)
                heapq.heappush(queue, (f_score, neighbor))

    return []


def parse_metadata(metadata: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in metadata.split():
        if '=' in item:
            key, value = item.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def generate_drones(nb_drones: int) -> dict[str, Dron]:

    for i in range(nb_drones):
        yield {
            'id': f"G0{i}",
            'start_hub': "",
            'end_hub': "",
            'current_hub': "",
            'path_idx': 0,
            'path': []
        }

def simulate_turns(drones: Dron, hubs: Hub):
    ### Me quedo aqui
    return 


def parse_map(map_path: str):

    start_name: str = ""    
    end_name: str = ""
    hubs: dict[str, Hub] = {}
    adjacencies: dict[str, list[str]] = {}
    nb_drones: int = 0  # type: ignore
    drones: list[dict[str, Any]]

    connection: Connection = {
        'connections': [],
        'mlc': 0
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

            # Crear una lista de nodos conectados:
            # Dónde pueden acceder (por eso usamos .append()!)
            elif line.startswith('connection'):
                parts: list[str] = line.split(':')
                data: list[str] = parts[1].split()
                nodes: list[str] = data[0].split('-')

                u: str = nodes[0]
                v: str = nodes[1]

                if u not in adjacencies:
                    adjacencies[u] = []
                if v not in adjacencies:
                    adjacencies[v] = []
                adjacencies[u].append(v)
                adjacencies[v].append(u)

        if not start_name and not end_name:
            return

        path_solved = find_path(hubs, adjacencies, start_name, end_name)
        for d in dron:
            d['start_hub'] = start_name
            d['end_hub'] = end_name
            d['current_hub'] = start_name
            d['path_idx'] = 0
            d['path'] = list(path_solved)

        simulate_turns(dron, hubs)


        print(*dron, sep="\n")


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
