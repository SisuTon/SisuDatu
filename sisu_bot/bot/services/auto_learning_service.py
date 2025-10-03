import json
import logging
import os
from typing import Dict, List, Any
from collections import Counter
from datetime import datetime, timedelta
from sisu_bot.bot.services.message_service import message_service
from sisu_bot.core.config import DATA_DIR

logger = logging.getLogger(__name__)

LEARNING_DATA_PATH = DATA_DIR / 'learning_data.json'


class AutoLearningService:
    """Сервис для автоматического обучения бота на основе сообщений пользователей"""
    
    def __init__(self):
        self.learning_data = self._load_learning_data()
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Загружает данные обучения из файла"""
        try:
            if os.path.exists(LEARNING_DATA_PATH):
                with open(LEARNING_DATA_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"triggers": {}, "responses": {}}
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
            return {"triggers": {}, "responses": {}}
    
    def _save_learning_data(self):
        """Сохраняет данные обучения в файл"""
        try:
            with open(LEARNING_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
            logger.info("Learning data saved successfully")
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def extract_phrases_from_messages(self, messages: List[str], min_length: int = 3) -> List[str]:
        """Извлекает фразы из сообщений"""
        phrases = []
        
        for message in messages:
            if not message or len(message.strip()) < min_length:
                continue
            
            # Очищаем сообщение
            cleaned = message.strip().lower()
            
            # Разбиваем на предложения
            sentences = self._split_into_sentences(cleaned)
            
            for sentence in sentences:
                if len(sentence) >= min_length:
                    phrases.append(sentence)
        
        return phrases
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Разбивает текст на предложения"""
        import re
        
        # Простое разбиение по знакам препинания
        sentences = re.split(r'[.!?]+', text)
        
        # Очищаем и фильтруем
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= 3:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def find_popular_triggers(self, days: int = 7, min_count: int = 3) -> List[Dict[str, Any]]:
        """Находит популярные фразы, которые могут стать триггерами"""
        try:
            # Получаем популярные фразы из базы данных
            popular_phrases = message_service.get_popular_phrases(days=days, min_count=min_count)
            
            # Фильтруем фразы, которые уже есть в learning_data
            new_triggers = []
            existing_triggers = set(self.learning_data.get("triggers", {}).keys())
            
            for phrase_data in popular_phrases:
                phrase_text = phrase_data['text'].lower().strip()
                
                # Пропускаем если уже есть
                if phrase_text in existing_triggers:
                    continue
                
                # Пропускаем слишком длинные фразы
                if len(phrase_text) > 100:
                    continue
                
                # Пропускаем фразы с командами
                if phrase_text.startswith('/'):
                    continue
                
                new_triggers.append({
                    'trigger': phrase_text,
                    'count': phrase_data['count'],
                    'unique_users': phrase_data['unique_users']
                })
            
            return new_triggers
            
        except Exception as e:
            logger.error(f"Error finding popular triggers: {e}")
            return []
    
    def generate_responses_for_trigger(self, trigger: str) -> List[str]:
        """Генерирует ответы на основе РЕАЛЬНЫХ сообщений из чата!"""
        responses = []
        
        # Получаем реальные сообщения из базы данных для этого триггера
        try:
            from sisu_bot.bot.services.message_service import message_service
            
            # Ищем сообщения, которые содержат этот триггер
            related_messages = message_service.get_messages_by_text_pattern(trigger, limit=20)
            
            if related_messages:
                # Берем реальные ответы из чата
                for msg in related_messages:
                    if msg.message_text and len(msg.message_text.strip()) > 2:
                        # Добавляем реальные фразы из чата
                        responses.append(msg.message_text.strip())
                
                # Если нашли реальные фразы, используем их
                if responses:
                    # Убираем дубликаты и ограничиваем количество
                    unique_responses = list(set(responses))[:10]
                    return unique_responses
            
        except Exception as e:
            logger.error(f"Error getting real messages for trigger {trigger}: {e}")
        
        # Если не нашли реальные фразы, используем базовые дерзкие ответы
        responses.extend([
            "Ого! Интересно! Расскажи еще!",
            "Вау! Что еще скажешь?",
            "Круто! Продолжай!",
            "Офигенно! Еще что-то есть?",
            "Класс! Расскажи подробнее!",
            "Супер! Что думаешь об этом?",
            "Огонь! Еще идеи есть?",
            "Топ! Поделись еще!",
            "Красота! Что еще?",
            "Бомба! Расскажи больше!"
        ])
        
        return responses
    
    def auto_learn_from_messages(self, days: int = 7, min_count: int = 3, max_new_triggers: int = 10) -> Dict[str, Any]:
        """Автоматически обучается на основе сообщений пользователей"""
        try:
            logger.info(f"Starting auto-learning for last {days} days")
            
            # Находим популярные триггеры
            popular_triggers = self.find_popular_triggers(days=days, min_count=min_count)
            
            if not popular_triggers:
                logger.info("No new triggers found for auto-learning")
                return {
                    'success': True,
                    'new_triggers': 0,
                    'total_responses': 0,
                    'message': 'No new triggers found'
                }
            
            # Ограничиваем количество новых триггеров
            popular_triggers = popular_triggers[:max_new_triggers]
            
            added_triggers = 0
            total_responses = 0
            
            for trigger_data in popular_triggers:
                trigger = trigger_data['trigger']
                
                # Генерируем ответы для триггера
                responses = self.generate_responses_for_trigger(trigger)
                
                if responses:
                    # Добавляем в learning_data
                    self.learning_data["triggers"][trigger] = responses
                    added_triggers += 1
                    total_responses += len(responses)
                    
                    logger.info(f"Added trigger '{trigger}' with {len(responses)} responses")
            
            # Сохраняем обновленные данные
            if added_triggers > 0:
                self._save_learning_data()
                
                # Помечаем обработанные сообщения
                self._mark_messages_as_processed()
            
            result = {
                'success': True,
                'new_triggers': added_triggers,
                'total_responses': total_responses,
                'message': f'Added {added_triggers} new triggers with {total_responses} responses'
            }
            
            logger.info(f"Auto-learning completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in auto-learning: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Auto-learning failed'
            }
    
    def _mark_messages_as_processed(self):
        """Помечает сообщения как обработанные"""
        try:
            # Получаем необработанные сообщения
            unprocessed_messages = message_service.get_unprocessed_messages(limit=1000)
            
            if unprocessed_messages:
                message_ids = [msg.id for msg in unprocessed_messages]
                message_service.mark_as_processed(message_ids)
                logger.info(f"Marked {len(message_ids)} messages as processed")
                
        except Exception as e:
            logger.error(f"Error marking messages as processed: {e}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Получает статистику обучения"""
        try:
            triggers_count = len(self.learning_data.get("triggers", {}))
            total_responses = sum(
                len(responses) for responses in self.learning_data.get("triggers", {}).values()
            )
            
            # Получаем статистику сообщений
            message_stats = message_service.get_user_message_stats(1, days=30)  # Пример для user_id=1
            
            return {
                'triggers_count': triggers_count,
                'total_responses': total_responses,
                'messages_processed': message_stats.get('total_messages', 0),
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting learning stats: {e}")
            return {
                'triggers_count': 0,
                'total_responses': 0,
                'messages_processed': 0,
                'last_update': None
            }
    
    def cleanup_old_data(self, days: int = 90):
        """Очищает старые данные"""
        try:
            cleaned_count = message_service.cleanup_old_messages(days=days)
            logger.info(f"Cleaned up {cleaned_count} old messages")
            return cleaned_count
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0


# Глобальный экземпляр сервиса
auto_learning_service = AutoLearningService()
