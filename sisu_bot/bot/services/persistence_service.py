"""
Сервис для персистентного хранения данных в БД
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sisu_bot.core.config import DB_PATH
import logging

logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class PersistentData(Base):
    __tablename__ = 'persistent_data'
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PersistenceService:
    def __init__(self):
        self._ensure_table()
    
    def _ensure_table(self):
        """Создает таблицу если не существует"""
        Base.metadata.create_all(engine)
    
    def save_data(self, key: str, data: Dict[str, Any]):
        """Сохраняет данные в БД"""
        session = Session()
        try:
            # Ищем существующую запись
            record = session.query(PersistentData).filter(PersistentData.key == key).first()
            
            if record:
                # Обновляем существующую запись
                record.value = json.dumps(data, ensure_ascii=False)
                record.updated_at = datetime.utcnow()
            else:
                # Создаем новую запись
                record = PersistentData(
                    key=key,
                    value=json.dumps(data, ensure_ascii=False)
                )
                session.add(record)
            
            session.commit()
            logger.info(f"Data saved for key: {key}")
            
        except Exception as e:
            logger.error(f"Error saving data for key {key}: {e}")
            session.rollback()
        finally:
            session.close()
    
    def load_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Загружает данные из БД"""
        session = Session()
        try:
            record = session.query(PersistentData).filter(PersistentData.key == key).first()
            
            if record:
                data = json.loads(record.value)
                logger.info(f"Data loaded for key: {key}")
                return data
            else:
                logger.info(f"No data found for key: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading data for key {key}: {e}")
            return None
        finally:
            session.close()
    
    def delete_data(self, key: str):
        """Удаляет данные из БД"""
        session = Session()
        try:
            record = session.query(PersistentData).filter(PersistentData.key == key).first()
            if record:
                session.delete(record)
                session.commit()
                logger.info(f"Data deleted for key: {key}")
        except Exception as e:
            logger.error(f"Error deleting data for key {key}: {e}")
            session.rollback()
        finally:
            session.close()
    
    def cleanup_old_data(self, days: int = 30):
        """Очищает старые данные"""
        session = Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            old_records = session.query(PersistentData).filter(
                PersistentData.updated_at < cutoff_date
            ).all()
            
            for record in old_records:
                session.delete(record)
            
            session.commit()
            logger.info(f"Cleaned up {len(old_records)} old records")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            session.rollback()
        finally:
            session.close()

# Глобальный экземпляр
persistence_service = PersistenceService() 