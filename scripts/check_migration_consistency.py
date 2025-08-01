import os
from pathlib import Path
import difflib

BACKUP_DIR = Path('backup_remaining/sisu_bot')
NEW_ROOT = Path('app')

# Собираем все файлы из backup_remaining/sisu_bot
old_files = [f for f in BACKUP_DIR.rglob('*') if f.is_file()]
# Собираем все файлы из app
new_files = [f for f in NEW_ROOT.rglob('*') if f.is_file()]

# Приводим к относительным путям (без backup_remaining/sisu_bot и app)
old_rel = set(str(f.relative_to(BACKUP_DIR)) for f in old_files)
new_rel = set(str(f.relative_to(NEW_ROOT)) for f in new_files)

# 1. Какие файлы из backup_remaining отсутствуют в app (не перенесены)
missing = sorted(old_rel - new_rel)

# 2. Сопоставление по шаблонам и логике
mapping = [
    ("bot/middlewares/allowed_chats_middleware.py", "presentation/bot/middlewares/allowed_chats.py"),
    ("bot/middlewares/antifraud.py", "presentation/bot/middlewares/antifraud.py"),
    ("bot/middlewares/preprocess.py", "presentation/bot/middlewares/preprocess.py"),
    ("bot/middlewares/user_sync.py", "presentation/bot/middlewares/user_sync.py"),
    ("bot/points/checkin.py", "domain/services/gamification/checkin.py"),
    ("bot/points/photo.py", "domain/services/gamification/photo.py"),
    ("bot/points/text.py", "domain/services/gamification/text.py"),
    ("bot/points/video.py", "domain/services/gamification/video.py"),
    ("bot/quiz/quiz_handler.py", "presentation/bot/handlers/quiz.py"),
    ("bot/quiz/quiz_service.py", "domain/services/quiz.py"),
    ("bot/ranks/rank_utils.py", "domain/services/gamification/ranks.py"),
    ("bot/services/adminlog_service.py", "infrastructure/system/adminlog.py"),
    ("bot/services/ai_memory_service.py", "infrastructure/ai/memory.py"),
    ("bot/services/ai_stats_service.py", "infrastructure/ai/stats.py"),
    ("bot/services/ai_trigger_service.py", "infrastructure/ai/trigger.py"),
    ("bot/services/allowed_chats_service.py", "infrastructure/system/allowed_chats.py"),
    ("bot/services/command_menu_service.py", "domain/services/command_menu.py"),
    ("bot/services/excuse_service.py", "domain/services/excuse.py"),
    ("bot/services/mood_service.py", "domain/services/mood.py"),
    ("bot/services/persona_service.py", "infrastructure/ai/persona.py"),
    ("bot/services/state_service.py", "domain/services/state.py"),
    ("bot/services/ton_service.py", "domain/services/ton.py"),
    ("bot/services/tts_service.py", "infrastructure/ai/tts.py"),
    ("bot/states/quiz.py", "presentation/bot/states/quiz.py"),
    ("bot/ton/ton_utils.py", "infrastructure/ton/utils.py"),
    ("bot/utils.py", "shared/utils/bot_utils.py"),
    ("core/database.py", "infrastructure/db/database.py"),
    ("core/interfaces.py", "shared/interfaces.py"),
    ("core/service_registry.py", "core/service_registry_old.py"),
    ("core/di.py", "core/di_old.py"),
]

print('==== Сопоставление отсутствующих файлов ====' if missing else 'Нет отсутствующих файлов!')
really_missing = []
for old in missing:
    found = False
    for old_pat, new_pat in mapping:
        if old == old_pat and new_pat in new_rel:
            print(f'{old} --> {new_pat} (ПЕРЕНЕСЁН, ПЕРЕИМЕНОВАН)')
            found = True
            break
    if not found:
        # Попробуем найти похожий файл по имени
        old_name = os.path.basename(old)
        matches = difflib.get_close_matches(old_name, [os.path.basename(n) for n in new_rel], n=1, cutoff=0.8)
        if matches:
            for n in new_rel:
                if os.path.basename(n) == matches[0]:
                    print(f'{old} --> {n} (ПОХОЖЕ, ПРОВЕРЬ ВРУЧНУЮ)')
                    found = True
                    break
    if not found:
        print(f'{old} --> (ОТСУТСТВУЕТ В app)')
        really_missing.append(old)

if really_missing:
    print('\n==== Реально отсутствуют в новой архитектуре ====' )
    for f in really_missing:
        print(f'- {f}')
else:
    print('\nВсе файлы из backup_remaining найдены в новой архитектуре (с учётом переименований)!') 