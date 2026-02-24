from typing import Generator
from domain.entities import Drone


class DroneFactory:
    """
    Factory class for creating Drone instances.

    Provides methods to generate drones for simulation.
    """

    @staticmethod
    def generate_drones(nb_drones: int) \
            -> Generator[Drone, None, None]:
        for i in range(nb_drones):
            yield Drone(id=f"D{i+1}", start_hub="", end_hub="")
