import json
import os
import datetime
from sisu_bot.bot.db.init_db import Session, engine
from sisu_bot.bot.db.models import User
from sisu_bot.bot.config import ADMIN_IDS, SUPERADMIN_IDS
from sisu_bot.core.config import DB_PATH
from sqlalchemy import text

USERS_JSON = os.path.join(os.path.dirname(__file__), '../../data/users.json')

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