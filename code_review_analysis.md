# Análisis de Código - Proyecto Fly-In
**Fecha:** 21 de Febrero, 2026  
**Estudiante:** ncaravac  
**Revisor:** GitHub Copilot

---

## 📋 Resumen Ejecutivo

Tu proyecto tiene una **base sólida** con implementación funcional del parser, pathfinding básico y simulación. Sin embargo, **faltan elementos críticos** del subject para considerarlo completo, especialmente en:
- Visualización (obligatoria según VII.1)
- Formato de salida de simulación (VII.5)
- Manejo de capacidad de conexiones
- Validación exhaustiva del parser
- Documentación completa del código
- README según especificaciones

**Estado General:** 🟡 **En Desarrollo** - Funcional pero incompleto

---

## ✅ Aspectos Correctos

### 1. **Estructura del Proyecto** ✅
- Organización clara con `src/` para módulos
- Uso de `pyproject.toml` con Poetry
- `.gitignore` presente
- Makefile implementado

### 2. **Parser Básico** ✅
- Lectura correcta de `nb_drones`
- Identificación de `start_hub`, `end_hub`, `hub`
- Parsing de conexiones bidireccionales
- Parsing de metadatos básico (color, zone, max_drones)

### 3. **Sistema de Tipos** ✅
- Uso de `TypedDict` para estructuras de datos
- Type hints en la mayoría de funciones
- Enum para zonas y colores
- Pasa `mypy` sin errores

### 4. **Algoritmo de Pathfinding** ✅
- Implementación de A* con heurística Manhattan
- Considera costes de zonas (normal=1, restricted=2)
- Evita zonas bloqueadas
- Recalculación dinámica de paths cuando hay bloqueos

### 5. **Gestión de Capacidad de Zonas** ✅ (Parcial)
- Tracking de ocupación por zona
- Respeta `max_drones` en zonas intermedias
- Recalcula paths cuando una zona está llena

---

## ❌ Problemas Críticos (Mandatory)

### 1. **❌ FORMATO DE SALIDA INCORRECTO** (VII.5)
**Problema:** Tu simulación imprime `D1-hub1` en líneas separadas en lugar de agrupar por turno.

**Especificación del Subject:**
```
Each simulation turn is represented by a line.
A line must list all the drone movements that occur during that turn, space-separated.
```

**Ejemplo esperado:**
```
D1-roof1 D2-corridorA D3-roof1
D1-roof2 D2-tunnelB D4-corridorA
D1-goal D2-goal D3-roof2
```

**Tu código actual:**
```python
# Línea 166 - INCORRECTO
for d, next_hub in planned_moves:
    if d['current_hub'] != d['end_hub']:
        occupancy[d['current_hub']] -= 1
    d['current_hub'] = next_hub
    d['path_idx'] += 1
    if hubs[next_hub]['zone'] == Zones.RESTRICTED.value:
        d['restricted'] = 2
```

**Solución requerida:**
```python
# Recoger todos los movimientos del turno
turn_moves: list[str] = []

for d, next_hub in planned_moves:
    if d['current_hub'] != d['end_hub']:
        occupancy[d['current_hub']] -= 1
    d['current_hub'] = next_hub
    d['path_idx'] += 1
    turn_moves.append(f"{d['id']}-{next_hub}")
    if hubs[next_hub]['zone'] == Zones.RESTRICTED.value:
        d['restricted'] = 2

# Imprimir todos los movimientos del turno en una línea
if turn_moves:
    print(" ".join(turn_moves))
```

---

### 2. **❌ FALTA VISUALIZACIÓN** (VII.1 - Obligatorio)
**Problema:** No hay implementación de visualización gráfica ni coloreada en terminal.

**Especificación del Subject:**
> Your implementation must provide visual feedback of the simulation, either through:
> - Colored terminal output showing drone movements and zone states
> - A graphical interface displaying the network and drone positions
> - Both options for enhanced user experience

**Lo que tienes:**
- Módulo `Colors.py` definido pero no usado en la simulación
- No hay representación visual del estado de cada turno

**Lo que falta implementar:**
1. **Salida coloreada en terminal** mostrando:
   - Estado de cada zona (ocupada/libre)
   - Movimientos de drones con colores
   - Zonas con sus colores definidos
   
2. **O interfaz gráfica** usando matplotlib/pygame/rich para mostrar:
   - Red de zonas
   - Posición de drones en tiempo real
   - Animación de movimientos

**Ejemplo de implementación básica con colores:**
```python
def print_turn_visual(turn: int, drones: list[Dron], hubs: dict[str, Hub]) -> None:
    print(f"\n{Color.BLUE}=== Turn {turn} ==={Color.RESET}")
    
    # Mostrar estado de cada zona
    for hub_name, hub_data in hubs.items():
        drones_here = [d['id'] for d in drones if d['current_hub'] == hub_name]
        if drones_here:
            color = get_color_for_hub(hub_data)
            print(f"{color}{hub_name}: {', '.join(drones_here)}{Color.RESET}")
```

---

### 3. **❌ NO MANEJA CAPACIDAD DE CONEXIONES** (VII.2, VII.3)
**Problema:** El parser ignora `max_link_capacity` en las conexiones.

**Especificación del Subject:**
> Connection capacity (max_link_capacity) defined on connections limits how many drones can traverse the same connection simultaneously.

**Tu código actual:**
```python
# Línea 281 - Solo parseas pero no almacenas max_link_capacity
elif line.startswith('connection'):
    parts: list[str] = line.split(':')
    data: list[str] = parts[1].split()
    nodes: list[str] = data[0].split('-')
    # No parseas el metadata de las conexiones
```

**Solución requerida:**
1. Cambiar estructura de datos de adjacencies:
```python
# En lugar de dict[str, list[str]]
adjacencies: dict[str, dict[str, dict[str, Any]]] = {}
# Ejemplo: adjacencies['A']['B'] = {'max_capacity': 2}
```

2. Parsear metadata de conexiones:
```python
elif line.startswith('connection'):
    parts = line.split(':')
    data = parts[1].split()
    nodes = data[0].split('-')
    
    max_capacity = 1  # Default
    if '[' in line:
        metadata = line.split('[')[1].split(']')[0]
        result = parse_metadata(metadata)
        if 'max_link_capacity' in result:
            max_capacity = int(result['max_link_capacity'])
    
    # Guardar con capacidad
    if u not in adjacencies:
        adjacencies[u] = {}
    if v not in adjacencies:
        adjacencies[v] = {}
    adjacencies[u][v] = {'max_capacity': max_capacity}
    adjacencies[v][u] = {'max_capacity': max_capacity}
```

3. Verificar capacidad durante simulación antes de mover drones.

---

### 4. **❌ MOVIMIENTO A ZONAS RESTRICTED INCOMPLETO** (VII.3)
**Problema:** El manejo de zonas restricted no sigue las reglas del subject completamente.

**Especificación del Subject:**
> Move to a connection towards a restricted zone (that requires 2 turns to be reached). 
> In this case, the drone MUST reach its destination during the next turn. 
> It can't wait extra turns on the connection.

**Tu implementación actual:**
```python
# Línea 172 - Solo marca el contador pero no maneja el estado "en conexión"
if hubs[next_hub]['zone'] == Zones.RESTRICTED.value:
    d['restricted'] = 2
```

**Problemas:**
1. No distingues entre estar "en la conexión" vs estar "en espera"
2. El output debería mostrar `D1-hub1-hub2` (conexión) no `D1-hub2`
3. No verificas que el drone DEBE moverse el siguiente turno (no puede esperar)

**Solución requerida:**
1. Añadir estado al drone: `in_transit_to: str | None`
2. En el output, mostrar conexión: `D1-hub1-restricted_zone`
3. Forzar movimiento en el siguiente turno (no permitir espera)

---

### 5. **❌ VALIDACIÓN DE PARSER INSUFICIENTE** (VII.4)
**Especificación del Subject:**
> Any parsing error must stop the program and return a clear error message indicating the line and cause.

**Validaciones que faltan:**
- ✅ Línea 1 debe ser `nb_drones` (no validado)
- ✅ Exactamente un `start_hub` y un `end_hub` (no validado)
- ✅ Nombres de zona únicos (no validado)
- ✅ Conexiones solo entre zonas definidas (no validado)
- ✅ Conexiones duplicadas (no validado)
- ✅ Tipos de zona válidos (no validado)
- ✅ Capacidades como enteros positivos (no validado)
- ✅ Nombres sin guiones o espacios (no validado)

**Ejemplo de validación necesaria:**
```python
def validate_map_file(map_path: str) -> None:
    """Valida que el archivo de mapa cumple con las especificaciones."""
    with open(map_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    
    # Validar primera línea
    if not lines or not lines[0].startswith('nb_drones:'):
        raise ValueError("Error línea 1: Primera línea debe definir 'nb_drones'")
    
    # Validar zonas duplicadas, etc.
    # ... más validaciones
```

---

### 6. **❌ FALTA DOCUMENTACIÓN CON DOCSTRINGS** (III.1)
**Especificación del Subject:**
> Include docstrings in functions and classes following PEP 257 (e.g., Google or NumPy style)

**Tu código actual:**
```python
# Línea 33 - Sin docstring
def heuristic(hubs: dict[str, Hub], node: str, end: str) -> float:
    # Solo comentarios inline
    (x1, y1) = hubs[node]['coord']
    ...
```

**Solución requerida:**
```python
def heuristic(hubs: dict[str, Hub], node: str, end: str) -> float:
    """
    Calcula la distancia Manhattan entre dos nodos.
    
    Forma parte del algoritmo A* para estimar el coste hasta el objetivo.
    
    Args:
        hubs: Diccionario de todos los hubs con sus coordenadas
        node: Nombre del nodo actual
        end: Nombre del nodo objetivo
        
    Returns:
        float: Distancia Manhattan (|x2-x1| + |y2-y1|)
        
    Example:
        >>> heuristic({'A': {'coord': (0,0)}, 'B': {'coord': (3,4)}}, 'A', 'B')
        7.0
    """
    (x1, y1) = hubs[node]['coord']
    (x2, y2) = hubs[end]['coord']
    return abs(x2 - x1) + abs(y2 - y1)
```

**Aplica a todas las funciones:** `find_path`, `parse_metadata`, `generate_drones`, `simulate_turns`, `parse_map`, `main`.

---

### 7. **❌ MAKEFILE INCOMPLETO** (III.2)
**Tu Makefile actual:**
```makefile
.PHONY: install run lint clean

install:
	poetry install

run:
	$(PYTHON) main.py $(MAP)

lint:
	poetry run flake8 .
	poetry run mypy .

clean:
	rm -rf `find . -name __pycache__`
	rm -rf .mypy_cache
```

**Problemas:**
1. ❌ **Falta regla `debug`**: Debe ejecutar con pdb
2. ❌ **Lint no tiene flags obligatorios**: Falta `--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
3. ❌ **Falta regla opcional `lint-strict`**

**Solución:**
```makefile
PYTHON = poetry run python
MAP = maps/example_map.txt

.PHONY: install run debug lint lint-strict clean

install:
	poetry install

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

lint:
	poetry run flake8 .
	poetry run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	poetry run flake8 .
	poetry run mypy . --strict

clean:
	rm -rf `find . -name __pycache__`
	rm -rf .mypy_cache
```

---

### 8. **❌ README INCOMPLETO** (VIII)
**Especificación del Subject:**
> The very first line must be italicized and read: 
> This project has been created as part of the 42 curriculum by <login1>

**Tu README actual:**
```markdown
# Fly-In

**Estudiante:** ncaravac  
```

**Problemas:**
1. ❌ **No empieza con la línea obligatoria en cursiva**
2. ❌ **Falta sección "Resources" con uso de IA**
3. ❌ **Falta descripción detallada del algoritmo**
4. ❌ **Falta documentación de visualización**

**Solución:**
```markdown
# Fly-In

*This project has been created as part of the 42 curriculum by ncaravac.*

## Description

[Tu descripción actual...]

## Instructions

### Installation
```bash
make install
```

### Usage
```bash
make run MAP=maps/01_the_impossible_dream.txt
```

### Debug
```bash
make debug MAP=maps/example.txt
```

## Algorithm

### Pathfinding Strategy
Este proyecto implementa el algoritmo A* para encontrar rutas óptimas...

[Explicación detallada de tu algoritmo]

### Visual Representation
[Describir cómo se visualiza la simulación]

## Resources

### Documentation
- [A* Algorithm - Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Python Type Hints - PEP 484](https://peps.python.org/pep-0484/)
- [Flake8 Documentation](https://flake8.pycqa.org/)

### AI Usage
Durante el desarrollo de este proyecto, se utilizó IA para:
- **Code Review**: Revisión de code quality y sugerencias de mejora
- **Documentation**: Ayuda con formato de docstrings PEP 257
- **Debugging**: Identificación de edge cases en el parser
- **Algorithm Research**: Conceptos de pathfinding y optimización

Todas las implementaciones fueron comprendidas, verificadas y validadas antes de su integración.
```

---

## 🟡 Problemas Menores

### 1. **Optimización del Algoritmo** 🟡
**Observación:** Usas A* que es correcto, pero hay margen de mejora para cumplir los benchmarks.

**Sugerencias:**
- Implementar Dijkstra con múltiples paths simultáneos
- Considerar el uso de max-flow algorithms para mapas complejos
- Pre-calcular paths y cachearlos (mencionar en README para bonus)

### 2. **Manejo de Excepciones** 🟡
**Código actual:**
```python
# Línea 212 - Sin try-except
with open(map_path, 'r') as file:
```

**Mejora sugerida:**
```python
try:
    with open(map_path, 'r') as file:
        # ...
except FileNotFoundError:
    print(f"{Color.ERROR}Error: File '{map_path}' not found{Color.RESET}")
    sys.exit(1)
except PermissionError:
    print(f"{Color.ERROR}Error: Permission denied to read '{map_path}'{Color.RESET}")
    sys.exit(1)
```

### 3. **Type Hints Inconsistentes** 🟡
**Problemas encontrados:**
```python
# Línea 111 - Generator sin tipo específico
def generate_drones(nb_drones: int) -> Generator:
    # Debería ser:
def generate_drones(nb_drones: int) -> Generator[dict[str, Any], None, None]:

# Línea 219 - Reasignación con type ignore
nb_drones: int = 0  # type: ignore
# Luego:
nb_drones: int = int(line.split(':')[1])  # type: ignore
```

**Solución:**
```python
def generate_drones(nb_drones: int) -> Generator[dict[str, Any], None, None]:
    """Genera drones inicializados."""
    for i in range(nb_drones):
        yield {...}

# En parse_map:
nb_drones: int = 0  # Inicialización válida
# ...
nb_drones = int(line.split(':')[1])  # Sin type: ignore
```

### 4. **Falta Gestión de Prioridades** 🟡
**Problema:** Las zonas `priority` no están siendo preferidas en pathfinding.

**Tu código:**
```python
# Línea 91 - Solo ajusta coste pero no prioriza en A*
zone_cost = 1
if hubs[neighbor]['zone'] == Zones.RESTRICTED.value:
    zone_cost = 2
```

**Sugerencia:**
```python
zone_cost = 1
if hubs[neighbor]['zone'] == Zones.RESTRICTED.value:
    zone_cost = 2
elif hubs[neighbor]['zone'] == Zones.PRIORITY.value:
    zone_cost = 0.8  # Reducir coste para priorizarla
```

### 5. **Tests Ausentes** 🟡
**Problema:** No hay archivos de test (`test_*.py`).

**Especificación del Subject (III.3):**
> Create test programs to verify project functionality (not submitted or graded). 
> Use frameworks like pytest or unittest.

**Crear:**
```python
# tests/test_parser.py
import pytest
from main import parse_metadata, parse_map

def test_parse_metadata():
    result = parse_metadata("zone=restricted color=red")
    assert result['zone'] == 'restricted'
    assert result['color'] == 'red'

def test_invalid_zone_type():
    with pytest.raises(ValueError):
        # Test con zona inválida
        pass
```

---

## 📊 Checklist de Completitud

### Mandatory Requirements
| Requisito | Estado | Prioridad |
|-----------|--------|-----------|
| Parser completo con validaciones (VII.4) | 🟡 Parcial | 🔴 ALTA |
| Formato de salida correcto (VII.5) | ❌ Incorrecto | 🔴 ALTA |
| Visualización (VII.1) | ❌ Ausente | 🔴 ALTA |
| Capacidad de conexiones (VII.2) | ❌ No implementado | 🔴 ALTA |
| Movimiento restricted correcto (VII.3) | 🟡 Parcial | 🟠 MEDIA |
| Docstrings PEP 257 (III.1) | ❌ Ausente | 🟠 MEDIA |
| Makefile completo (III.2) | 🟡 Parcial | 🟠 MEDIA |
| README según spec (VIII) | 🟡 Parcial | 🟠 MEDIA |
| Type safety completo (III.1) | 🟡 Parcial | 🟢 BAJA |
| Manejo de excepciones (III.1) | 🟡 Parcial | 🟢 BAJA |

### Bonus Requirements
| Requisito | Estado |
|-----------|--------|
| Performance benchmarks | ❌ No testeado |
| Challenger map | ❌ No intentado |
| Tests unitarios | ❌ Ausente |

---

## 🎯 Plan de Acción Recomendado

### Fase 1: Correcciones Críticas (Prioridad Alta)
**Tiempo estimado: 4-6 horas**

1. **✅ Corregir formato de salida** (1h)
   - Agrupar movimientos por turno en una línea
   - Implementar correctamente el output según VII.5

2. **✅ Implementar visualización básica** (2h)
   - Añadir salida coloreada en terminal
   - Mostrar estado de zonas por turno
   - Usar el módulo `Colors.py` existente

3. **✅ Añadir capacidad de conexiones** (1-2h)
   - Modificar estructura de adjacencies
   - Parsear `max_link_capacity`
   - Validar en simulación

4. **✅ Completar validaciones del parser** (1h)
   - Añadir todas las validaciones de VII.4
   - Mensajes de error claros con número de línea

### Fase 2: Mejoras Obligatorias (Prioridad Media)
**Tiempo estimado: 3-4 horas**

5. **✅ Añadir docstrings** (1-2h)
   - Documentar todas las funciones
   - Seguir estilo Google o NumPy

6. **✅ Completar Makefile** (30min)
   - Añadir regla `debug`
   - Corregir flags de `lint`
   - Añadir `lint-strict`

7. **✅ Actualizar README** (1h)
   - Línea inicial obligatoria
   - Sección de algoritmo detallada
   - Sección Resources con uso de IA

8. **✅ Mejorar movimiento restricted** (1h)
   - Implementar estado "en tránsito"
   - Forzar movimiento en siguiente turno
   - Output correcto para conexiones

### Fase 3: Pulido y Tests (Prioridad Baja)
**Tiempo estimado: 2-3 horas**

9. **✅ Añadir manejo de excepciones** (30min)
   - Try-except en file I/O
   - Validaciones adicionales

10. **✅ Corregir type hints** (30min)
    - Generator con tipos completos
    - Eliminar `# type: ignore`

11. **✅ Crear tests básicos** (1-2h)
    - Tests de parser
    - Tests de pathfinding
    - Tests de edge cases

### Fase 4: Optimización (Opcional - Bonus)
**Tiempo estimado: Variable**

12. **✅ Optimizar para benchmarks**
    - Testear con todos los mapas
    - Mejorar algoritmo si es necesario
    - Documentar resultados

13. **✅ Intentar Challenger map**
    - Solo si tienes tiempo
    - Investigar algoritmos avanzados

---

## 💡 Recomendaciones Adicionales

### Código Limpio
- ✅ **Buenos nombres de variables**: Claros y descriptivos
- ⚠️ **Evitar números mágicos**: Línea 127 `max_turns: int = 500` - considera hacerlo configurable
- ✅ **Funciones cortas**: La mayoría están bien, pero `simulate_turns` y `parse_map` podrían dividirse

### Arquitectura
- Considera separar en módulos:
  - `src/parser.py` - Funciones de parsing
  - `src/pathfinding.py` - Algoritmos A*, Dijkstra
  - `src/simulation.py` - Lógica de simulación
  - `src/visualizer.py` - Sistema de visualización
  
### Testing
- Crea mapas pequeños de test personalizados
- Testea edge cases:
  - 0 drones
  - 1 drone
  - Mapa sin solución
  - Todas las zonas bloqueadas
  - Capacidades extremas

### Performance
- Considera cachear paths calculados
- Evita recalcular A* en cada turno si no es necesario
- Usa estructuras de datos eficientes (heapq está bien)

---

## 📝 Conclusión

Tu proyecto tiene una **base técnica sólida** con:
- ✅ Algoritmo A* bien implementado
- ✅ Parser funcional (aunque incompleto)
- ✅ Type safety básico
- ✅ Gestión de capacidad de zonas

Sin embargo, **no está listo para evaluación** debido a:
- ❌ Formato de output incorrecto (crítico)
- ❌ Falta visualización obligatoria (crítico)
- ❌ Capacidad de conexiones no implementada (crítico)
- ❌ Validaciones de parser insuficientes
- ❌ Documentación incompleta

**Tiempo estimado para completar mandatory:** 9-13 horas de trabajo enfocado.

**Prioriza:**
1. Formato de salida correcto
2. Visualización básica con colores
3. Capacidad de conexiones
4. Validaciones del parser
5. Docstrings y README

Una vez completadas estas correcciones críticas, tendrás un proyecto que cumple con todos los requisitos mandatory y podrás enfocarte en optimización para los bonus.

---

## 🔗 Enlaces Útiles

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [A* Algorithm Visualization](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [Rich Library - Terminal Colors](https://rich.readthedocs.io/)
- [Flake8 Rules](https://www.flake8rules.com/)

---

**¡Mucho ánimo con las correcciones! Tu base es buena, solo necesitas completar los requisitos obligatorios. 🚀**
