import networkx as nx
import json
import random
import sys
import math

try:
    from scipy.spatial import Delaunay
    import numpy as np
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Scipy не найден. Установите: pip install scipy")
    sys.exit(1)

def generate_random_planar_graph(n, seed=None):
    """
    Генерирует случайный планарный граф через триангуляцию Делоне.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Генерируем случайные точки в квадрате [0,1] x [0,1]
    points = np.random.rand(n, 2)
    
    # Строим триангуляцию Делоне
    tri = Delaunay(points)
    
    # Создаём граф
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    # Добавляем рёбра из триангуляции
    for simplex in tri.simplices:
        # Приводим индексы к обычному int
        u = int(simplex[0])
        v = int(simplex[1])
        w = int(simplex[2])
        
        # Добавляем рёбра
        if not G.has_edge(u, v):
            G.add_edge(u, v)
        if not G.has_edge(v, w):
            G.add_edge(v, w)
        if not G.has_edge(u, w):
            G.add_edge(u, w)
    
    return G

def graph_to_json(G, filename):
    """
    Сохраняет граф в JSON-файл.
    """
    data = {
        "vertices": list(G.nodes()),
        "edges": [[int(u), int(v)] for u, v in G.edges()]  # явное приведение к int
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    n = 10
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Использование: python generate_graph.py [число_вершин]")
            sys.exit(1)
    
    # Генерируем граф (без seed, каждый раз разный)
    G = generate_random_planar_graph(n)
    filename = f"graph_{n}.json"
    graph_to_json(G, filename)
    print(f"Случайный планарный граф с {n} вершинами сохранён в {filename}")
    print(f"Число рёбер: {G.number_of_edges()}")

if __name__ == "__main__":
    main()