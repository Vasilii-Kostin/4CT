
import networkx as nx
import json
import matplotlib.pyplot as plt
import sys
import time
from itertools import combinations
from collections import defaultdict
from datetime import datetime
import os
import traceback
import re

# ============================================================
# НАСТРОЙКИ (меняйте здесь)
# ============================================================
MAX_VERTICES = 100
MAX_CYCLE_LENGTH = None
MAX_CYCLES_PER_VERTEX = 0
DEBUG = False
MAX_CHAIN_DEPTH = 20  # Ограничиваем глубину поиска до 20 треугольников
MAX_CHAINS_TO_FIND = 200  # Ограничиваем количество найденных цепочек
MAX_START_TRIANGLES = 100  # Ограничение стартовых треугольников (0 = все)
MAX_CHAINS_TO_DISPLAY = 200  # Сколько цепочек показывать в логе (0 = все)
LOG_TO_FILE = True
SAVE_STRUCTURE_IMAGES = True
# ============================================================

log_lines = []
error_occurred = False
coloring_success = False

def log_print(*args, **kwargs):
    import builtins
    line = ' '.join(str(arg) for arg in args)
    builtins.print(line, **kwargs)
    if LOG_TO_FILE:
        log_lines.append(line)

# ============================================================
# ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ ИЗОБРАЖЕНИЙ
# ============================================================

def save_original_graph(G, graph_name):
    """Сохраняет изображение исходного графа."""
    try:
        plt.figure(figsize=(14, 12))
        
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
        
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=400, edgecolors='black', linewidths=2)
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.5)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.title(f"Исходный граф\n{G.number_of_nodes()} вершин, {G.number_of_edges()} рёбер", fontsize=14, fontweight='bold')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{graph_name}_{timestamp}_original.png"
        
        # Создаём папку для изображений
        os.makedirs("images", exist_ok=True)
        filepath = os.path.join("images", filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        log_print(f"   📁 Сохранён исходный граф: {filepath}")
        return filepath
    except Exception as e:
        log_print(f"   ⚠️ Ошибка сохранения исходного графа: {e}")
        plt.close()
        return None

def save_color4_vertices_graph(G, color4_vertices, graph_name):
    """Сохраняет изображение графа с выделенными вершинами 4-го цвета."""
    try:
        plt.figure(figsize=(14, 12))
        
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
        
        # Все вершины серые
        all_nodes = list(G.nodes())
        nx.draw_networkx_nodes(G, pos, nodelist=all_nodes, 
                               node_color='lightgray', node_size=300, alpha=0.5)
        
        # Вершины 4-го цвета — фиолетовые
        if color4_vertices:
            nx.draw_networkx_nodes(G, pos, nodelist=list(color4_vertices),
                                   node_color='purple', node_size=500, alpha=1.0,
                                   edgecolors='black', linewidths=3)
        
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=1)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Легенда
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='purple', edgecolor='black', label='Вершины 4-го цвета'),
            Patch(facecolor='lightgray', edgecolor='black', label='Остальные вершины')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.title(f"Вершины 4-го цвета\n{len(color4_vertices)} вершин: {sorted(color4_vertices)}", 
                  fontsize=14, fontweight='bold')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{graph_name}_{timestamp}_color4_vertices.png"
        
        os.makedirs("images", exist_ok=True)
        filepath = os.path.join("images", filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        log_print(f"   📁 Сохранён граф с вершинами 4-го цвета: {filepath}")
        return filepath
    except Exception as e:
        log_print(f"   ⚠️ Ошибка сохранения графа с вершинами 4-го цвета: {e}")
        plt.close()
        return None

def save_final_colored_graph(G, colors, graph_name):
    """Сохраняет изображение финальной 4-цветной раскраски."""
    try:
        plt.figure(figsize=(14, 12))
        
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
        
        color_map = {0: 'red', 1: 'blue', 2: 'green', 3: 'purple'}
        
        # Группируем вершины по цветам
        colored_nodes = {0: [], 1: [], 2: [], 3: []}
        for v, color in colors.items():
            if color in colored_nodes:
                colored_nodes[color].append(v)
        
        # Рисуем рёбра
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=1)
        
        # Рисуем вершины каждого цвета
        for color, nodes in colored_nodes.items():
            if nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                       node_color=color_map[color], node_size=400,
                                       edgecolors='black', linewidths=2)
        
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Легенда
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', edgecolor='black', label='Цвет 0'),
            Patch(facecolor='blue', edgecolor='black', label='Цвет 1'),
            Patch(facecolor='green', edgecolor='black', label='Цвет 2'),
            Patch(facecolor='purple', edgecolor='black', label='Цвет 3 (4-й цвет)')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.title(f"Финальная 4-цветная раскраска\n{G.number_of_nodes()} вершин, {G.number_of_edges()} рёбер", 
                  fontsize=14, fontweight='bold')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{graph_name}_{timestamp}_final_colored.png"
        
        os.makedirs("images", exist_ok=True)
        filepath = os.path.join("images", filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        log_print(f"   📁 Сохранена финальная раскраска: {filepath}")
        return filepath
    except Exception as e:
        log_print(f"   ⚠️ Ошибка сохранения финальной раскраски: {e}")
        plt.close()
        return None

# ============================================================
# ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ ИЗОБРАЖЕНИЙ СТРУКТУР
# ============================================================

def save_structure_image(G, structure_info, graph_name, struct_type, struct_index, images_dir):
    """Сохраняет изображение графа с выделенной одной структурой."""
    try:
        structure_vertices = set()
        structure_edges = set()
        
        if struct_type == 'K4':
            structure_vertices = set(structure_info)
            for u, v in combinations(sorted(structure_info), 2):
                if G.has_edge(u, v):
                    structure_edges.add((u, v))
                    
        elif struct_type == 'S':
            center, cycle_nodes, cycle_edges = structure_info
            structure_vertices = {center} | set(cycle_nodes)
            structure_edges = set(cycle_edges)
            for v in cycle_nodes:
                if G.has_edge(center, v):
                    structure_edges.add((center, v))
                    
        elif struct_type == 'C':
            start_vertex, chain_vertices, chain_triangles = structure_info
            structure_vertices = set(chain_vertices)
            for tri in chain_triangles:
                edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]
                for u, v in edges:
                    if G.has_edge(u, v):
                        structure_edges.add((u, v))
        
        plt.figure(figsize=(12, 10))
        
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
        
        all_edges = list(G.edges())
        nx.draw_networkx_edges(G, pos, edgelist=all_edges, 
                               edge_color='lightgray', width=1, alpha=0.5)
        
        all_nodes = list(G.nodes())
        nx.draw_networkx_nodes(G, pos, nodelist=all_nodes, 
                               node_color='lightgray', node_size=200, alpha=0.5)
        
        if structure_vertices:
            color_map = {
                'K4': 'red',
                'S': 'blue', 
                'C': 'orange'
            }
            color = color_map.get(struct_type, 'green')
            
            nx.draw_networkx_nodes(G, pos, nodelist=list(structure_vertices),
                                   node_color=color, node_size=400, alpha=1.0)
            nx.draw_networkx_nodes(G, pos, nodelist=list(structure_vertices),
                                   node_color=color, node_size=400, 
                                   edgecolors='black', linewidths=2, alpha=1.0)
        
        if structure_edges:
            color_map = {
                'K4': 'darkred',
                'S': 'darkblue',
                'C': 'darkorange'
            }
            edge_color = color_map.get(struct_type, 'darkgreen')
            nx.draw_networkx_edges(G, pos, edgelist=list(structure_edges),
                                   edge_color=edge_color, width=3.0, alpha=1.0)
        
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        type_name = {'K4': 'K4', 'S': 'Нечётная звезда', 'C': 'Цепочка вынужденности'}.get(struct_type, struct_type)
        title = f"{type_name} #{struct_index}\nВершин: {len(structure_vertices)}, Рёбер: {len(structure_edges)}"
        plt.title(title, fontsize=14, fontweight='bold')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{graph_name}_{timestamp}_{struct_type}_{struct_index}.png"
        filepath = os.path.join(images_dir, filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        log_print(f"   📁 Сохранено изображение: {filepath}")
        return filepath
        
    except Exception as e:
        log_print(f"   ⚠️ Ошибка сохранения изображения структуры {struct_type}_{struct_index}: {e}")
        plt.close()
        return None

def save_chain_segment_image(G, chain_data, graph_name, struct_index, images_dir):
    """Сохраняет изображение сегмента цепочки с выделением конфликта."""
    try:
        # Распаковываем данные цепочки
        if len(chain_data) == 3:
            start_vertex, chain_vertices, chain_triangles = chain_data
            colors, color_history, conflict_desc = None, None, None
        elif len(chain_data) == 6:
            start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc = chain_data
        else:
            return None
        
        # Если нет конфликта или нет цветов, сохраняем всю цепочку
        if not conflict_desc or not colors:
            return save_structure_image(G, (start_vertex, chain_vertices, chain_triangles), 
                                       graph_name, 'C', struct_index, images_dir)
        
        # Находим сегмент конфликта
        start_idx, end_idx, segment = find_chain_conflict_segment(
            chain_triangles, conflict_desc, colors, color_history
        )
        
        # Если сегмент не найден или пустой, используем всю цепочку
        if segment is None or len(segment) == 0:
            segment = chain_triangles
            start_idx = 0
            end_idx = len(chain_triangles) - 1
        
        # Извлекаем конфликтующие вершины
        v1, v2 = None, None
        if "вершины" in conflict_desc:
            numbers = re.findall(r'\d+', conflict_desc)
            if len(numbers) >= 2:
                v1, v2 = int(numbers[0]), int(numbers[1])
        
        # Собираем вершины и рёбра ТОЛЬКО сегмента
        segment_vertices = set()
        segment_edges = set()
        for tri in segment:
            segment_vertices.update(tri)
            edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]
            for u, v in edges:
                if G.has_edge(u, v):
                    segment_edges.add((u, v))
        
        # Находим конфликтное ребро
        conflict_edge = None
        if v1 is not None and v2 is not None and G.has_edge(v1, v2):
            conflict_edge = (v1, v2)
        
        # Определяем стартовую вершину
        start_vertex_in_segment = start_vertex if start_vertex in segment_vertices else None
        
        plt.figure(figsize=(14, 12))
        
        # Позиционирование как в других функциях
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
        
        # Рисуем ВСЕ рёбра графа светло-серым (как в save_original_graph)
        all_edges = list(G.edges())
        nx.draw_networkx_edges(G, pos, edgelist=all_edges, 
                               edge_color='lightgray', width=1.0, alpha=0.5)
        
        # Рисуем ВСЕ вершины графа светло-голубым (как в save_original_graph)
        all_nodes = list(G.nodes())
        nx.draw_networkx_nodes(G, pos, nodelist=all_nodes, 
                               node_color='lightblue', node_size=300, alpha=0.6,
                               edgecolors='gray', linewidths=1)
        
        # Рисуем вершины СЕГМЕНТА ярко-голубым
        nx.draw_networkx_nodes(G, pos, nodelist=list(segment_vertices),
                               node_color='deepskyblue', node_size=400, alpha=0.9,
                               edgecolors='black', linewidths=2)
        
        # Рисуем рёбра СЕГМЕНТА синим
        if segment_edges:
            nx.draw_networkx_edges(G, pos, edgelist=list(segment_edges),
                                   edge_color='blue', width=2.5, alpha=0.8)
        
        # Выделяем конфликтное ребро красным (поверх всех рёбер)
        if conflict_edge:
            nx.draw_networkx_edges(G, pos, edgelist=[conflict_edge],
                                   edge_color='red', width=4.0, alpha=1.0)
        
        # Выделяем стартовую вершину оранжевым
        if start_vertex_in_segment is not None:
            nx.draw_networkx_nodes(G, pos, nodelist=[start_vertex_in_segment],
                                   node_color='orange', node_size=500,
                                   edgecolors='black', linewidths=3)
        
        # Выделяем конфликтующие вершины красным
        conflict_vertices = []
        if v1 is not None and v2 is not None:
            conflict_vertices = [v for v in [v1, v2] if v in segment_vertices]
            if conflict_vertices:
                nx.draw_networkx_nodes(G, pos, nodelist=conflict_vertices,
                                       node_color='red', node_size=500,
                                       edgecolors='black', linewidths=3)
        
        # Подписываем ВСЕ вершины графа
        labels = {v: str(v) for v in all_nodes}
        # Для конфликтующих вершин добавляем цвет
        if v1 is not None and v2 is not None:
            if v1 in labels and v1 in colors:
                labels[v1] = f"{v1}\n(цв.{colors[v1]})"
            if v2 in labels and v2 in colors:
                labels[v2] = f"{v2}\n(цв.{colors[v2]})"
        # Для стартовой вершины добавляем пометку
        if start_vertex_in_segment is not None and start_vertex_in_segment in labels:
            labels[start_vertex_in_segment] = f"{start_vertex_in_segment}\n★СТАРТ"
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        # Легенда
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='orange', edgecolor='black', label=f'Стартовая вершина: {start_vertex_in_segment}'),
            Patch(facecolor='red', edgecolor='black', label=f'Конфликтное ребро: {v1}-{v2}'),
            Patch(facecolor='red', edgecolor='black', label=f'Конфликтующие вершины: {v1}, {v2} (цвет {colors.get(v1, "?")})'),
            Patch(facecolor='deepskyblue', edgecolor='black', label='Вершины сегмента'),
            Patch(facecolor='lightblue', edgecolor='gray', label='Остальные вершины графа')
        ]
        plt.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        # Заголовок
        title = f"Цепочка #{struct_index}: сегмент конфликта\n"
        title += f"Треугольники {start_idx+1}-{end_idx+1} из {len(chain_triangles)} (всего {len(segment)} треугольников)"
        if conflict_edge and v1 is not None and v2 is not None:
            title += f"\n⚠️ КОНФЛИКТ: вершины {v1} и {v2} имеют одинаковый цвет {colors.get(v1, '?')}!"
        plt.title(title, fontsize=14, fontweight='bold')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{graph_name}_{timestamp}_C_{struct_index}_segment.png"
        filepath = os.path.join(images_dir, filename)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        log_print(f"   📁 Сохранён сегмент цепочки #{struct_index} ({len(segment)} треугольников): {filepath}")
        return filepath
        
    except Exception as e:
        log_print(f"   ⚠️ Ошибка сохранения сегмента цепочки #{struct_index}: {e}")
        import traceback
        log_print(traceback.format_exc())
        plt.close()
        return None

def save_all_structures_images(G, k4s, odd_stars, chains, graph_name):
    """Сохраняет изображения для всех структур в одну папку."""
    if not SAVE_STRUCTURE_IMAGES:
        return
    
    log_print("\n" + "="*50)
    log_print("🖼️ СОХРАНЕНИЕ ИЗОБРАЖЕНИЙ СТРУКТУР")
    log_print("="*50)
    
    images_dir = "structures_images"
    os.makedirs(images_dir, exist_ok=True)
    log_print(f"   Папка для изображений: {images_dir}")
    
    total_structures = len(k4s) + len(odd_stars) + len(chains)
    log_print(f"   Всего структур для сохранения: {total_structures}")
    
    saved_count = 0
    
    if k4s:
        log_print(f"\n   Сохраняем K4 ({len(k4s)} шт.)...")
        for idx, k4 in enumerate(k4s, 1):
            filepath = save_structure_image(G, k4, graph_name, 'K4', idx, images_dir)
            if filepath:
                saved_count += 1
    
    if odd_stars:
        log_print(f"\n   Сохраняем звёзды S ({len(odd_stars)} шт.)...")
        for idx, (center, cycle_nodes, cycle_edges) in enumerate(odd_stars, 1):
            structure_info = (center, cycle_nodes, cycle_edges)
            filepath = save_structure_image(G, structure_info, graph_name, 'S', idx, images_dir)
            if filepath:
                saved_count += 1
    
    if chains:
        log_print(f"\n   Сохраняем цепочки C ({len(chains)} шт.)...")
        for idx, chain_data in enumerate(chains, 1):
            # Используем новую функцию для сохранения сегмента
            filepath = save_chain_segment_image(G, chain_data, graph_name, idx, images_dir)
            if filepath:
                saved_count += 1
    
    log_print(f"\n✅ Сохранено изображений: {saved_count} из {total_structures}")
    log_print(f"📁 Все изображения сохранены в папку: {os.path.abspath(images_dir)}")
    log_print("="*50 + "\n")

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_edges_of_triangle(G, tri):
    """Возвращает список рёбер треугольника с указанием, есть ли они в графе."""
    edges_info = []
    edge_pairs = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]
    for u, v in edge_pairs:
        u_sorted, v_sorted = sorted([u, v])
        exists = G.has_edge(u, v)
        edges_info.append(f"{u_sorted}-{v_sorted} {'есть' if exists else 'НЕТ'}")
    return edges_info

def find_chain_conflict_segment(chain_triangles, conflict_desc, colors, color_history):
    """
    Находит сегмент цепочки, участвующий в конфликте.
    Определяет момент, когда впервые появляется ребро между конфликтующими вершинами.
    Возвращает (start_index, end_index, segment_triangles)
    """
    if "вершины" not in conflict_desc:
        return None, None, chain_triangles
    
    # Извлекаем номера конфликтующих вершин
    numbers = re.findall(r'\d+', conflict_desc)
    if len(numbers) < 2:
        return None, None, chain_triangles
    
    v1, v2 = int(numbers[0]), int(numbers[1])
    
    # Находим шаги, когда были раскрашены конфликтующие вершины
    step_v1 = color_history.get(v1, -1)
    step_v2 = color_history.get(v2, -1)
    
    if step_v1 == -1 or step_v2 == -1:
        return None, None, chain_triangles
    
    # Ищем треугольник, в котором впервые появляется РЕБРО между v1 и v2
    conflict_tri_index = None
    for i, tri in enumerate(chain_triangles):
        # Проверяем, есть ли ребро между конфликтующими вершинами в этом треугольнике
        if (v1 in tri and v2 in tri):
            # Проверяем, было ли это ребро уже в предыдущих треугольниках
            edge_exists_before = False
            for j in range(i):
                prev_tri = chain_triangles[j]
                if v1 in prev_tri and v2 in prev_tri:
                    edge_exists_before = True
                    break
            
            if not edge_exists_before:
                # Это первое появление ребра между v1 и v2
                conflict_tri_index = i
                break
    
    # Если не нашли треугольник с ребром, ищем по шагам (запасной вариант)
    if conflict_tri_index is None:
        # Ищем треугольник, который добавил позднюю вершину
        late_vertex = v2 if step_v2 > step_v1 else v1
        for i, tri in enumerate(chain_triangles):
            if late_vertex in tri:
                # Проверяем, есть ли в этом треугольнике другая конфликтующая вершина
                other_vertex = v1 if late_vertex == v2 else v2
                if other_vertex in tri:
                    conflict_tri_index = i
                    break
    
    if conflict_tri_index is None:
        # Если не нашли, берем последний треугольник с любой из вершин
        for i, tri in enumerate(chain_triangles):
            if v1 in tri or v2 in tri:
                conflict_tri_index = i
    
    if conflict_tri_index is None:
        return None, None, chain_triangles
    
    # Теперь ищем, где впервые появились конфликтующие вершины
    first_v1 = None
    first_v2 = None
    for i, tri in enumerate(chain_triangles):
        if first_v1 is None and v1 in tri:
            first_v1 = i
        if first_v2 is None and v2 in tri:
            first_v2 = i
        if first_v1 is not None and first_v2 is not None:
            break
    
    if first_v1 is None or first_v2 is None:
        return None, None, chain_triangles
    
    # Начало сегмента - первое появление любой из конфликтующих вершин
    start_idx = min(first_v1, first_v2)
    
    # Конец сегмента - треугольник, где впервые появилось ребро между ними
    end_idx = conflict_tri_index
    
    # Не добавляем контекст после конфликта, чтобы показать точный момент
    segment = chain_triangles[start_idx:end_idx + 1]
    
    return start_idx, end_idx, segment

def find_cycle_conflict(G, chain_triangles, colors, color_history):
    """
    Находит первый обнаруженный конфликт при замыкании цикла.
    Возвращает (есть_конфликт, описание_конфликта).
    """
    if len(chain_triangles) < 3:
        return False, "цепочка слишком короткая"
    
    # Проверяем конфликт с ребрами (две вершины одного цвета соединены ребром)
    color_groups = defaultdict(list)
    for v, color in colors.items():
        color_groups[color].append(v)
    
    # Ищем ПЕРВЫЙ конфликт и сразу возвращаем его
    for color, vertices in color_groups.items():
        if len(vertices) >= 2:
            for i in range(len(vertices)):
                for j in range(i + 1, len(vertices)):
                    v1, v2 = vertices[i], vertices[j]
                    if G.has_edge(v1, v2):
                        # Нашли первый конфликт - сразу возвращаем
                        return True, f"КОНФЛИКТ! вершины {v1} и {v2} имеют одинаковый цвет {color}, но между ними есть ребро!"
    
    # Если нет конфликта с ребрами - это не цепочка вынужденности
    return False, "замыкание корректно, конфликта нет"

def get_structure_description(struct_type, struct_data):
    try:
        if struct_type == 'k4':
            k4 = struct_data
            return f"K4: вершины {sorted(k4)}"
        elif struct_type == 'star':
            center, cycle_nodes, cycle_edges = struct_data
            return f"Нечётная звезда: центр {center}, вершины {sorted(cycle_nodes)}, рёбер {len(cycle_edges)}"
        elif struct_type == 'chain':
            start_vertex, chain_vertices, chain_triangles = struct_data
            return f"Цепочка: старт {start_vertex}, вершин {len(chain_vertices)}, треугольников {len(chain_triangles)}"
        return "Неизвестная структура"
    except Exception as e:
        return f"Ошибка описания структуры: {e}"

def analyze_structures(structures, edges_list):
    try:
        total_k4 = sum(1 for s in structures if s[0] == 'k4')
        total_stars = sum(1 for s in structures if s[0] == 'star')
        total_chains = sum(1 for s in structures if s[0] == 'chain')
        
        chain_sizes = []
        star_sizes = []
        k4_sizes = []
        
        for i, (struct_type, data) in enumerate(structures):
            try:
                if struct_type == 'k4':
                    k4_sizes.append(len(data))
                elif struct_type == 'star':
                    center, cycle_nodes, cycle_edges = data
                    star_sizes.append(len(cycle_nodes))
                elif struct_type == 'chain':
                    start_vertex, chain_vertices, chain_triangles = data
                    chain_sizes.append(len(chain_triangles))
            except:
                pass
        
        return {
            'total': len(structures),
            'k4': total_k4,
            'stars': total_stars,
            'chains': total_chains,
            'k4_sizes': k4_sizes,
            'star_sizes': star_sizes,
            'chain_sizes': chain_sizes
        }
    except Exception as e:
        log_print(f"⚠️ Ошибка анализа структур: {e}")
        return {'total': 0, 'k4': 0, 'stars': 0, 'chains': 0, 
                'k4_sizes': [], 'star_sizes': [], 'chain_sizes': []}

def print_structure_summary(structures, edges_list, title="Структуры"):
    try:
        stats = analyze_structures(structures, edges_list)
        
        log_print(f"\n{'='*60}")
        log_print(f"📊 {title}")
        log_print(f"{'='*60}")
        log_print(f"Всего структур: {stats['total']}")
        log_print(f"  K4: {stats['k4']}")
        log_print(f"  Нечётные звёзды: {stats['stars']}")
        log_print(f"  Цепочки вынужденности: {stats['chains']}")
        
        if stats['k4_sizes']:
            log_print(f"  K4 размеры: {sorted(stats['k4_sizes'])}")
        if stats['star_sizes']:
            log_print(f"  Размеры звёзд (вершин в цикле): {sorted(stats['star_sizes'])}")
        if stats['chain_sizes']:
            log_print(f"  Размеры цепочек (треугольников): {sorted(stats['chain_sizes'])}")
        
        k4_list = [s for s in structures if s[0] == 'k4']
        star_list = [s for s in structures if s[0] == 'star']
        chain_list = [s for s in structures if s[0] == 'chain']
        
        if k4_list:
            log_print(f"\n  K4 ({len(k4_list)}):")
            for i, struct in enumerate(k4_list, 1):
                desc = get_structure_description('k4', struct[1])
                log_print(f"    {i}. {desc}")
        
        if star_list:
            log_print(f"\n  Нечётные звёзды ({len(star_list)}):")
            for i, struct in enumerate(star_list, 1):
                desc = get_structure_description('star', (struct[1], struct[2], struct[3]))
                log_print(f"    {i}. {desc}")
        
        if chain_list:
            log_print(f"\n  Цепочки вынужденности ({len(chain_list)}):")
            for i, struct in enumerate(chain_list, 1):
                desc = get_structure_description('chain', (struct[1], struct[2], struct[4]))
                log_print(f"    {i}. {desc}")
        
        log_print(f"{'='*60}\n")
    except Exception as e:
        log_print(f"⚠️ Ошибка вывода сводки структур: {e}")

def load_graph_from_json(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        G = nx.Graph()
        G.add_nodes_from(data["vertices"])
        G.add_edges_from(data["edges"])
        return G
    except Exception as e:
        log_print(f"❌ Ошибка загрузки файла {filename}: {e}")
        raise

def find_all_k4(G):
    try:
        k4s = []
        nodes = list(G.nodes())
        for quartet in combinations(nodes, 4):
            subgraph = G.subgraph(quartet)
            if subgraph.number_of_edges() == 6:
                k4s.append(set(quartet))
        return k4s
    except Exception as e:
        log_print(f"⚠️ Ошибка поиска K4: {e}")
        return []

def find_all_odd_cycles_in_subgraph(sub, center=None):
    try:
        if sub.number_of_nodes() < 3:
            return []
        
        digraph = nx.DiGraph()
        for u, v in sub.edges():
            digraph.add_edge(u, v)
            digraph.add_edge(v, u)
        
        all_cycles = []
        seen_cycles = set()
        cycle_count = 0
        
        for cycle in nx.simple_cycles(digraph):
            if len(cycle) < 3:
                continue
            if MAX_CYCLE_LENGTH is not None and len(cycle) > MAX_CYCLE_LENGTH:
                continue
            
            cycle_edges = set()
            is_valid = True
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i + 1) % len(cycle)]
                if sub.has_edge(u, v):
                    cycle_edges.add((u, v))
                else:
                    is_valid = False
                    break
            
            if not is_valid:
                continue
            
            cycle_set = frozenset(cycle)
            if cycle_set not in seen_cycles:
                seen_cycles.add(cycle_set)
                if len(cycle) % 2 == 1:
                    all_cycles.append((set(cycle), cycle_edges))
                    cycle_count += 1
                    if MAX_CYCLES_PER_VERTEX > 0 and cycle_count >= MAX_CYCLES_PER_VERTEX:
                        break
        return all_cycles
    except Exception as e:
        log_print(f"⚠️ Ошибка поиска нечётных циклов: {e}")
        return []

def find_all_odd_stars(G, k4s):
    try:
        odd_stars = []
        k4_vertices = set()
        for k4 in k4s:
            k4_vertices.update(k4)
        
        for center in G.nodes():
            neighbors = list(G.neighbors(center))
            if len(neighbors) < 3:
                continue
            sub = G.subgraph(neighbors)
            cycles = find_all_odd_cycles_in_subgraph(sub, center)
            for cycle_nodes, cycle_edges in cycles:
                is_inside_k4 = False
                for k4 in k4s:
                    if cycle_nodes.issubset(k4):
                        is_inside_k4 = True
                        break
                if not is_inside_k4:
                    odd_stars.append((center, cycle_nodes, cycle_edges))
        return odd_stars
    except Exception as e:
        log_print(f"⚠️ Ошибка поиска нечётных звёзд: {e}")
        return []

def find_all_triangles(G):
    """Находит все реальные треугольники в графе."""
    try:
        triangles = []
        for u in G.nodes():
            for v in G.neighbors(u):
                if v <= u:
                    continue
                for w in G.neighbors(v):
                    if w <= v:
                        continue
                    if G.has_edge(u, w):
                        triangles.append((u, v, w))
        return triangles
    except Exception as e:
        log_print(f"⚠️ Ошибка поиска треугольников: {e}")
        return []

def get_common_edge(tri1, tri2):
    """Находит общее ребро между двумя треугольниками."""
    try:
        common = set(tri1) & set(tri2)
        if len(common) == 2:
            return tuple(sorted(common))
        return None
    except:
        return None

def get_triangles_by_edge(triangles):
    """Строит словарь: ребро -> список треугольников, содержащих это ребро."""
    try:
        edge_to_triangles = defaultdict(list)
        for tri in triangles:
            edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]
            for e in edges:
                e_sorted = tuple(sorted(e))
                edge_to_triangles[e_sorted].append(tri)
        return edge_to_triangles
    except Exception as e:
        log_print(f"⚠️ Ошибка построения словаря треугольников: {e}")
        return defaultdict(list)

def simulate_coloring_advanced(chain_triangles):
    """Симулирует 3-раскраску для цепочки треугольников."""
    try:
        colors = {}
        forced = {}
        color_history = {}
        
        start_tri = chain_triangles[0]
        
        colors[start_tri[0]] = 0
        color_history[start_tri[0]] = 0
        colors[start_tri[1]] = 1
        color_history[start_tri[1]] = 0
        colors[start_tri[2]] = 2
        color_history[start_tri[2]] = 0
        
        for i in range(1, len(chain_triangles)):
            tri = chain_triangles[i]
            prev_tri = chain_triangles[i - 1]
            
            common = get_common_edge(prev_tri, tri)
            if common is None:
                continue
            
            new_vertex = None
            for v in tri:
                if v not in common:
                    new_vertex = v
                    break
            
            if new_vertex is None:
                continue
            
            colors_common = []
            for v in common:
                if v in colors:
                    colors_common.append(colors[v])
                else:
                    if v in forced:
                        for c in range(3):
                            if c in forced[v]:
                                colors_common.append(c)
                                break
                        else:
                            colors_common.append(None)
                    else:
                        colors_common.append(None)
            
            if None in colors_common:
                continue
            
            used_colors = set(colors_common)
            
            if new_vertex in colors:
                if colors[new_vertex] not in used_colors:
                    return colors, True, forced, color_history
                continue
            
            forced_color = None
            for c in range(3):
                if c not in used_colors:
                    forced_color = c
                    break
            
            if forced_color is not None:
                if new_vertex not in forced:
                    forced[new_vertex] = set()
                forced[new_vertex].add(forced_color)
                color_history[new_vertex] = i
                
                if len(forced[new_vertex]) > 1:
                    return colors, True, forced, color_history
                
                if len(forced[new_vertex]) == 1:
                    colors[new_vertex] = next(iter(forced[new_vertex]))
        
        return colors, False, forced, color_history
    except Exception as e:
        log_print(f"⚠️ Ошибка симуляции раскраски: {e}")
        return None, False, {}, {}

def find_all_forced_chains(G):
    """
    Находит все замкнутые цепочки вынужденности с ограничениями.
    Сохраняет только цепочки с реальным конфликтом.
    """
    try:
        triangles = find_all_triangles(G)
        if not triangles:
            return []
        
        log_print(f"   Найдено реальных треугольников в графе: {len(triangles)}")
        log_print(f"   Максимальная глубина поиска: {MAX_CHAIN_DEPTH} треугольников")
        log_print(f"   Максимум стартовых треугольников: {MAX_START_TRIANGLES if MAX_START_TRIANGLES > 0 else 'все'}")
        log_print(f"   Максимум цепочек для поиска: {MAX_CHAINS_TO_FIND}")
        
        edge_to_triangles = get_triangles_by_edge(triangles)
        
        all_chains = []
        processed = set()
        chain_count = 0
        
        # Ограничиваем количество стартовых треугольников
        if MAX_START_TRIANGLES > 0:
            start_triangles = triangles[:MAX_START_TRIANGLES]
        else:
            start_triangles = triangles
        
        log_print(f"   Стартовых треугольников для обхода: {len(start_triangles)}")
        
        # Множество для хранения уже найденных конфликтов (чтобы не дублировать)
        found_conflicts = set()
        
        for start_tri in start_triangles:
            initial_chain = [start_tri]
            initial_vertices = set(start_tri)
            
            def dfs(current_chain, current_vertices, depth):
                nonlocal all_chains, processed, chain_count, found_conflicts
                
                # Ограничиваем количество найденных цепочек
                if len(all_chains) >= MAX_CHAINS_TO_FIND:
                    return
                
                # Проверяем замыкание
                if len(current_chain) >= 3:
                    first_tri = current_chain[0]
                    last_tri = current_chain[-1]
                    common = set(first_tri) & set(last_tri)
                    if common:
                        colors, conflict, forced, color_history = simulate_coloring_advanced(current_chain)
                        if conflict:
                            # Проверяем, есть ли реальный конфликт (ребро между вершинами одного цвета)
                            has_conflict, conflict_desc = find_cycle_conflict(G, current_chain, colors, color_history)
                            if has_conflict:
                                # Создаем ключ для конфликта (извлекаем вершины из описания)
                                conflict_key = None
                                if "вершины" in conflict_desc:
                                    # Извлекаем номера вершин из описания
                                    numbers = re.findall(r'\d+', conflict_desc)
                                    if len(numbers) >= 2:
                                        conflict_key = tuple(sorted([int(numbers[0]), int(numbers[1])]))
                                
                                # Если такой конфликт уже был, пропускаем
                                if conflict_key is not None and conflict_key in found_conflicts:
                                    return
                                
                                # Добавляем конфликт в найденные
                                if conflict_key is not None:
                                    found_conflicts.add(conflict_key)
                                
                                key = tuple(sorted(current_chain))
                                if key not in processed:
                                    processed.add(key)
                                    all_chains.append((start_tri[0], list(current_vertices), current_chain.copy(), colors, color_history, conflict_desc))
                                    chain_count += 1
                                    if chain_count % 10 == 0:
                                        log_print(f"      Найдено цепочек: {chain_count}")
                
                if depth >= MAX_CHAIN_DEPTH:
                    return
                
                last_tri = current_chain[-1]
                last_edges = [(last_tri[0], last_tri[1]), 
                             (last_tri[1], last_tri[2]), 
                             (last_tri[0], last_tri[2])]
                
                for edge in last_edges:
                    e_sorted = tuple(sorted(edge))
                    if e_sorted not in edge_to_triangles:
                        continue
                    
                    for next_tri in edge_to_triangles[e_sorted]:
                        if next_tri in current_chain:
                            continue
                        
                        common = get_common_edge(last_tri, next_tri)
                        if common is None:
                            continue
                        
                        current_chain.append(next_tri)
                        new_vertices = current_vertices | set(next_tri)
                        dfs(current_chain, new_vertices, depth + 1)
                        current_chain.pop()
            
            dfs(initial_chain, initial_vertices, 1)
        
        log_print(f"   Всего найдено уникальных цепочек с конфликтами: {len(all_chains)}")
        log_print(f"   Найдено уникальных конфликтов: {len(found_conflicts)}")
        
        # Фильтруем и возвращаем только уникальные цепочки
        filtered_chains = []
        seen = set()
        for start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc in all_chains:
            key = tuple(sorted(chain_triangles))
            if key not in seen:
                seen.add(key)
                filtered_chains.append((start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc))
        
        return filtered_chains        
    except Exception as e:
        log_print(f"⚠️ Ошибка поиска цепочек вынужденности: {e}")
        log_print(traceback.format_exc())
        return []

def build_edge_participation_table(G, k4s, odd_stars, chains):
    try:
        all_edges = [tuple(sorted(e)) for e in G.edges()]
        edge_participation = {e: {'k4': [], 'star': [], 'chain': []} for e in all_edges}
        
        for k4_idx, k4 in enumerate(k4s, 1):
            k4_edges = [tuple(sorted(e)) for e in G.subgraph(k4).edges()]
            for e in k4_edges:
                if e in edge_participation:
                    edge_participation[e]['k4'].append(k4_idx)
        
        for star_idx, (center, cycle_nodes, cycle_edges) in enumerate(odd_stars, 1):
            for e in cycle_edges:
                e_sorted = tuple(sorted(e))
                if e_sorted in edge_participation:
                    edge_participation[e_sorted]['star'].append(star_idx)
        
        for chain_idx, chain_data in enumerate(chains, 1):
            if len(chain_data) == 3:
                start_vertex, chain_vertices, chain_triangles = chain_data
            elif len(chain_data) == 6:
                start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc = chain_data
            else:
                continue
            
            for tri in chain_triangles:
                edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]
                for e in edges:
                    e_sorted = tuple(sorted(e))
                    if e_sorted in edge_participation:
                        edge_participation[e_sorted]['chain'].append(chain_idx)
        
        return edge_participation
    except Exception as e:
        log_print(f"⚠️ Ошибка построения таблицы участия рёбер: {e}")
        return {}

def print_edge_participation_table(edge_participation, k4_count, star_count, chain_count, max_cols=20):
    try:
        sorted_edges = sorted(
            edge_participation.items(),
            key=lambda item: len(item[1]['k4']) + len(item[1]['star']) + len(item[1]['chain']),
            reverse=True
        )
        
        groups = defaultdict(list)
        for e, data in sorted_edges:
            total = len(data['k4']) + len(data['star']) + len(data['chain'])
            groups[total].append((e, data))
        
        group_mapping = {}
        group_number = 1
        for total in sorted(groups.keys(), reverse=True):
            group_mapping[total] = group_number
            group_number += 1
        
        all_rows = []
        for total, group in groups.items():
            grp_num = group_mapping[total]
            structure_counts = defaultdict(int)
            for e, data in group:
                for s in data['k4']:
                    structure_counts[f'K4_{s}'] += 1
                for s in data['star']:
                    structure_counts[f'S_{s}'] += 1
                for s in data['chain']:
                    structure_counts[f'C_{s}'] += 1
            
            for e, data in group:
                unique_count = 0
                for s in data['k4']:
                    if structure_counts[f'K4_{s}'] == 1:
                        unique_count += 1
                for s in data['star']:
                    if structure_counts[f'S_{s}'] == 1:
                        unique_count += 1
                for s in data['chain']:
                    if structure_counts[f'C_{s}'] == 1:
                        unique_count += 1
                
                row_data = {
                    'group': grp_num,
                    'edge': f"{e[0]}-{e[1]}",
                    'k4': data['k4'],
                    'star': data['star'],
                    'chain': data['chain'],
                    'total': len(data['k4']) + len(data['star']) + len(data['chain']),
                    'unique': unique_count
                }
                all_rows.append(row_data)
        
        all_rows.sort(key=lambda x: (x['group'], -x['unique']))
        
        log_print("\n" + "="*80)
        log_print("📊 ТАБЛИЦА УЧАСТИЯ РЁБЕР")
        log_print("="*80)
        
        header = "Группа | Ребро"
        for i in range(1, k4_count + 1):
            header += f" | K4_{i}"
        for i in range(1, star_count + 1):
            header += f" | S_{i}"
        for i in range(1, chain_count + 1):
            header += f" | C_{i}"
        header += " | Сумма | Уник."
        log_print(header)
        log_print("-" * len(header))
        
        for row in all_rows[:50]:
            line = f"{row['group']} | {row['edge']}"
            for i in range(1, k4_count + 1):
                line += " | 1" if i in row['k4'] else " | 0"
            for i in range(1, star_count + 1):
                line += " | 1" if i in row['star'] else " | 0"
            for i in range(1, chain_count + 1):
                line += " | 1" if i in row['chain'] else " | 0"
            line += f" | {row['total']} | {row['unique']}"
            log_print(line)
        
        if len(all_rows) > 50:
            log_print(f"\n... и ещё {len(all_rows) - 50} строк")
    except Exception as e:
        log_print(f"⚠️ Ошибка вывода таблицы участия рёбер: {e}")

# ============================================================
# УЛУЧШЕННЫЙ АЛГОРИТМ 3-РАСКРАСКИ (ПОЛНЫЙ ПЕРЕБОР)
# ============================================================

def color_3_colors_exact(G, vertices, fixed_colors=None):
    if fixed_colors is None:
        fixed_colors = {}
    
    sorted_vertices = sorted(vertices, key=lambda v: len(list(G.neighbors(v))), reverse=True)
    colors = dict(fixed_colors)
    
    def get_available_colors(v, current_colors):
        used = set()
        for neighbor in G.neighbors(v):
            if neighbor in current_colors and current_colors[neighbor] in [0, 1, 2]:
                used.add(current_colors[neighbor])
        return [c for c in range(3) if c not in used]
    
    def is_valid(current_colors):
        for u, v in G.edges():
            if u in current_colors and v in current_colors:
                if current_colors[u] == current_colors[v]:
                    return False
        return True
    
    def backtrack(index, current_colors, depth=0):
        if index == len(sorted_vertices):
            return True
        
        v = sorted_vertices[index]
        
        if v in current_colors:
            return backtrack(index + 1, current_colors, depth + 1)
        
        available = get_available_colors(v, current_colors)
        if not available:
            return False
        
        for color in available:
            current_colors[v] = color
            if is_valid(current_colors):
                if backtrack(index + 1, current_colors, depth + 1):
                    return True
            del current_colors[v]
        
        return False
    
    log_print("   🔍 Запуск точного перебора для 3-раскраски...")
    log_print(f"      Вершин для раскраски: {len(vertices)}")
    
    success = backtrack(0, colors)
    
    if success:
        log_print(f"   ✅ 3-раскраска найдена!")
        return colors, True
    else:
        log_print(f"   ❌ 3-раскраска не найдена")
        return colors, False

def color_remaining_vertices(G, remaining_vertices, initial_colors):
    log_print(f"\n📍 Раскрашиваем {len(remaining_vertices)} вершин в 3 цвета...")
    log_print(f"   Вершины: {sorted(remaining_vertices)}")
    
    result_colors, success = color_3_colors_exact(G, remaining_vertices, initial_colors)
    
    if success:
        log_print("   ✅ 3-раскраска успешно найдена!")
        return result_colors, True
    else:
        log_print("   ❌ 3-раскраска не найдена! Возможно, нужны дополнительные структуры.")
        return result_colors, False

# ============================================================
# ИСПРАВЛЕННЫЙ АЛГОРИТМ ВЫБОРА ВЕРШИН ДЛЯ 4-ГО ЦВЕТА
# ============================================================

def select_vertices_for_color4_bruteforce(G, split_edges):
    log_print("\n📍 Выбор вершин для 4-го цвета (улучшенный алгоритм):")
    
    if not split_edges:
        log_print("   Нет рёбер для разбиения.")
        return set(), set(), set()
    
    edges_set = set()
    for u, v, _ in split_edges:
        edges_set.add(tuple(sorted((u, v))))
    
    edges_list = list(edges_set)
    log_print(f"   Всего рёбер для покрытия: {len(edges_list)}")
    
    all_vertices = set()
    for u, v in edges_list:
        all_vertices.add(u)
        all_vertices.add(v)
    
    log_print(f"   Всего вершин: {len(all_vertices)}")
    
    def is_independent(selected_set):
        for v in selected_set:
            for neighbor in G.neighbors(v):
                if neighbor in selected_set:
                    return False
        return True
    
    def get_covered_edges(selected_set):
        covered = set()
        for u, v in edges_list:
            if u in selected_set or v in selected_set:
                covered.add((u, v))
        return covered
    
    def covers_all_edges(selected_set):
        return len(get_covered_edges(selected_set)) == len(edges_list)
    
    vertex_degree = defaultdict(int)
    for u, v in edges_list:
        vertex_degree[u] += 1
        vertex_degree[v] += 1
    
    sorted_vertices = sorted(all_vertices, key=lambda x: (-vertex_degree[x], x))
    
    best_solution = None
    best_size = float('inf')
    
    def backtrack(index, current_selected):
        nonlocal best_solution, best_size
        
        if len(current_selected) >= best_size:
            return
        
        if covers_all_edges(current_selected):
            if len(current_selected) < best_size:
                best_solution = set(current_selected)
                best_size = len(current_selected)
            return
        
        if index >= len(sorted_vertices):
            return
        
        v = sorted_vertices[index]
        
        can_add = True
        for neighbor in G.neighbors(v):
            if neighbor in current_selected:
                can_add = False
                break
        
        if can_add:
            covered = get_covered_edges(current_selected)
            helps = False
            for u, w in edges_list:
                if (u == v or w == v) and (u, w) not in covered:
                    helps = True
                    break
            
            if helps:
                current_selected.add(v)
                backtrack(index + 1, current_selected)
                current_selected.remove(v)
        
        backtrack(index + 1, current_selected)
    
    log_print("   Выполняется перебор вариантов...")
    backtrack(0, set())
    
    if best_solution is None:
        log_print("   ⚠️ Перебор не нашёл решение, используем жадный + локальный поиск")
        return select_vertices_greedy_with_local_search(G, edges_list, all_vertices, vertex_degree)
    
    covered_edges = get_covered_edges(best_solution)
    skipped_edges = set(edges_list) - covered_edges
    
    log_print(f"\n📊 РЕЗУЛЬТАТ ВЫБОРА:")
    log_print(f"   Выбрано вершин цвета 4: {len(best_solution)}")
    log_print(f"   Вершины цвета 4: {sorted(best_solution)}")
    log_print(f"   Покрыто рёбер: {len(covered_edges)} из {len(edges_list)}")
    
    if not skipped_edges:
        log_print(f"   ✅ ВСЕ рёбра покрыты!")
    else:
        log_print(f"   ⚠️ НЕ ПОКРЫТЫ: {[f'{u}-{v}' for u, v in skipped_edges]}")
    
    if is_independent(best_solution):
        log_print(f"   ✅ Нет смежных выбранных вершин!")
    else:
        log_print(f"   ⚠️ ВНИМАНИЕ: есть смежные выбранные вершины!")
        fixed_solution = set()
        for v in sorted(best_solution, key=lambda x: -vertex_degree[x]):
            can_add = True
            for neighbor in G.neighbors(v):
                if neighbor in fixed_solution:
                    can_add = False
                    break
            if can_add:
                fixed_solution.add(v)
        best_solution = fixed_solution
        log_print(f"   Исправленное множество: {sorted(best_solution)}")
    
    return best_solution, covered_edges, skipped_edges

def select_vertices_greedy_with_local_search(G, edges_list, all_vertices, vertex_degree):
    log_print("\n   Используется жадный алгоритм с локальным поиском:")
    
    selected = set()
    remaining_edges = set(edges_list)
    
    vertices_by_degree = sorted(all_vertices, key=lambda x: (-vertex_degree[x], x))
    
    for v in vertices_by_degree:
        can_add = True
        for neighbor in G.neighbors(v):
            if neighbor in selected:
                can_add = False
                break
        
        if can_add:
            new_edges = set()
            for u, w in edges_list:
                if (u == v or w == v) and (u, w) in remaining_edges:
                    new_edges.add((u, w))
            
            if new_edges:
                selected.add(v)
                remaining_edges -= new_edges
    
    if remaining_edges:
        for u, v in list(remaining_edges):
            if u not in selected:
                selected.add(u)
            elif v not in selected:
                selected.add(v)
    
    improved = True
    while improved:
        improved = False
        for v in list(selected):
            temp = set(selected)
            temp.remove(v)
            
            covered = get_covered_edges_local(temp, edges_list)
            uncovered = set(edges_list) - covered
            
            for w in all_vertices:
                if w in temp:
                    continue
                
                can_add = True
                for neighbor in G.neighbors(w):
                    if neighbor in temp:
                        can_add = False
                        break
                
                if can_add:
                    new_covered = set()
                    for u, e in edges_list:
                        if (u == w or e == w) and (u, e) in uncovered:
                            new_covered.add((u, e))
                    
                    if len(new_covered) > 0:
                        temp.add(w)
                        if get_covered_edges_local(temp, edges_list) == set(edges_list):
                            if len(temp) < len(selected):
                                selected = temp
                                improved = True
                                break
                    else:
                        if vertex_degree[w] > vertex_degree[v]:
                            temp.add(w)
                            if get_covered_edges_local(temp, edges_list) == set(edges_list):
                                selected = temp
                                improved = True
                                break
    
    covered_edges = get_covered_edges_local(selected, edges_list)
    skipped_edges = set(edges_list) - covered_edges
    
    log_print(f"   Выбрано вершин: {len(selected)}")
    log_print(f"   Покрыто рёбер: {len(covered_edges)} из {len(edges_list)}")
    
    def is_independent(selected_set):
        for v in selected_set:
            for neighbor in G.neighbors(v):
                if neighbor in selected_set:
                    return False
        return True
    
    if not is_independent(selected):
        log_print(f"   ⚠️ Есть смежные вершины, исправляем...")
        fixed = set()
        for v in sorted(selected, key=lambda x: -vertex_degree[x]):
            can_add = True
            for neighbor in G.neighbors(v):
                if neighbor in fixed:
                    can_add = False
                    break
            if can_add:
                fixed.add(v)
        selected = fixed
        covered_edges = get_covered_edges_local(selected, edges_list)
        skipped_edges = set(edges_list) - covered_edges
        log_print(f"   Исправлено: {len(selected)} вершин")
    
    return selected, covered_edges, skipped_edges

def get_covered_edges_local(selected_set, edges_list):
    covered = set()
    for u, v in edges_list:
        if u in selected_set or v in selected_set:
            covered.add((u, v))
    return covered

# ============================================================
# ОПТИМИЗАЦИЯ ДО 4 ЦВЕТОВ
# ============================================================

def optimize_to_4_colors(G, k4s, odd_stars, chains):
    try:
        G_work = G.copy()
        split_edges = []
        
        all_structures = []
        structure_edges = []
        
        for k4 in k4s:
            edges = set()
            for edge in combinations(sorted(k4), 2):
                edges.add(tuple(sorted(edge)))
            all_structures.append(('k4', k4, None, None, None))
            structure_edges.append(edges)
        
        for center, cycle_nodes, cycle_edges in odd_stars:
            edges = set(cycle_edges)
            all_structures.append(('star', center, cycle_nodes, cycle_edges, None))
            structure_edges.append(edges)
        
        for chain_data in chains:
            if len(chain_data) == 3:
                start_vertex, chain_vertices, chain_triangles = chain_data
            elif len(chain_data) == 6:
                start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc = chain_data
            else:
                continue
            
            edges = set()
            for tri in chain_triangles:
                edges.update([(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])])
            all_structures.append(('chain', start_vertex, chain_vertices, None, chain_triangles))
            structure_edges.append(edges)
        
        structures_for_print = []
        for i, (s_type, k4_data, start_vertex, cycle_nodes, chain_triangles) in enumerate(all_structures):
            if s_type == 'k4':
                structures_for_print.append((s_type, k4_data))
            elif s_type == 'star':
                structures_for_print.append((s_type, (start_vertex, cycle_nodes, structure_edges[i])))
            elif s_type == 'chain':
                structures_for_print.append((s_type, (start_vertex, chain_triangles, structure_edges[i])))
        
        print_structure_summary(structures_for_print, structure_edges, "НАЧАЛЬНЫЕ СТРУКТУРЫ")
        
        iteration = 0
        first_iteration_done = False
        
        while all_structures and iteration < 30:
            iteration += 1
            old_count = len(all_structures)
            log_print(f"\n🔄 Итерация {iteration}")
            log_print(f"   Структур до разбиения: {old_count}")
            
            edge_to_structures = defaultdict(set)
            for idx, edges in enumerate(structure_edges):
                for edge in edges:
                    edge_to_structures[edge].add(idx)
            
            edge_scores = {}
            for edge, structs in edge_to_structures.items():
                edge_scores[edge] = len(structs)
            
            if not edge_scores:
                break
            
            best_edge = max(edge_scores.items(), key=lambda x: (x[1], len(x[0])))
            u, v = best_edge[0]
            best_group = best_edge[1]
            
            log_print(f"   Разбиваем ребро {u}-{v} (сумма = {best_group})")
            
            # === ПОСЛЕ ПЕРВОЙ ИТЕРАЦИИ ПОКАЗЫВАЕМ СПИСОК УДАЛЁННЫХ ЦЕПОЧЕК ===
            if iteration == 1 and not first_iteration_done:
                first_iteration_done = True
                
                # Собираем структуры, которые содержат это ребро
                affected_structures = []
                for idx, edges in enumerate(structure_edges):
                    if (u, v) in edges or (v, u) in edges:
                        affected_structures.append(idx)
                
                log_print(f"\n   📋 УДАЛЁННЫЕ СТРУКТУРЫ (после первой итерации):")
                
                # Сортируем по типу для красивого вывода
                k4_list = []
                star_list = []
                chain_list = []
                
                for idx in affected_structures:
                    if idx < len(all_structures):
                        s_type = all_structures[idx][0]
                        if s_type == 'k4':
                            k4_list.append(idx)
                        elif s_type == 'star':
                            star_list.append(idx)
                        elif s_type == 'chain':
                            chain_list.append(idx)
                
                # Выводим K4
                if k4_list:
                    names = [f"K4_{i+1}" for i in k4_list]
                    log_print(f"      K4: {', '.join(names)}")
                
                # Выводим звёзды
                if star_list:
                    names = [f"S_{i+1}" for i in star_list]
                    log_print(f"      Звёзды: {', '.join(names)}")
                
                # Выводим цепочки
                if chain_list:
                    names = [f"C_{i+1}" for i in chain_list]
                    log_print(f"      Цепочки: {', '.join(names)}")
                
                log_print(f"      Всего структур удалено: {len(affected_structures)}")
                log_print("")
            
            split_edges.append((u, v, None))
            G_work.remove_edge(u, v)
            
            log_print(f"   Перестраиваем структуры...")
            try:
                current_k4s = find_all_k4(G_work)
                current_odd_stars = find_all_odd_stars(G_work, current_k4s)
                current_chains = find_all_forced_chains(G_work)
            except Exception as e:
                log_print(f"   ⚠️ Ошибка перестроения структур: {e}")
                break
            
            new_structures = []
            new_edges = []
            
            for k4 in current_k4s:
                edges = set()
                for edge in combinations(sorted(k4), 2):
                    edges.add(tuple(sorted(edge)))
                new_structures.append(('k4', k4, None, None, None))
                new_edges.append(edges)
            
            for center, cycle_nodes, cycle_edges in current_odd_stars:
                edges = set(cycle_edges)
                new_structures.append(('star', center, cycle_nodes, cycle_edges, None))
                new_edges.append(edges)
            
            for chain_data in current_chains:
                if len(chain_data) == 3:
                    start_vertex, chain_vertices, chain_triangles = chain_data
                elif len(chain_data) == 6:
                    start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc = chain_data
                else:
                    continue
                
                edges = set()
                for tri in chain_triangles:
                    edges.update([(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])])
                new_structures.append(('chain', start_vertex, chain_vertices, None, chain_triangles))
                new_edges.append(edges)
            
            all_structures = new_structures
            structure_edges = new_edges
            
            new_count = len(all_structures)
            log_print(f"   Структур после разбиения: {new_count}")
            
            expected_count = old_count - best_group
            if new_count == expected_count:
                log_print(f"   ✅ Изменение корректно: {old_count} - {best_group} = {new_count}")
            else:
                log_print(f"   ⚠️ Некорректное изменение!")
                log_print(f"   Ожидалось: {old_count} - {best_group} = {expected_count}")
                log_print(f"   Получено: {new_count}")
                log_print(f"   Разница: {new_count - expected_count}")
            
            structures_for_print = []
            for i, (s_type, k4_data, start_vertex, cycle_nodes, chain_triangles) in enumerate(all_structures):
                if s_type == 'k4':
                    structures_for_print.append((s_type, k4_data))
                elif s_type == 'star':
                    structures_for_print.append((s_type, (start_vertex, cycle_nodes, structure_edges[i])))
                elif s_type == 'chain':
                    structures_for_print.append((s_type, (start_vertex, chain_triangles, structure_edges[i])))
            
            print_structure_summary(structures_for_print, structure_edges, f"СТРУКТУРЫ ПОСЛЕ ИТЕРАЦИИ {iteration}")
        
        try:
            color4_vertices, covered_edges, skipped_edges = select_vertices_for_color4_bruteforce(G, split_edges)
        except Exception as e:
            log_print(f"⚠️ Ошибка выбора вершин для 4-го цвета: {e}")
            log_print(traceback.format_exc())
            color4_vertices = set()
            covered_edges = set()
            skipped_edges = set()
        
        log_print(f"\n✅ Оптимизация до 4 цветов завершена.")
        log_print(f"   Вершин цвета 4: {len(color4_vertices)}")
        log_print(f"   Вершины цвета 4: {sorted(color4_vertices)}")
        
        final_split_edges = []
        for u, v, _ in split_edges:
            if u in color4_vertices:
                final_split_edges.append((u, v, u))
            elif v in color4_vertices:
                final_split_edges.append((u, v, v))
            else:
                final_split_edges.append((u, v, None))
        
        return final_split_edges, color4_vertices
    except Exception as e:
        log_print(f"❌ Ошибка в оптимизации: {e}")
        log_print(traceback.format_exc())
        return [], set()

# ============================================================
# РАСКРАСКА В 4 ЦВЕТА
# ============================================================

def color_4_colors(G, split_edges, color4_vertices):
    log_print("\n" + "="*50)
    log_print("🎨 ЭТАП 4: РАСКРАСКА В 4 ЦВЕТА")
    log_print("="*50)
    
    colors = {}
    
    for v in color4_vertices:
        colors[v] = 3
        log_print(f"   {v} -> цвет 3 (4-й цвет)")
    
    remaining = [v for v in G.nodes() if v not in colors]
    
    if not remaining:
        log_print("   Все вершины уже раскрашены!")
        return colors, True
    
    log_print(f"\n📍 Раскрашиваем оставшиеся {len(remaining)} вершин в 3 цвета...")
    
    result_colors, success = color_remaining_vertices(G, remaining, colors)
    
    if not success:
        log_print("   ❌ 3-раскраска не найдена!")
        return colors, False
    
    colors = result_colors
    
    log_print("\n🔍 Проверка 4-цветной раскраски:")
    correct = True
    conflicts = []
    for u, v in G.edges():
        if u in colors and v in colors:
            if colors[u] == colors[v]:
                conflicts.append((u, v, colors[u]))
                log_print(f"   ❌ Ошибка: вершины {u} и {v} имеют одинаковый цвет {colors[u]}")
                correct = False
        else:
            log_print(f"   ⚠️ Вершина {u} или {v} не раскрашена")
            correct = False
    
    if correct:
        log_print(f"   ✅ Все {G.number_of_edges()} рёбер правильно раскрашены в 4 цвета!")
    else:
        log_print(f"   ⚠️ Найдены ошибки в раскраске!")
        if conflicts:
            log_print(f"\n   Конфликтующие рёбра ({len(conflicts)}):")
            for u, v, c in conflicts[:10]:
                log_print(f"      {u} - {v} (оба цвета {c})")
    
    return colors, correct

def draw_4color_graph(G, colors, title="Граф с 4-цветной раскраской"):
    try:
        plt.figure(figsize=(14, 12))
        
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except nx.NetworkXException:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
            log_print("⚠️ Граф не планарный!")
        
        color_map = {0: 'red', 1: 'blue', 2: 'green', 3: 'purple'}
        
        colored_nodes = [v for v in G.nodes() if v in colors]
        uncolored_nodes = [v for v in G.nodes() if v not in colors]
        
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=1)
        
        if colored_nodes:
            node_colors = [color_map.get(colors.get(v, 0), 'gray') for v in colored_nodes]
            nx.draw_networkx_nodes(G, pos, nodelist=colored_nodes, 
                                   node_color=node_colors, node_size=300)
        
        if uncolored_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=uncolored_nodes, 
                                   node_color='lightgray', node_size=300, 
                                   edgecolors='black', linewidths=2)
        
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', label='Цвет 0'),
            Patch(facecolor='blue', label='Цвет 1'),
            Patch(facecolor='green', label='Цвет 2'),
            Patch(facecolor='purple', label='Цвет 3 (4-й цвет)'),
            Patch(facecolor='lightgray', edgecolor='black', label='Нераскрашена')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        plt.title(title)
        plt.show()
    except Exception as e:
        log_print(f"⚠️ Ошибка рисования 4-цветного графа: {e}")

def draw_with_structures(G, k4s, odd_stars, chains, title="Граф с выделенными структурами"):
    try:
        plt.figure(figsize=(14, 12))
        
        is_planar = nx.is_planar(G)
        if is_planar:
            try:
                pos = nx.planar_layout(G)
            except nx.NetworkXException:
                pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, seed=42)
            log_print("⚠️ Граф не планарный!")
        
        nx.draw_networkx_nodes(G, pos, node_color='lightgray', node_size=300)
        nx.draw_networkx_edges(G, pos, edge_color='gray', width=1)
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        k4_vertices_set = set()
        for k4 in k4s:
            k4_vertices_set.update(k4)
        
        if k4_vertices_set:
            nx.draw_networkx_nodes(G, pos, nodelist=list(k4_vertices_set),
                                   node_color='maroon', node_size=450)
        for k4 in k4s:
            edges = list(G.subgraph(k4).edges())
            nx.draw_networkx_edges(G, pos, edgelist=edges,
                                   edge_color='maroon', width=2.0, style='dashed')
        
        colored_nodes = set(k4_vertices_set)
        for center, cycle_nodes, cycle_edges in odd_stars:
            if center not in colored_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=[center],
                                       node_color='blue', node_size=500)
                colored_nodes.add(center)
            for node in cycle_nodes:
                if node not in colored_nodes:
                    nx.draw_networkx_nodes(G, pos, nodelist=[node],
                                           node_color='lightblue', node_size=380)
                    colored_nodes.add(node)
            for node in cycle_nodes:
                nx.draw_networkx_edges(G, pos, edgelist=[(center, node)],
                                       edge_color='blue', width=1.5)
            if cycle_edges:
                nx.draw_networkx_edges(G, pos, edgelist=list(cycle_edges),
                                       edge_color='blue', width=2.5)
        
        for chain_data in chains:
            if len(chain_data) == 3:
                start_vertex, chain_vertices, chain_triangles = chain_data
            elif len(chain_data) == 6:
                start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc = chain_data
            else:
                continue
            
            if start_vertex not in colored_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=[start_vertex],
                                       node_color='orange', node_size=500)
                colored_nodes.add(start_vertex)
            for v in chain_vertices:
                if v != start_vertex and v not in colored_nodes:
                    nx.draw_networkx_nodes(G, pos, nodelist=[v],
                                           node_color='lightcoral', node_size=380)
                    colored_nodes.add(v)
            for tri in chain_triangles:
                edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[0], tri[2])]
                nx.draw_networkx_edges(G, pos, edgelist=edges,
                                       edge_color='orange', width=2.0, style='dashed')
        
        plt.title(title)
        plt.show()
    except Exception as e:
        log_print(f"⚠️ Ошибка рисования графа со структурами: {e}")

def save_log_to_file(graph_name, success, start_time, end_time):
    global log_lines
    if not LOG_TO_FILE:
        return
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "SUCCESS" if success else "FAILED"
        log_filename = f"{graph_name}_LOG_{timestamp}_{status}.txt"
        
        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", log_filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Лог-файл анализа графа\n")
            f.write(f"Граф: {graph_name}\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Статус: {'УСПЕШНО' if success else 'НЕ УДАЛОСЬ'}\n")
            f.write(f"Время выполнения: {end_time - start_time:.2f} секунд\n")
            f.write("="*80 + "\n\n")
            f.write("\n".join(log_lines))
        
        log_print(f"\n📁 Лог сохранён в файл: {log_path}")
        return log_path
    except Exception as e:
        log_print(f"⚠️ Ошибка сохранения лога: {e}")
        return None

def graph_to_string(G):
    vertices = sorted(G.nodes())
    edges = sorted([tuple(sorted(e)) for e in G.edges()])
    return f"V={vertices}, E={edges}"

def coloring_to_string(colors):
    result = []
    for v in sorted(colors.keys()):
        result.append(f"{v}-{colors[v]}")
    return "[" + ", ".join(result) + "]"

def main():
    global log_lines, LOG_TO_FILE, error_occurred, coloring_success
    
    start_time = time.time()
    coloring_success = False
    
    try:
        filename = "graph_35_03.json"
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        
        try:
            G = load_graph_from_json(filename)
        except Exception as e:
            log_print(f"❌ Критическая ошибка загрузки файла: {e}")
            log_print(traceback.format_exc())
            input("Нажмите Enter, чтобы закрыть окно...")
            return
        
        graph_name = os.path.splitext(os.path.basename(filename))[0]
        n = G.number_of_nodes()
        m = G.number_of_edges()
        
        log_print(f"Загружен граф: {n} вершин, {m} рёбер")
        log_print(f"Имя графа: {graph_name}")
        log_print(f"Граф: {graph_to_string(G)}")
        log_print(f"Режим DEBUG: {'ВКЛЮЧЕН' if DEBUG else 'ВЫКЛЮЧЕН'}")
        
        if n > MAX_VERTICES:
            log_print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЕ: граф ({n} вершин) превышает лимит MAX_VERTICES ({MAX_VERTICES}).")
            log_print("Анализ остановлен. Измените MAX_VERTICES в настройках, чтобы обработать этот граф.")
            input("\nНажмите Enter, чтобы закрыть окно...")
            return
        
        # === СОХРАНЯЕМ ИСХОДНЫЙ ГРАФ ===
        log_print("\n" + "="*50)
        log_print("📸 СОХРАНЕНИЕ ИСХОДНОГО ГРАФА")
        log_print("="*50)
        save_original_graph(G, graph_name)
        
        # === ПОИСК СТРУКТУР ===
        log_print("\n" + "="*50)
        log_print("🔍 ПОИСК K4")
        log_print("="*50)
        k4s = find_all_k4(G)
        if k4s:
            unique_k4s = []
            for k4 in k4s:
                if k4 not in unique_k4s:
                    unique_k4s.append(k4)
            k4s = unique_k4s
            for i, k4 in enumerate(k4s, 1):
                k4_edges = [tuple(sorted(e)) for e in G.subgraph(k4).edges()]
                log_print(f"K4 #{i}: вершины: {sorted(k4)}")
                log_print(f"   Рёбра: {sorted(k4_edges)}")
        else:
            log_print("K4 не найдены.")
        
        log_print("\n" + "="*50)
        log_print("🔍 ПОИСК НЕЧЁТНЫХ ЗВЁЗД (КЛАССИЧЕСКИХ)")
        log_print("="*50)
        
        odd_stars = find_all_odd_stars(G, k4s)
        if odd_stars:
            k4_count = 0
            star_count = 0
            for center, cycle_nodes, cycle_edges in odd_stars:
                if len(cycle_nodes) == 3:
                    k4_count += 1
                    log_print(f"🔺 K4 (как звезда): центр {center}, вершины: {sorted(cycle_nodes)}")
                    log_print(f"   Рёбра цикла: {sorted(cycle_edges)}")
                else:
                    star_count += 1
                    log_print(f"⭐ Нечётная звезда: центр {center}")
                    log_print(f"   Вершины цикла: {sorted(cycle_nodes)}")
                    log_print(f"   Рёбра цикла: {sorted(cycle_edges)}")
            log_print(f"\n📊 ИТОГО: K4 = {len(k4s)} (уникальных), Нечётных звёзд = {len(odd_stars)}")
            log_print(f"   Из них K4 как звёзды: {k4_count}, звёзд с циклом >3: {star_count}")
        else:
            log_print("Нечётные звёзды не найдены.")
        
        log_print("\n" + "="*50)
        log_print("🔍 ПОИСК ЦЕПОЧЕК ВЫНУЖДЕННОСТИ (СКРЫТЫЕ НЕЧЁТНЫЕ ЗВЁЗДЫ)")
        log_print("="*50)
        
        chains = find_all_forced_chains(G)
        if chains:
            log_print(f"\n📊 Найдено цепочек вынужденности: {len(chains)}")
            
            # Определяем, сколько цепочек показывать
            if MAX_CHAINS_TO_DISPLAY > 0:
                show_count = min(MAX_CHAINS_TO_DISPLAY, len(chains))
            else:
                show_count = len(chains)
            
            for i in range(show_count):
                chain_data = chains[i]
                if len(chain_data) == 3:
                    start_vertex, chain_vertices, chain_triangles = chain_data
                    colors, color_history, conflict_desc = None, None, None
                elif len(chain_data) == 6:
                    start_vertex, chain_vertices, chain_triangles, colors, color_history, conflict_desc = chain_data
                else:
                    continue
                
                log_print(f"🔗 Цепочка #{i+1}: старт {start_vertex}")
                log_print(f"   Всего вершин: {len(chain_vertices)}")
                log_print(f"   Вершины цепочки: {sorted(chain_vertices)}")
                log_print(f"   Треугольников в цепочке: {len(chain_triangles)}")
                
                # Выводим все треугольники
                for j, tri in enumerate(chain_triangles, 1):
                    edges_info = get_edges_of_triangle(G, tri)
                    edges_str = ", ".join(edges_info)
                    log_print(f"      {j}. {tri} -> рёбра: {edges_str}")
                
                # Если есть конфликт, показываем его сегмент
                if conflict_desc and "КОНФЛИКТ" in conflict_desc and colors:
                    start_idx, end_idx, segment = find_chain_conflict_segment(
                        chain_triangles, conflict_desc, colors, color_history
                    )
                    # Извлекаем конфликтующие вершины для дополнительной информации
                    v1, v2 = None, None
                    if "вершины" in conflict_desc:
                        numbers = re.findall(r'\d+', conflict_desc)
                        if len(numbers) >= 2:
                            v1, v2 = int(numbers[0]), int(numbers[1])
                    
                    if segment and len(segment) < len(chain_triangles):
                        log_print(f"\n   📌 СЕГМЕНТ ЦЕПОЧКИ, УЧАСТВУЮЩИЙ В КОНФЛИКТЕ (треугольники {start_idx+1}-{end_idx+1}):")
                        log_print(f"   ⚡ КОНФЛИКТ ВОЗНИК ПРИ ДОБАВЛЕНИИ ТРЕУГОЛЬНИКА #{end_idx+1}: {segment[-1]}")
                        if v1 is not None and v2 is not None:
                            log_print(f"   🔴 РЕБРО {v1}-{v2} ПОЯВЛЯЕТСЯ ВПЕРВЫЕ В ЭТОМ ТРЕУГОЛЬНИКЕ!")
                        for j, tri in enumerate(segment, start_idx + 1):
                            edges_info = get_edges_of_triangle(G, tri)
                            edges_str = ", ".join(edges_info)
                            if j == end_idx + 1:
                                log_print(f"      ⚠️ {j}. {tri} -> рёбра: {edges_str} ⚠️ КОНФЛИКТ ЗДЕСЬ!")
                            else:
                                log_print(f"      {j}. {tri} -> рёбра: {edges_str}")
                    elif segment:
                        log_print(f"\n   📌 ВЕСЬ СЕГМЕНТ УЧАСТВУЕТ В КОНФЛИКТЕ:")
                        for j, tri in enumerate(chain_triangles, 1):
                            edges_info = get_edges_of_triangle(G, tri)
                            edges_str = ", ".join(edges_info)
                            log_print(f"      {j}. {tri} -> рёбра: {edges_str}")
                
                if colors:
                    log_print(f"\n   Раскраска:")
                    for v in sorted(colors.keys()):
                        step = color_history.get(v, '?')
                        if v == start_vertex:
                            log_print(f"      {v} -> цвет {colors[v]} (стартовая вершина, начальный цвет)")
                        else:
                            log_print(f"      {v} -> цвет {colors[v]} (получен на шаге {step})")
                    
                    if conflict_desc:
                        log_print(f"\n   ⚠️ КОНФЛИКТ В ЦЕПОЧКЕ! {conflict_desc}")
                log_print()
            
            if len(chains) > show_count:
                log_print(f"\n... и ещё {len(chains) - show_count} цепочек")           
        else:
            log_print("Цепочки вынужденности не найдены.")
        
        log_print("\n" + "="*50)
        log_print("📊 ТАБЛИЦА УЧАСТИЯ РЁБЕР")
        log_print("="*50)
        edge_participation = build_edge_participation_table(G, k4s, odd_stars, chains)
        print_edge_participation_table(edge_participation, len(k4s), len(odd_stars), len(chains))
        log_print("="*50 + "\n")
        
        # === СОХРАНЯЕМ ИЗОБРАЖЕНИЯ СТРУКТУР ===
        save_all_structures_images(G, k4s, odd_stars, chains, graph_name)
        
        log_print("\n🖼️  Рисуем граф с выделенными структурами...")
        draw_with_structures(G, k4s, odd_stars, chains)
        
        # === ОПТИМИЗАЦИЯ ДО 4 ЦВЕТОВ ===
        log_print("\n" + "="*50)
        log_print("🛠️ ЭТАП 3: ОПТИМИЗАЦИЯ ДО 4 ЦВЕТОВ")
        log_print("="*50)
        log_print("   (разбиение рёбер раскраской вершин в 4-й цвет)")
        
        split_edges, color4_vertices = optimize_to_4_colors(G, k4s, odd_stars, chains)
        
        # === СОХРАНЯЕМ ГРАФ С ВЕРШИНАМИ 4-ГО ЦВЕТА ===
        log_print("\n" + "="*50)
        log_print("📸 СОХРАНЕНИЕ ГРАФА С ВЕРШИНАМИ 4-ГО ЦВЕТА")
        log_print("="*50)
        save_color4_vertices_graph(G, color4_vertices, graph_name)
        
        log_print("\n" + "="*50)
        log_print("📊 РЕЗУЛЬТАТ ОПТИМИЗАЦИИ")
        log_print("="*50)
        log_print(f"   Вершин цвета 4: {len(color4_vertices)}")
        log_print(f"   Вершины цвета 4: {sorted(color4_vertices)}")
        
        # === РАСКРАСКА В 4 ЦВЕТА ===
        colors, coloring_success = color_4_colors(G, split_edges, color4_vertices)
        
        # === СОХРАНЯЕМ ФИНАЛЬНУЮ РАСКРАСКУ ===
        if coloring_success:
            log_print("\n" + "="*50)
            log_print("📸 СОХРАНЕНИЕ ФИНАЛЬНОЙ РАСКРАСКИ")
            log_print("="*50)
            save_final_colored_graph(G, colors, graph_name)
        
        # === РИСУЕМ РАСКРАШЕННЫЙ ГРАФ ===
        log_print("\n🖼️  Рисуем граф с 4-цветной раскраской...")
        draw_4color_graph(G, colors, title="Граф с 4-цветной раскраской")
        
        end_time = time.time()
        elapsed = end_time - start_time
        log_print(f"\n⏱️  Время выполнения: {elapsed:.2f} секунд")
        
        log_print(f"\n📋 РАСКРАСКА: {coloring_to_string(colors)}")
        
        if coloring_success:
            log_print("\n" + "="*50)
            log_print("✅ АНАЛИЗ УСПЕШНО ЗАВЕРШЁН! Граф успешно раскрашен в 4 цвета.")
            log_print("="*50)
        else:
            log_print("\n" + "="*50)
            log_print("❌ АНАЛИЗ ЗАВЕРШЁН С ОШИБКАМИ! Граф НЕ раскрашен в 4 цвета.")
            log_print("="*50)
        
        save_log_to_file(graph_name, coloring_success, start_time, time.time())
        
    except Exception as e:
        log_print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        log_print(traceback.format_exc())
        error_occurred = True
        coloring_success = False
        save_log_to_file(graph_name, False, start_time, time.time())
    
    finally:
        if coloring_success:
            print("\n✅ УСПЕШНО! Граф раскрашен в 4 цвета.")
        else:
            print("\n❌ НЕ УДАЛОСЬ! Проверьте лог для деталей.")
        input("\nНажмите Enter, чтобы закрыть окно...")

if __name__ == "__main__":
    main()