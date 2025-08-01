#!/usr/bin/env python3
"""
SisuDatuBot Architecture Audit 2025
Современный анализатор зависимостей Python-проекта с экспортом PNG, GraphML, HTML и текстового отчета.
"""
import ast
import os
import time
from pathlib import Path
from collections import defaultdict
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
import warnings
import logging
import matplotlib.pyplot as plt
import re
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Игнорировать предупреждения AST
warnings.filterwarnings('ignore', category=SyntaxWarning)

AUDIT_DIR = Path('architecture_audit')
AUDIT_DIR.mkdir(exist_ok=True)

PROJECT_PREFIXES = ('app', 'alembic', 'tests', 'core', 'shared')

class ImportAnalyzer(ast.NodeVisitor):
    """Анализатор импортов с кешированием и расширенной логикой"""
    def __init__(self):
        self.imports = defaultdict(set)
        self.import_details = defaultdict(list)
        self.current_file = None
        self._module_cache = {}

    def _resolve_module(self, module_name: str, current_file: Optional[Path] = None) -> Optional[str]:
        """Гибкое разрешение модулей: ищет по всей структуре app/, поддерживает относительные импорты, fallback по совпадению концов пути."""
        if module_name in self._module_cache:
            return self._module_cache[module_name]
        parts = module_name.split('.')
        # Абсолютные импорты внутри app/
        candidates = [
            Path('app').joinpath(*parts).with_suffix('.py'),
            Path('app').joinpath(*parts, '__init__.py')
        ]
        for candidate in candidates:
            if candidate.exists():
                resolved = str(candidate)
                self._module_cache[module_name] = resolved
                return resolved
        # Fallback: ищем любой файл, заканчивающийся на нужный путь
        for py_file in Path('app').rglob('*.py'):
            if tuple(py_file.parts[-len(parts):]) == tuple(parts):
                resolved = str(py_file)
                self._module_cache[module_name] = resolved
                return resolved
        # Alembic, tests, core, shared
        for base in ['alembic', 'tests', 'core', 'shared']:
            if parts[0] == base:
                candidate = Path(base).joinpath(*parts[1:]).with_suffix('.py')
                if candidate.exists():
                    resolved = str(candidate)
                    self._module_cache[module_name] = resolved
                    return resolved
        # Относительные импорты
        if current_file and module_name.startswith('.'):
            rel_parts = module_name.lstrip('.').split('.')
            rel_path = current_file.parent.joinpath(*rel_parts).with_suffix('.py')
            if rel_path.exists():
                resolved = str(rel_path)
                self._module_cache[module_name] = resolved
                return resolved
        # Если ничего не найдено — возвращаем модуль как есть (для графа)
        self._module_cache[module_name] = module_name
        return module_name

    def visit_Import(self, node):
        for alias in node.names:
            full_module = alias.name
            resolved_path = self._resolve_module(full_module)
            if resolved_path:
                self.imports[self.current_file].add(resolved_path)
                self.import_details[self.current_file].append(
                    (resolved_path, full_module, 'import', node.lineno)
                )

    def visit_ImportFrom(self, node):
        if node.module:
            resolved_path = self._resolve_module(node.module, Path(self.current_file))
            if resolved_path:
                self.imports[self.current_file].add(resolved_path)
                for alias in node.names:
                    self.import_details[self.current_file].append(
                        (resolved_path, f"{node.module}.{alias.name}", 'from', node.lineno)
                    )

def parse_file(file_path: Path) -> Tuple[Dict, Dict]:
    """Парсит Python-файл, возвращает импорты и детали импортов."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'import ' not in content and 'from ' not in content:
            return {}, {}
        tree = ast.parse(content)
        analyzer = ImportAnalyzer()
        try:
            analyzer.current_file = str(file_path.relative_to(Path.cwd()))
        except ValueError:
            analyzer.current_file = str(file_path)
        analyzer.visit(tree)
        return analyzer.imports, analyzer.import_details
    except Exception as e:
        logging.warning(f"Ошибка при анализе {file_path}: {str(e)}")
        return {}, {}

def find_python_files(root_dir: Path) -> List[Path]:
    """Ищет все Python-файлы в проекте."""
    return list(root_dir.rglob('*.py'))

def should_skip_file(file_path: Path) -> bool:
    """Пропускает служебные и скрытые файлы."""
    path_str = str(file_path)
    return (
        '.venv' in path_str or 
        '.git' in path_str or
        file_path.name.startswith('__') or
        '__pycache__' in path_str or
        file_path.name.startswith('.')
    )

def classify_module(module_path: str) -> str:
    """Улучшенная классификация для SisuDatuBot"""
    path = Path(module_path)
    if 'alembic' in module_path:
        return 'alembic'
    elif 'tests' in module_path:
        return 'tests'
    elif path.parts[0] == 'app':
        if path.name == 'main.py':
            return 'presentation'
        if path.name == '__init__.py':
            return path.parent.name.upper() if path.parent.name else 'core'
        if len(path.parts) > 1:
            return path.parts[1]  # app/domain, app/infrastructure и т.д.
        return 'app'
    elif path.parts[0] in ('core', 'shared'):
        return path.parts[0]
    return 'other'
# TODO: интеграция с architecture_config.py для кастомных паттернов

def is_project_module(module_path: str) -> bool:
    """Проверяет, является ли модуль частью проекта (а не внешней/стандартной библиотекой)."""
    path = Path(module_path)
    return path.parts and path.parts[0] in PROJECT_PREFIXES

def build_dependency_graph(files: List[Path]) -> Tuple[nx.DiGraph, dict]:
    """Строит граф зависимостей и собирает детали импортов (только проектные модули)."""
    graph = nx.DiGraph()
    all_details = defaultdict(list)
    file_stats = {}
    for file in files:
        if should_skip_file(file):
            continue
        imports, details = parse_file(file)
        try:
            module_path = str(file.relative_to(Path.cwd()))
        except ValueError:
            module_path = str(file)
        file_stats[module_path] = {
            'size': os.path.getsize(file),
            'mtime': os.path.getmtime(file)
        }
        for file_name, deps in imports.items():
            if not is_project_module(file_name):
                continue
            graph.add_node(file_name, **{
                'size': file_stats.get(file_name, {}).get('size', 0),
                'title': f"{file_name}\nSize: {file_stats.get(file_name, {}).get('size', 0)} bytes",
                'layer': classify_module(file_name),
                'dependencies': len(deps)
            })
            for dep in deps:
                if is_project_module(dep) and dep != file_name:
                    graph.add_edge(file_name, dep)
        for file_name, detail_list in details.items():
            all_details[file_name].extend(detail_list)
    for u, v in graph.edges():
        graph.edges[u, v]['weight'] = sum(
            1 for details in all_details.get(u, []) 
            if details[0] == v
        )
    return graph, all_details

def export_graph_png(graph: nx.DiGraph, out_path: Path):
    """Экспортирует граф в PNG через networkx+matplotlib."""
    plt.figure(figsize=(18, 12))
    pos = nx.spring_layout(graph, k=0.25, iterations=50, seed=42)
    layers = nx.get_node_attributes(graph, 'layer')
    color_map = {
        'domain': '#FF6B6B',
        'infrastructure': '#4ECDC4',
        'presentation': '#FFE66D',
        'shared': '#A5FFD6',
        'app': '#AA99FF',
        'other': '#B8B8FF',
        'tests': '#CCCCCC',
        'alembic': '#888888',
        'core': '#FFD6A5'
    }
    node_colors = [color_map.get(layers.get(n, 'other'), '#B8B8FF') for n in graph.nodes()]
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=350, alpha=0.85)
    nx.draw_networkx_edges(graph, pos, arrows=True, alpha=0.3)
    nx.draw_networkx_labels(graph, pos, font_size=8, font_color='black')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    logging.info(f"PNG-граф сохранён: {out_path}")

def export_graphml(graph: nx.DiGraph, out_path: Path):
    """Экспортирует граф в GraphML."""
    nx.write_graphml(graph, out_path)
    logging.info(f"GraphML сохранён: {out_path}")

def export_html_pyvis(graph: nx.DiGraph, out_path: Path):
    """Пытается экспортировать граф в HTML через pyvis."""
    try:
        from pyvis.network import Network
        net = Network(height='900px', width='100%', directed=True, notebook=False)
        layer_colors = {
            'domain': '#FF6B6B',
            'infrastructure': '#4ECDC4',
            'presentation': '#FFE66D',
            'shared': '#A5FFD6',
            'app': '#AA99FF',
            'other': '#B8B8FF',
            'tests': '#CCCCCC',
            'alembic': '#888888',
            'core': '#FFD6A5'
        }
        for node in graph.nodes():
            layer = graph.nodes[node].get('layer', 'other')
            net.add_node(
                node,
                label=node.split('/')[-1],
                title=graph.nodes[node].get('title', node),
                color=layer_colors.get(layer, '#B8B8FF'),
                size=min(30, max(5, graph.nodes[node].get('size', 10) / 10000))
            )
        for u, v in graph.edges():
            weight = graph.edges[u, v].get('weight', 1)
            net.add_edge(
                u, v,
                width=min(5, max(1, weight)),
                title=f"{weight} imports"
            )
        net.show(str(out_path))
        logging.info(f"HTML-граф сохранён: {out_path}")
    except Exception as e:
        logging.warning(f"Pyvis visualization failed: {e}")

def export_plantuml(graph: nx.DiGraph, out_path: Path):
    """Экспортирует граф зависимостей в PlantUML format."""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('@startuml\n')
        for node in graph.nodes():
            label = node.replace('/', '_').replace('.', '_').replace('-', '_')
            f.write(f'class {label}\n')
        for u, v in graph.edges():
            u_label = u.replace('/', '_').replace('.', '_').replace('-', '_')
            v_label = v.replace('/', '_').replace('.', '_').replace('-', '_')
            f.write(f'{u_label} --> {v_label}\n')
        f.write('@enduml\n')
    logging.info(f"PlantUML сохранён: {out_path}")

def analyze_architecture(graph: nx.DiGraph) -> str:
    """Анализирует архитектуру, возвращает текстовый отчет с нарушениями и связями между слоями."""
    report = []
    report.append("\n🔍 Архитектурный аудит SisuDatuBot:")
    layers = nx.get_node_attributes(graph, 'layer')
    layer_stats = defaultdict(lambda: {'count': 0, 'size': 0})
    for node, layer in layers.items():
        layer_stats[layer]['count'] += 1
        layer_stats[layer]['size'] += graph.nodes[node].get('size', 0)
    report.append("\n📊 Статистика по слоям:")
    for layer, stats in sorted(layer_stats.items()):
        avg_size = stats['size'] / stats['count'] if stats['count'] else 0
        report.append(f"  {layer.upper():<15}: {stats['count']:>3} модулей | Средний размер: {avg_size:,.0f} байт")
    report.append("\n🔗 Связи между слоями:")
    dep_directions = defaultdict(int)
    for u, v in graph.edges():
        u_layer = graph.nodes[u].get('layer', 'other')
        v_layer = graph.nodes[v].get('layer', 'other')
        dep_directions[(u_layer, v_layer)] += 1
    for (src, tgt), count in sorted(dep_directions.items(), key=lambda x: -x[1]):
        report.append(f"  {src.upper():<15} → {tgt.upper():<15}: {count:>4} связей")
    # Нарушения архитектуры (Clean Architecture)
    forbidden_edges = [
        ('presentation', 'infrastructure'),
        ('presentation', 'alembic'),
        ('presentation', 'core'),
        ('presentation', 'shared'),
        ('infrastructure', 'presentation'),
        ('infrastructure', 'domain'),
        ('domain', 'presentation'),
        ('domain', 'infrastructure'),
        ('tests', 'domain'),
        ('tests', 'infrastructure'),
        ('tests', 'presentation'),
    ]
    violations = []
    for u, v in graph.edges():
        u_layer = graph.nodes[u].get('layer', 'other')
        v_layer = graph.nodes[v].get('layer', 'other')
        if (u_layer, v_layer) in forbidden_edges:
            violations.append((u, v, u_layer, v_layer))
    if violations:
        report.append("\n⚠️ Нарушения архитектуры (Clean Architecture):")
        for u, v, u_layer, v_layer in violations[:10]:
            report.append(f"  {u_layer.upper()} → {v_layer.upper()}: {u} → {v}")
        if len(violations) > 10:
            report.append(f"  ... и еще {len(violations) - 10} нарушений")
    else:
        report.append("\n✅ Нарушений архитектуры не обнаружено!")
    betweenness = nx.betweenness_centrality(graph)
    critical = sorted(betweenness.items(), key=lambda x: -x[1])[:5]
    report.append("\n🔝 Наиболее критические модули:")
    for module, score in critical:
        report.append(f"  {module.split('/')[-1]:<30} (centrality: {score:.3f})")
    return '\n'.join(report)

def main():
    print("\n🚀 SisuDatuBot Architecture Audit 2025\n")
    start_time = time.time()
    root_dir = Path('.')
    python_files = find_python_files(root_dir)
    filtered_files = [f for f in python_files if not should_skip_file(f)]
    print(f"🔍 Python файлов для анализа: {len(filtered_files)} (из {len(python_files)})")
    graph, details = build_dependency_graph(filtered_files)
    print(f"📊 Граф: {len(graph.nodes)} модулей, {len(graph.edges)} связей")
    # Экспорт
    export_graphml(graph, AUDIT_DIR / 'dependencies.graphml')
    export_graph_png(graph, AUDIT_DIR / 'dependencies.png')
    export_html_pyvis(graph, AUDIT_DIR / 'dependencies.html')
    export_plantuml(graph, AUDIT_DIR / 'dependencies.puml')
    # Анализ и отчет
    report = analyze_architecture(graph)
    print(report)
    with open(AUDIT_DIR / 'architecture_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ Все результаты сохранены в папке: {AUDIT_DIR.resolve()}")
    print(f"⏱️ Время выполнения: {time.time() - start_time:.2f} сек\n")
    # --- CI/CD exit code logic ---
    if '--ci' in sys.argv:
        if 'Нарушения архитектуры' in report:
            print('❌ Архитектурные нарушения обнаружены! PR будет заблокирован.')
            sys.exit(1)
        else:
            print('✅ Архитектурных нарушений не найдено.')
            sys.exit(0)

if __name__ == '__main__':
    main() 