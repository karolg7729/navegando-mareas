"""
Prototipo: Navegando mareas - Estrategias de navegación en un catálogo
Patrones: Composite, Iterator, Strategy, Command, Observer
Uso:  python prototipo_navegacion.py          (menú interactivo)
      python prototipo_navegacion.py --demo   (demostración automática)
"""
import sys
import time
import random
from abc import ABC, abstractmethod
from collections import deque


# ---------------- COMPOSITE ----------------
class CatalogNode(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def children(self):
        ...


class Product(CatalogNode):
    def __init__(self, name, popularity):
        super().__init__(name)
        self.popularity = popularity

    def children(self):
        return []

    def __str__(self):
        return f"[Producto] {self.name} (popularidad {self.popularity})"


class Category(CatalogNode):
    def __init__(self, name):
        super().__init__(name)
        self._children = []

    def add(self, node):
        self._children.append(node)
        return node

    def children(self):
        return self._children

    def __str__(self):
        return f"[Categoría] {self.name} ({len(self._children)} elementos)"


# ---------------- ITERATOR ----------------
class CatalogIterator:
    """Recorrido en amplitud (por niveles)."""
    def __init__(self, root):
        self._queue = deque([root])

    def __iter__(self):
        return self

    def __next__(self):
        if not self._queue:
            raise StopIteration
        node = self._queue.popleft()
        self._queue.extend(node.children())
        return node


class DepthIterator:
    """Recorrido en profundidad."""
    def __init__(self, root):
        self._stack = [root]

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stack:
            raise StopIteration
        node = self._stack.pop()
        self._stack.extend(reversed(node.children()))
        return node


# ---------------- OBSERVER ----------------
class Observer(ABC):
    @abstractmethod
    def update(self, event):
        ...


class MetricsObserver(Observer):
    def __init__(self):
        self.records = []

    def update(self, event):
        self.records.append(event)

    def summary(self):
        if not self.records:
            return "Sin métricas registradas."
        n = len(self.records)
        pasos = sum(r["pasos"] for r in self.records)
        nodos = sum(r["nodos"] for r in self.records)
        t = sum(r["tiempo_ms"] for r in self.records)
        return (f"Navegaciones: {n} | Pasos totales: {pasos} | "
                f"Nodos visitados: {nodos} | Tiempo total: {t:.3f} ms")


# ---------------- STRATEGY ----------------
class INavigationStrategy(ABC):
    name = "base"

    @abstractmethod
    def navigate(self, root, query):
        """Devuelve (resultados, nodos_visitados, pasos)."""
        ...


class CategoryStrategy(INavigationStrategy):
    """Desciende por la ruta de categorías: 'Electrónica/Celulares'."""
    name = "Por categoría"

    def navigate(self, root, query):
        node, visited, steps = root, 1, 0
        for part in [p.strip().lower() for p in query.split("/") if p.strip()]:
            steps += 1
            nxt = None
            for ch in node.children():
                visited += 1
                if ch.name.lower() == part:
                    nxt = ch
                    break
            if nxt is None:
                return [], visited, steps
            node = nxt
        return [str(c) for c in node.children()[:10]], visited, steps


class SearchStrategy(INavigationStrategy):
    """Búsqueda por palabra clave usando el iterador en profundidad."""
    name = "Por búsqueda"

    def navigate(self, root, query):
        found, visited = [], 0
        for node in DepthIterator(root):
            visited += 1
            if isinstance(node, Product) and query.lower() in node.name.lower():
                found.append(str(node))
                if len(found) == 10:
                    break
        return found, visited, 1


class PopularityStrategy(INavigationStrategy):
    """Los productos más populares (atajo directo)."""
    name = "Por popularidad"

    def navigate(self, root, query):
        prods, visited = [], 0
        for node in CatalogIterator(root):
            visited += 1
            if isinstance(node, Product):
                prods.append(node)
        prods.sort(key=lambda p: p.popularity, reverse=True)
        return [str(p) for p in prods[:5]], visited, 1


class StrategyManager:
    def __init__(self):
        self._strategies = {
            "1": CategoryStrategy(),
            "2": SearchStrategy(),
            "3": PopularityStrategy(),
        }

    def get(self, key):
        return self._strategies[key]

    def register(self, key, strategy):  # extensible sin modificar lo existente
        self._strategies[key] = strategy


# ---------------- COMMAND ----------------
class Command(ABC):
    @abstractmethod
    def execute(self):
        ...

    @abstractmethod
    def undo(self):
        ...


class NavigateCommand(Command):
    def __init__(self, controller, strategy, query):
        self.controller = controller
        self.strategy = strategy
        self.query = query
        self.previous = None

    def execute(self):
        self.previous = self.controller.current_view
        self.controller._run(self.strategy, self.query)

    def undo(self):
        self.controller.current_view = self.previous
        print("  << Se deshizo la navegación. Vista anterior restaurada.")
        self.controller.show()


class HistoryManager:
    def __init__(self):
        self._done, self._undone = [], []

    def run(self, cmd):
        cmd.execute()
        self._done.append(cmd)
        self._undone.clear()

    def undo(self):
        if not self._done:
            print("  No hay nada que deshacer.")
            return
        cmd = self._done.pop()
        cmd.undo()
        self._undone.append(cmd)

    def redo(self):
        if not self._undone:
            print("  No hay nada que rehacer.")
            return
        cmd = self._undone.pop()
        cmd.execute()
        self._done.append(cmd)


# ---------------- CONTROLADOR (Observer subject) ----------------
class NavigationController:
    def __init__(self, root):
        self.root = root
        self.history = HistoryManager()
        self.manager = StrategyManager()
        self._observers = []
        self.current_view = []

    def attach(self, obs):
        self._observers.append(obs)

    def _notify(self, event):
        for o in self._observers:
            o.update(event)

    def _run(self, strategy, query):
        t0 = time.perf_counter()
        results, visited, steps = strategy.navigate(self.root, query)
        ms = (time.perf_counter() - t0) * 1000
        self.current_view = results
        self._notify({"estrategia": strategy.name, "consulta": query,
                      "pasos": steps, "nodos": visited, "tiempo_ms": ms})
        self.show()
        print(f"  [Métrica] {strategy.name}: {steps} pasos, "
              f"{visited} nodos visitados, {ms:.3f} ms")

    def navigate(self, key, query):
        cmd = NavigateCommand(self, self.manager.get(key), query)
        self.history.run(cmd)

    def show(self):
        if not self.current_view:
            print("  (sin resultados)")
        for r in self.current_view:
            print("   -", r)


def baseline(root, target):
    """Navegación única (sin estrategias): recorre todo el catálogo en orden."""
    visited = 0
    for node in CatalogIterator(root):
        visited += 1
        if node.name.lower() == target.lower():
            break
    return visited


# ---------------- DATOS ----------------
def build_catalog():
    random.seed(7)
    root = Category("Catálogo")
    data = {
        "Electrónica": ["Celulares", "Computadores", "Audio", "Televisores"],
        "Hogar": ["Cocina", "Muebles", "Decoración", "Iluminación"],
        "Deportes": ["Ciclismo", "Fútbol", "Natación", "Gimnasio"],
        "Libros": ["Ficción", "Tecnología", "Historia", "Ciencia"],
    }
    for cat, subs in data.items():
        c = root.add(Category(cat))
        for sub in subs:
            s = c.add(Category(sub))
            for i in range(1, 16):
                s.add(Product(f"{sub} modelo {i}", random.randint(1, 100)))
    return root


# ---------------- EJECUCIÓN ----------------
def demo():
    root = build_catalog()
    ctrl = NavigationController(root)
    metrics = MetricsObserver()
    ctrl.attach(metrics)

    print("=== DEMO: catálogo de 4 categorías, 16 subcategorías, 240 productos ===\n")
    print(">> Navegación única (sin estrategias) hasta 'Gimnasio':")
    v = baseline(root, "Gimnasio")
    print(f"  Nodos visitados: {v}\n")

    print(">> Estrategia 1: Por categoría -> Deportes/Gimnasio")
    ctrl.navigate("1", "Deportes/Gimnasio")
    print("\n>> Estrategia 2: Por búsqueda -> 'ciclismo modelo 1'")
    ctrl.navigate("2", "ciclismo modelo 1")
    print("\n>> Estrategia 3: Por popularidad")
    ctrl.navigate("3", "")
    print("\n>> DESHACER (Command/HistoryManager)")
    ctrl.history.undo()
    print("\n>> REHACER")
    ctrl.history.redo()
    print("\n=== RESUMEN DE MÉTRICAS (Observer) ===")
    print(metrics.summary())


def interactive():
    root = build_catalog()
    ctrl = NavigationController(root)
    metrics = MetricsObserver()
    ctrl.attach(metrics)
    while True:
        print("\n--- Menú ---\n1. Por categoría (ej: Deportes/Gimnasio)\n"
              "2. Por búsqueda\n3. Por popularidad\n4. Deshacer\n"
              "5. Rehacer\n6. Métricas\n0. Salir")
        op = input("Opción: ").strip()
        if op in ("1", "2"):
            ctrl.navigate(op, input("Consulta: "))
        elif op == "3":
            ctrl.navigate("3", "")
        elif op == "4":
            ctrl.history.undo()
        elif op == "5":
            ctrl.history.redo()
        elif op == "6":
            print(metrics.summary())
        elif op == "0":
            break


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else interactive()
