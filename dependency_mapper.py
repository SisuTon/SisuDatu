#!/usr/bin/env python3
"""
Скрипт для анализа и визуализации всех зависимостей проекта в виде графа
"""
import ast
import os
import sys
from pathlib import Path
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = defaultdict(set)
        self.current_file = None

    def visit_Import(self, node):
        for alias in node.names:
            self.imports[self.current_file].add(alias.name.split('.')[0])

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports[self.current_file].add(node.module.split('.')[0])

def parse_file(file_path: Path) -> dict:
    """Анализирует файл и возвращает его зависимости"""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
            analyzer = ImportAnalyzer()
            analyzer.current_file = file_path.stem
            analyzer.visit(tree)
            return analyzer.imports
        except Exception as e:
            print(f"⚠️ Ошибка при анализе {file_path}: {str(e)}")
            return {}

def find_python_files(root_dir: Path) -> list:
    """Находит все Python файлы в директории"""
    return [f for f in root_dir.rglob('*.py') 
            if '.venv' not in str(f) and '.git' not in str(f)]

def build_dependency_graph(files: list) -> nx.DiGraph:
    """Строит граф зависимостей"""
    graph = nx.DiGraph()
    all_imports = defaultdict(set)
    
    for file in files:
        imports = parse_file(file)
        for file_name, deps in imports.items():
            all_imports[file_name].update(deps)
    
    # Добавляем узлы и связи
    for file, deps in all_imports.items():
        graph.add_node(file, size=10, title=file, group=1)
        for dep in deps:
            if dep in all_imports:  # Показываем только внутренние зависимости
                graph.add_node(dep, size=8, title=dep, group=2)
                graph.add_edge(file, dep)
    
    return graph

def visualize_with_pyvis(graph: nx.DiGraph, output_file: str = 'dependencies.html'):
    """Визуализирует граф с помощью PyVis"""
    net = Network(height='800px', width='100%', directed=True)
    net.from_nx(graph)
    
    # Настраиваем внешний вид
    net.toggle_physics(True)
    net.show_buttons(filter_=['physics'])
    net.show(output_file)
    print(f"🎯 Визуализация сохранена в {output_file}")

def visualize_with_matplotlib(graph: nx.DiGraph):
    """Визуализирует граф с помощью matplotlib"""
    plt.figure(figsize=(20, 15))
    pos = nx.spring_layout(graph, k=0.5, iterations=50)
    
    nx.draw_networkx_nodes(graph, pos, node_size=200, alpha=0.9)
    nx.draw_networkx_edges(graph, pos, arrowstyle='->', arrowsize=10)
    nx.draw_networkx_labels(graph, pos, font_size=8)
    
    plt.title("Карта зависимостей проекта", size=15)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('dependencies.png', dpi=300)
    print("🎯 Статичная визуализация сохранена в dependencies.png")

def export_to_dot(graph: nx.DiGraph, filename: str = 'dependencies.dot'):
    """Экспортирует граф в формат DOT"""
    nx.drawing.nx_pydot.write_dot(graph, filename)
    print(f"🎯 Граф экспортирован в {filename} (можно открыть в GraphViz)")

def main():
    root_dir = Path('.')
    python_files = find_python_files(root_dir)
    print(f"🔍 Найдено {len(python_files)} Python файлов")
    
    graph = build_dependency_graph(python_files)
    print(f"📊 Построен граф с {len(graph.nodes)} узлами и {len(graph.edges)} связями")
    
    # Визуализации
    visualize_with_pyvis(graph)
    visualize_with_matplotlib(graph)
    export_to_dot(graph)
    
    # Дополнительный анализ
    print("\n🔎 Ключевые метрики:")
    print(f"   Самый связанный модуль: {max(graph.degree, key=lambda x: x[1])[0]}")
    print(f"   Число компонент связности: {nx.number_weakly_connected_components(graph)}")
    
    if nx.is_directed_acyclic_graph(graph):
        print("   Граф ациклический (нет циклических зависимостей)")
    else:
        print("   ⚠️ Обнаружены циклические зависимости!")
        for cycle in nx.simple_cycles(graph):
            print(f"      Цикл: {' → '.join(cycle)}")

if __name__ == '__main__':
    main() 