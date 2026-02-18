# Fly-In

**Estudiante:** ncaravac  
**Campus:** 42 Madrid, España <br>
**Período:** Febrero 2026  
**Lenguaje:** Python ^3.10

---

> **PROYECTO EN DESARROLLO** - Este proyecto se encuentra actualmente en progreso y no está completo.

## Descripción

Sistema de enrutamiento de drones diseñado para navegar múltiples drones a través de hubs conectados, minimizando giros y evitando colisiones. El sistema permite definir mapas con zonas especiales, restricciones de capacidad y prioridades.

## Funcionalidades Implementadas

- **Parser de mapas**: Lectura y análisis de archivos de configuración de mapas
- **Sistema de hubs**: Definición de nodos con coordenadas y metadatos
  - Zonas configurables (normal, bloqueada, restringida, prioritaria)
  - Límite de drones por hub
  - Colores personalizables
- **Conexiones entre hubs**: Sistema de grafo con conexiones bidireccionales
- **Búsqueda de rutas**: Algoritmo BFS para encontrar caminos entre puntos
- **Sistema de colores**: Módulo de utilidades para salida visual en consola

## Estructura del Proyecto

```
fly-in/
├── main.py          # Punto de entrada principal
├── src/
│   └── Colors.py    # Definiciones de colores y paletas
├── maps/
│   └── map.txt      # Archivo de ejemplo de mapa
├── pyproject.toml   # Configuración del proyecto y dependencias
├── .gitignore       # Evita subir /__pycache__/ y otros
├── README.md        # Este archivo
└── Makefile         # Comandos de automatización
```

## Instalación

```bash
make install
```

## Uso

```bash
make run MAP=maps/map.txt
```

## Dependencias

- Python ^3.10
- colored ^2.3.1
- matplotlib ^3.10.8
- rich ^14.3.2 

---

## Información de Contacto

**GitHub:** [ncara42](https://github.com/ncara42)  
**42 Network:** [42 Madrid](https://www.42madrid.com/)

---

*Documento para fines de portfolio profesional. Todos los ejercicios fueron completados de forma individual siguiendo la normativa y valores de 42.*

