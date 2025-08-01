#!/usr/bin/env python3
"""
Полный аудит проекта SisuDatuBot
Проверяет все папки, файлы и их расположение
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ProjectAuditor:
    """Полный аудит проекта"""
    
    def __init__(self):
        self.base = Path(".")
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "project_structure": {},
            "file_counts": {},
            "migration_status": {},
            "issues": [],
            "recommendations": []
        }
    
    def scan_directory(self, path: Path, max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
        """Рекурсивное сканирование директории"""
        if current_depth > max_depth:
            return {"type": "max_depth_reached"}
        
        result = {
            "type": "directory",
            "path": str(path),
            "exists": path.exists(),
            "files": [],
            "directories": [],
            "total_files": 0,
            "total_dirs": 0
        }
        
        if not path.exists():
            return result
        
        try:
            for item in path.iterdir():
                if item.is_file():
                    file_info = {
                        "name": item.name,
                        "size": item.stat().st_size,
                        "extension": item.suffix,
                        "is_python": item.suffix == '.py',
                        "is_json": item.suffix == '.json',
                        "is_config": item.name in ['.env', 'config.yml', 'settings.py']
                    }
                    result["files"].append(file_info)
                    result["total_files"] += 1
                    
                elif item.is_dir():
                    if not item.name.startswith('.') and not item.name in ['__pycache__', 'node_modules', '.git']:
                        sub_dir = self.scan_directory(item, max_depth, current_depth + 1)
                        result["directories"].append(sub_dir)
                        result["total_dirs"] += 1
                        
        except PermissionError:
            result["error"] = "Permission denied"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def audit_migration_status(self):
        """Проверка статуса миграции"""
        print("🔄 Проверка статуса миграции...")
        
        # Проверяем что перенесено
        migrated_files = [
            "app/domain/services/user.py",
            "app/domain/services/gamification/points.py",
            "app/domain/services/gamification/top.py",
            "app/domain/services/games.py",
            "app/domain/services/motivation.py",
            "app/domain/services/triggers/core.py",
            "app/domain/services/triggers/stats.py",
            "app/infrastructure/ai/providers/yandex_gpt.py",
            "app/infrastructure/db/models.py",
            "app/infrastructure/db/session.py",
            "app/shared/config/settings.py",
            "app/presentation/bot/handlers/ai.py",
            "app/presentation/bot/middlewares/rate_limiter.py"
        ]
        
        # Проверяем что осталось в старых местах
        old_files = [
            "sisu_bot/bot/services/user_service.py",
            "sisu_bot/bot/services/points_service.py",
            "sisu_bot/bot/services/top_service.py",
            "sisu_bot/bot/services/games_service.py",
            "sisu_bot/bot/services/motivation_service.py",
            "sisu_bot/bot/services/trigger_service.py",
            "sisu_bot/bot/services/trigger_stats_service.py",
            "sisu_bot/bot/db/models.py",
            "sisu_bot/bot/db/session.py",
            "sisu_bot/core/config.py"
        ]
        
        migration_status = {
            "migrated": [],
            "not_migrated": [],
            "old_files_removed": [],
            "old_files_still_exist": []
        }
        
        for file_path in migrated_files:
            if Path(file_path).exists():
                migration_status["migrated"].append(file_path)
                print(f"✅ {file_path}")
            else:
                migration_status["not_migrated"].append(file_path)
                print(f"❌ {file_path}")
        
        print("\n📋 Старые файлы:")
        for file_path in old_files:
            if Path(file_path).exists():
                migration_status["old_files_still_exist"].append(file_path)
                print(f"⚠️ {file_path} (все еще существует)")
            else:
                migration_status["old_files_removed"].append(file_path)
                print(f"✅ {file_path} (удален)")
        
        self.audit_results["migration_status"] = migration_status
        return migration_status
    
    def audit_file_types(self):
        """Аудит типов файлов"""
        print("\n📊 Аудит типов файлов...")
        
        file_types = {
            "python": 0,
            "json": 0,
            "yaml": 0,
            "markdown": 0,
            "sql": 0,
            "log": 0,
            "other": 0
        }
        
        total_files = 0
        
        for root, dirs, files in os.walk(self.base):
            # Пропускаем системные папки
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                total_files += 1
                file_path = Path(root) / file
                extension = file_path.suffix.lower()
                
                if extension == '.py':
                    file_types["python"] += 1
                elif extension == '.json':
                    file_types["json"] += 1
                elif extension in ['.yml', '.yaml']:
                    file_types["yaml"] += 1
                elif extension == '.md':
                    file_types["markdown"] += 1
                elif extension == '.sql':
                    file_types["sql"] += 1
                elif extension == '.log':
                    file_types["log"] += 1
                else:
                    file_types["other"] += 1
        
        print(f"📈 Всего файлов: {total_files}")
        for file_type, count in file_types.items():
            if count > 0:
                print(f"   {file_type}: {count}")
        
        self.audit_results["file_counts"] = file_types
        return file_types
    
    def audit_key_directories(self):
        """Аудит ключевых директорий"""
        print("\n🔍 Аудит ключевых директорий...")
        
        key_dirs = [
            "app",
            "sisu_bot", 
            "backup_original",
            "data",
            "tests",
            "migrations",
            "scripts"
        ]
        
        for dir_name in key_dirs:
            dir_path = self.base / dir_name
            if dir_path.exists():
                files_count = len(list(dir_path.rglob("*")))
                dirs_count = len([d for d in dir_path.rglob("*") if d.is_dir()])
                print(f"📁 {dir_name}/: {files_count} файлов, {dirs_count} папок")
            else:
                print(f"❌ {dir_name}/: не существует")
    
    def generate_recommendations(self):
        """Генерация рекомендаций"""
        print("\n💡 Генерация рекомендаций...")
        
        recommendations = []
        
        # Проверяем DI контейнер
        if not Path("app/core/container.py").exists():
            recommendations.append("❌ Отсутствует DI контейнер: app/core/container.py")
        else:
            recommendations.append("✅ DI контейнер найден")
        
        # Проверяем конфигурацию
        if not Path("app/shared/config/settings.py").exists():
            recommendations.append("❌ Отсутствует конфигурация: app/shared/config/settings.py")
        else:
            recommendations.append("✅ Конфигурация найдена")
        
        # Проверяем основные сервисы
        core_services = [
            "app/domain/services/user.py",
            "app/domain/services/gamification/points.py",
            "app/infrastructure/db/models.py"
        ]
        
        for service in core_services:
            if Path(service).exists():
                recommendations.append(f"✅ {service}")
            else:
                recommendations.append(f"❌ Отсутствует: {service}")
        
        # Проверяем тесты
        if not Path("tests").exists():
            recommendations.append("⚠️ Папка tests не найдена")
        
        # Проверяем .env
        if not Path(".env").exists():
            recommendations.append("⚠️ Файл .env не найден")
        
        self.audit_results["recommendations"] = recommendations
        return recommendations
    
    def run_full_audit(self):
        """Запуск полного аудита"""
        print("🚀 ЗАПУСК ПОЛНОГО АУДИТА ПРОЕКТА")
        print("=" * 60)
        
        # 1. Сканируем всю структуру
        print("📁 Сканирование структуры проекта...")
        project_structure = self.scan_directory(self.base)
        self.audit_results["project_structure"] = project_structure
        
        # 2. Аудит миграции
        migration_status = self.audit_migration_status()
        
        # 3. Аудит типов файлов
        file_types = self.audit_file_types()
        
        # 4. Аудит ключевых директорий
        self.audit_key_directories()
        
        # 5. Генерация рекомендаций
        recommendations = self.generate_recommendations()
        
        # 6. Сохраняем результаты
        audit_file = f"project_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Результаты сохранены в: {audit_file}")
        
        # 7. Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ:")
        print(f"📁 Всего файлов: {file_types.get('python', 0) + file_types.get('json', 0) + file_types.get('other', 0)}")
        print(f"🐍 Python файлов: {file_types.get('python', 0)}")
        print(f"📋 JSON файлов: {file_types.get('json', 0)}")
        print(f"✅ Перенесено файлов: {len(migration_status.get('migrated', []))}")
        print(f"❌ Не перенесено: {len(migration_status.get('not_migrated', []))}")
        print(f"🗑️ Удалено старых: {len(migration_status.get('old_files_removed', []))}")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        for rec in recommendations:
            print(f"   {rec}")
        
        return self.audit_results

if __name__ == "__main__":
    auditor = ProjectAuditor()
    auditor.run_full_audit() 