*This project has been created as part of the 42 curriculum by ncaravac.*

# Fly-in

**Student:** ncaravac <br>
**Campus:** 42 Madrid, Spain <br>
**Period:** February 2026 <br>
**Language:** Python ^3.10 <br>

---

## Description
Fly-in is an object-oriented drone routing simulation system. It efficiently routes a fleet of drones from a central base to a destination, navigating a dynamic network of zones under strict movement and capacity constraints. The project is written in Python 3.10+, fully typed, and complies with flake8 and mypy standards.

## Instructions

### Requirements
- Python 3.10 or later
- Poetry

### Installation
```sh
make install
```

### Run the simulation
To run the simulation with a specific map:
```sh
make run MAP=maps/easy/01_linear_path.txt
```
Change the map file as needed.

### Debug mode
```sh
make debug MAP=maps/easy/01_linear_path.txt
```

### Linting and type checking
```sh
make lint
make lint-strict
```

### Clean cache
```sh
make clean
```

## Features
- **Object-oriented design:** All logic is encapsulated in classes.
- **Strict typing:** Full type annotations and mypy compliance.
- **Custom parser:** Reads map files with flexible metadata and robust error handling.
- **Pathfinding:** Distributes drones across multiple paths, prioritizes 'priority' zones, and avoids deadlocks/conflicts. Dynamically replans if a path is blocked.
- **Simulation engine:** Manages drone movement, zone and link capacities, and turn mechanics. Prevents collisions and ensures maximum throughput.
- **Visual feedback:** Colored terminal output for drone movements and zone states.
- **Makefile automation:** For install, run, debug, lint, and clean tasks.

## Algorithm & Implementation
- **Pathfinding:** The system distributes drones across multiple paths, prioritizing 'priority' zones and avoiding deadlocks/conflicts. It dynamically replans if a path is blocked.
- **Simulation:** Drones move turn by turn, respecting zone and link capacities. The engine prevents collisions, deadlocks, and ensures optimal throughput.
- **Parser:** Strictly validates map file syntax, metadata, and constraints. Reports errors with line and cause, and suggests corrections for common typos (e.g., 'restric' → 'restricted').
- **Visuals:** Terminal colors are mapped according to zone metadata for clear, real-time feedback.

## Visual Representation
- Each simulation turn is printed as a line, showing all drone movements with colored zone names.
- Zone occupancy and link usage are displayed for each turn.
- Colors are mapped according to the zone's metadata for easy visual tracking.

## Resources
- [Python documentation](https://docs.python.org/3/)
- [flake8](https://flake8.pycqa.org/)
- [mypy](http://mypy-lang.org/)
- [Algorithm A*](https://es.wikipedia.org/wiki/Algoritmo_A*)
- [ANSI](https://es.wikipedia.org/wiki/C%C3%B3digo_de_escape_ANSI)

AI was consulted to better understand pathfinding algorithms, and to help refactor, simplify, and make certain parts of the code more efficient and professional. Suggestions from AI were used for code structure, error handling, and improving documentation clarity.

---

## Contact Information

**GitHub:** [ncara42](https://github.com/ncara42)  
**42 Network:** [42 Madrid](https://www.42madrid.com/)

---

*Document for professional portfolio purposes. All exercises were completed individually following the rules and values of 42.*
