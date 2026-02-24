from typing import Sequence
from domain.entities import Drone, Hub, Zones
from domain.services import RoutingService, SimulationService, DroneFactory


class MapParser:
    """Parser for map files that delegates work to service objects.

    The previous implementation instantiated the routing, simulation and
    factory services as globals at module import time. that approach leaks
    state between different uses and prevents easy testing or reuse with
    alternative implementations. instead, the dependencies are injected via
    the constructor; callers (for example :mod:`main`) can supply specific
    instances or let the parser create its own defaults.
    """

    def __init__(self,
                 routing_service: RoutingService,
                 simulation_service: SimulationService,
                 drone_factory: DroneFactory):

        self.routing = routing_service
        self.simulation = simulation_service
        self.drone_factory = drone_factory

    def parse_metadata(self, metadata: str) -> dict[str, str]:
        """
        Parses a metadata string into a dictionary of key-value pairs.
        Metadata format: "key1=value1 key2=value2 ...". Used to extract hub
        properties such as zone type, color, and capacities from map files.

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

    def parse_map(self, map_path: str) -> None:
        """
        Parses the map file, builds hubs and connections, initializes drones,
        and starts the simulation. Handles all parsing rules,
        metadata extraction, and error handling for robust operation.

        Args:
            map_path: Path to the map file to parse.

        Returns:
            None. Initiates simulation after successful parsing.
        """

        start_name: str = ""
        end_name: str = ""
        hubs: dict[str, Hub] = {}
        drones: list[Drone] = []
        adjacencies: dict[str, list[str]] = {}
        link_capacity: dict[tuple[str, str], int] = {}
        nb_drones: int = 0

        try:
            with open(map_path, 'r') as file:
                print(f"Reading {map_path}")
                # Leer linea por linea del doc.
                for line in file:
                    line = line.strip()

                    # Ignorar lineas vacías y comentarios
                    if not line or line.startswith('#'):
                        continue

                    # Identificar variable 'nb_drones'
                    if line.startswith('nb_drones'):
                        nb_drones = int(line.split(':')[1].strip())

                        # Si es negativo: raise
                        if nb_drones < 0:
                            raise ValueError(
                                "'nb_drones' must be a positive number"
                            )
                        for d in self.drone_factory.generate_drones(nb_drones):
                            drones.append(d)

                    # Identificar variable 'hub', 'start_hub, end_hub'
                    elif line.startswith(('hub', 'start_hub', 'end_hub')):
                        parts: Sequence[str] = line.split(':')
                        x_hub: str = parts[0]
                        data: Sequence[str] = parts[1].split()

                        # Guardar path (hub_name) y coordenadas
                        path: str = data[0]
                        x: int = int(data[1])
                        y: int = int(data[2])

                        # Guardar el nombre del start/end hub
                        if x_hub == 'start_hub':
                            start_name = path
                        elif x_hub == 'end_hub':
                            end_name = path

                        # Crear nuevo (@dataclass) Hub con info del nodo
                        hub = Hub(
                            name=path,
                            coord=(x, y),
                            color=None,
                            max_drones=1,
                            zone=Zones.NORMAL
                        )

                        # Identificar metadatos y guardarlos en hub anterior
                        if '[' in line:
                            metadata = line.split('[')[1].split(']')[0]
                            result = self.parse_metadata(metadata)
                            # Añadir metadata con hub.set_metadata()
                            hub.set_metadata(result)

                        if path in hubs:
                            raise Exception("Zones can't be repeated")
                        elif '-' in path or ' ' in path:
                            raise ValueError(
                                f"{path} name don't support spaces and hyphen"
                            )
                        hubs[path] = hub

                    elif line.startswith('connection'):
                        parts = line.split(':')
                        data = parts[1].split()
                        nodes: Sequence[str] = data[0].split('-')

                        # hub_a - hub_b
                        a: str = nodes[0].strip()
                        b: str = nodes[1].strip()

                        # Si max_capacity está en la metadata de connection
                        max_capacity = 1
                        if '[' in line:
                            metadata = line.split('[')[1].split(']')[0].strip()
                            result = self.parse_metadata(metadata)
                            if 'max_link_capacity' in result:
                                max_capacity = int(result['max_link_capacity'])

                        # Si es negativo: raise
                        if max_capacity < 0:
                            raise ValueError(
                                "'max_capacity' must be a positive integer"
                            )

                        # Para comprobar link_capacity es necesario guardar las
                        # conexiones en un dict. Luego se comparan
                        link_key: tuple[str, str] = (a, b)
                        if link_key in link_capacity \
                                or link_key[::-1] in link_capacity:
                            raise ValueError("Connections can't be duplicated")
                        link_capacity[link_key] = max_capacity

                        # Adjacencies guardan los caminos desde cada nodo
                        adjacencies.setdefault(a, []).append(b)
                        adjacencies.setdefault(b, []).append(a)

            if not start_name or not end_name:
                return

            path_solved: list[str] = self.routing.find_path(hubs,
                                                            adjacencies,
                                                            hubs[start_name],
                                                            hubs[end_name])

            for d in drones:
                d.start_hub = start_name
                d.end_hub = end_name
                d.path_idx = 0
                d.path = path_solved
                d.restricted = 0

            self.simulation.simulate_turns(
                drones, adjacencies, hubs, link_capacity
            )

        except Exception as e:
            print(f"Error: {e}")
