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


def heuristic(hubs: dict[str, Hub], node: str, end: str) -> float:
    # Distancias (euclidiana) entre coordenadas de cada nodo
    # Parte del algoritmo A*. Superior a BFS: Explora todos los caminos al mismo tiempo
    # Superior A*: Calcula el coste de cada ruta
    # A* Elegirá entre la suma más baja
    (x1, y1) = hubs[node]['coord']
    (x2, y2) = hubs[end]['coord']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def find_path(hubs: dict[str, Hub], adjacencies: dict[str, list[str]], start: str, end: str) -> list[Any]:
    
    # Como Python siempre mira el primer elemento de una tupla
    # para decidir cual es menor, uso 0 al principio
    queue = [(0, start)]

    # came_from va a guardar el camino que se va a tomar desde el final
    # hasta el inicio. Luego se le dará la vuelta 
    came_from = {}
    g_score: dict[str, float] = {node: float('inf') for node in hubs}
    g_score[start] = 0

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
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]


        ###### Aquí me quedo. Seguir comentando aquí
        for neighbor in adjacencies.get(current, []):
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
            
            # Identificar variable 'start_hub, end_hub', 'hub': Coordenadas
            elif line.startswith(('hub', 'start_hub', 'end_hub')):
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

                hubs[path] = hub

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
    path_solved = find_path(hubs, adjacencies, dron['start_hub'], dron['end_hub'])
    dron['path'] = path_solved
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
