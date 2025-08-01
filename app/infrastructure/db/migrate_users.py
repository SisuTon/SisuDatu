import json
import os
import datetime
from app.infrastructure.db.session import Session, engine
from app.infrastructure.db.models import User
from app.shared.config.bot_config import ADMIN_IDS, SUPERADMIN_IDS
from app.shared.config.settings import Settings
DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    from pathlib import Path
    DATA_DIR = Path(DATA_DIR)
USERS_JSON = DATA_DIR / 'users.json'
from sqlalchemy import text

def migrate_database():
    """Добавляет новые колонки в таблицу users"""
    try:
        with engine.connect() as conn:
            # Добавляем колонку supporter_tier
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN supporter_tier VARCHAR DEFAULT 'none'
            """))
            
            # Добавляем колонку supporter_until
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN supporter_until DATETIME
            """))
            conn.commit()
        
        print("Миграция базы данных успешно завершена")
    except Exception as e:
        print(f"Ошибка при миграции базы данных: {e}")

def migrate_users():
    if not os.path.exists(USERS_JSON):
        print(f'Файл {USERS_JSON} не найден. Миграция не требуется.')
        return
    with open(USERS_JSON, encoding='utf-8') as f:
        users_data = json.load(f)
    with Session() as session:
        for user_id, user in users_data.items():
            user_id_int = int(user_id)
            # Определяем роль
            if user_id_int in SUPERADMIN_IDS:
                role = 'superadmin'
            elif user_id_int in ADMIN_IDS:
                role = 'admin'
            else:
                role = 'user'
            # Преобразуем last_checkin
            last_checkin = user.get('last_checkin')
            if last_checkin:
                try:
                    last_checkin = datetime.datetime.fromisoformat(last_checkin)
                except Exception:
                    last_checkin = None
            else:
                last_checkin = None
            db_user = User(
                id=user_id_int,
                username=user.get('username'),
                first_name=user.get('first_name'),
                points=user.get('points', 0),
                rank=user.get('rank', 'novice'),
                active_days=user.get('active_days', 0),
                referrals=user.get('referrals', 0),
                message_count=user.get('message_count', 0),
                last_checkin=last_checkin,
                is_supporter=user.get('is_supporter', False),
                invited_by=int(user.get('invited_by')) if user.get('invited_by') else None,
                pending_referral=int(user.get('pending_referral')) if user.get('pending_referral') else None,
                role=role
            )
            session.merge(db_user)
        session.commit()

if __name__ == "__main__":
    migrate_database()
    migrate_users() 