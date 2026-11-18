# Navegando mareas: Estrategias de navegación en un catálogo

Prototipo funcional en Python que mejora la navegación de un catálogo de productos aplicando patrones de diseño (Gamma et al., 1994).

## Problema

- Recorridos largos para llegar a un producto.
- Una sola forma de navegar.
- Poca reversibilidad: el usuario no puede deshacer ni rehacer.

## Patrones de diseño aplicados

| Patrón | Clases | Problema que resuelve |
|---|---|---|
| Composite | CatalogNode, Category, Product | El catálogo es un árbol de categorías y productos |
| Iterator | CatalogIterator, DepthIterator | Recorrer el catálogo sin exponer su estructura |
| Strategy | INavigationStrategy, CategoryStrategy, SearchStrategy, PopularityStrategy, StrategyManager | Una sola forma de navegar |
| Command | Command, NavigateCommand, HistoryManager | Deshacer y rehacer navegaciones |
| Observer | Observer, MetricsObserver, NavigationController | Medir el desempeño sin acoplarlo a la navegación |

## Requisitos

- Python 3.8 o superior (no requiere librerías externas).

## Ejecución

```bash
# Demostración automática
python prototipo_navegacion.py --demo

# Menú interactivo
python prototipo_navegacion.py
```

## Resultados de la demo

- Navegación única hasta «Gimnasio»: 17 nodos visitados.
- Estrategia por categoría hasta «Gimnasio»: 8 nodos y 2 pasos.
- Deshacer y rehacer restauran correctamente la vista anterior.
- El Observer registra pasos, nodos y tiempo de cada navegación.

La salida completa está en `evidencia_ejecucion.txt`.

## Estructura del repositorio

```
.
├── README.md
├── prototipo_navegacion.py
├── evidencia_ejecucion.txt
└── docs/
    ├── Figura2_Diagrama_de_secuencia.png
    ├── Figura3_Diagrama_de_clases.png
    └── Tabla1_Patrones_de_diseno.png
```

## Autor

Nombre del estudiante · Curso · Institución · 2026
