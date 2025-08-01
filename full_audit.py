import os
import json
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List
import datetime

class ProjectAuditor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.report = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "project_root": str(self.project_root)
            },
            "structure": {},
            "di_analysis": {},
            "migration_status": {},
            "dependencies": [],
            "docker_files": [],
            "issues": []
        }

    def scan_structure(self) -> Dict:
        """Сканирует структуру проекта, игнорируя скрытые папки."""
        structure = {}
        for root, dirs, files in os.walk(self.project_root):
            # Исключаем скрытые и служебные папки
            dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
            files = [f for f in files if not f.startswith('.')]
            rel_path = os.path.relpath(root, self.project_root)
            structure[rel_path] = {
                "files": files,
                "dirs": dirs,
                "size": sum(os.path.getsize(os.path.join(root, f)) for f in files 
                          if os.path.isfile(os.path.join(root, f)))
            }
        self.report["structure"] = structure
        return structure

    def analyze_di(self) -> Dict:
        """Анализирует DI-контейнеры с проверкой типов."""
        di_data = {}
        for di_file in self.project_root.glob("**/*container*.py"):
            try:
                spec = importlib.util.spec_from_file_location("di_module", di_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                providers = []
                for name, obj in module.__dict__.items():
                    if "Container" in name or "Provider" in name:
                        providers.append(name)
                di_data[str(di_file.relative_to(self.project_root))] = {
                    "providers": providers,
                    "dependencies": self._find_di_dependencies(di_file)
                }
            except Exception as e:
                self.report["issues"].append(f"DI analysis failed for {di_file}: {str(e)}")
        self.report["di_analysis"] = di_data
        return di_data

    def check_migration(self) -> Dict:
        """Проверяет миграцию с учетом переименований."""
        old_new_map = {
            "sisu_bot/bot/services/": "app/domain/services/",
            "sisu_bot/core/config.py": "app/shared/config/settings.py"
        }
        migration_status = {"migrated": [], "not_migrated": []}
        for old_path, new_path in old_new_map.items():
            old_file = self.project_root / old_path
            if old_file.exists():
                new_file = self.project_root / new_path
                status = "migrated" if new_file.exists() else "not_migrated"
                migration_status[status].append(str(old_file.relative_to(self.project_root)))
        self.report["migration_status"] = migration_status
        return migration_status

    def generate_report(self, format: str = "all") -> None:
        """Генерирует отчеты и возвращает статус."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_report_path = self.project_root / f"audit_report_{timestamp}.json"
        md_report_path = self.project_root / f"audit_report_{timestamp}.md"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)
        if format in ("md", "all"):
            self._generate_markdown_report(md_report_path)
            # Выводим Markdown-отчёт в терминал
            with open(md_report_path, 'r', encoding='utf-8') as f:
                print("\n" + "="*40 + "\nАУДИТ (Markdown):\n" + "="*40)
                print(f.read())
        self.print_summary()
        print(f"\n📄 Отчеты сохранены:\n- JSON: {json_report_path}\n- Markdown: {md_report_path}")
        if self.report["issues"]:
            sys.exit(1)  # Для CI/CD

    def print_summary(self):
        print("\n=== КРАТКОЕ SUMMARY ===")
        print(f"Дата: {self.report['metadata']['timestamp']}")
        print(f"Всего файлов: {sum(len(data['files']) for data in self.report['structure'].values())}")
        print(f"Перенесено: {len(self.report['migration_status']['migrated'])}")
        print(f"Не перенесено: {len(self.report['migration_status']['not_migrated'])}")
        if self.report['issues']:
            print("Проблемы:")
            for issue in self.report['issues']:
                print(" -", issue)
        else:
            print("Нет критических проблем")

    def _find_di_dependencies(self, di_file: Path) -> List[str]:
        dependencies = []
        with open(di_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            for line in lines:
                if "import" in line or "from" in line:
                    dependencies.append(line.strip())
                elif "providers." in line or "Factory(" in line:
                    dependencies.append(line.strip())
        return dependencies

    def _generate_markdown_report(self, path: Path) -> None:
        md_content = f"""# Аудит проекта: {self.project_root.name}

## 📌 Метаданные
- **Дата аудита**: {self.report['metadata']['timestamp']}
- **Всего файлов**: {sum(len(data['files']) for data in self.report['structure'].values())}

## 🏗 Структура проекта
```json
{json.dumps(self.report['structure'], indent=2)}
```

## ⚙️ DI-анализ
```json
{json.dumps(self.report['di_analysis'], indent=2)}
```

## 🚦 Статус миграции
- **Перенесено**: {len(self.report['migration_status']['migrated'])}
- **Не перенесено**: {len(self.report['migration_status']['not_migrated'])}

## 🚨 Проблемы
{'- ' + '\n- '.join(self.report['issues']) if self.report['issues'] else 'Нет критических проблем'}
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(md_content)

if __name__ == "__main__":
    print("🚀 Запуск аудита проекта...")
    auditor = ProjectAuditor(os.getcwd())
    auditor.scan_structure()
    auditor.analyze_di()
    auditor.check_migration()
    auditor.generate_report() 