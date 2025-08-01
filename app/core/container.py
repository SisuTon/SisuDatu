"""
DI Container для SisuDatuBot (Modern Python 2025)
"""
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from typing import AsyncContextManager
import logging

# Infrastructure imports
from app.infrastructure.db.session import get_async_session
from app.infrastructure.ai.providers.yandex_gpt import YandexGPTService
from app.infrastructure.ai.tts import TTSService
from app.infrastructure.system.adminlog_service import AdminLogService
from app.infrastructure.system.allowed_chats import AllowedChatsService

# Domain imports
from app.domain.services.user import UserService
from app.domain.services.gamification.points import PointsService
from app.domain.services.gamification.top import TopService
from app.domain.services.games import GamesService
from app.domain.services.motivation import MotivationService
from app.domain.services.triggers.core import TriggerService
from app.domain.services.triggers.stats import TriggerStatsService

# Shared imports
from app.shared.config.settings import Settings

class Container(containers.DeclarativeContainer):
    """Основной контейнер зависимостей SisuDatuBot"""
    
    # Configuration
    config = providers.Singleton(Settings)
    
    # -----------------------------------------------
    # 1. Infrastructure Layer
    # -----------------------------------------------
    
    # Database
    db_session = providers.Resource(
        get_async_session,
        database_url=config.provided.database_url,
    )
    
    # AI Services
    yandex_gpt_service = providers.Singleton(
        YandexGPTService,
        api_key=config.provided.yandex_api_key,
        base_url=config.provided.yandex_base_url,
    )
    
    tts_service = providers.Singleton(
        TTSService,
        api_key=config.provided.yandex_api_key,
    )
    
    # System Services
    adminlog_service = providers.Singleton(
        AdminLogService,
        data_file=config.provided.adminlog_file,
    )
    
    allowed_chats_service = providers.Singleton(
        AllowedChatsService,
        data_file=config.provided.allowed_chats_file,
    )
    
    # -----------------------------------------------
    # 2. Domain Layer
    # -----------------------------------------------
    
    # Gamification Services
    points_service = providers.Singleton(
        PointsService,
        session=db_session,
        config=config,
    )
    
    top_service = providers.Singleton(
        TopService,
        session=db_session,
        points_service=points_service,
    )
    
    games_service = providers.Singleton(
        GamesService,
        session=db_session,
        config=config,
    )
    
    motivation_service = providers.Singleton(
        MotivationService,
        session=db_session,
        config=config,
    )
    
    # Trigger Services
    trigger_service = providers.Singleton(
        TriggerService,
        session=db_session,
        config=config,
    )
    
    trigger_stats_service = providers.Singleton(
        TriggerStatsService,
        session=db_session,
        config=config,
    )
    
    # User Service
    user_service = providers.Singleton(
        UserService,
        session=db_session,
        points_service=points_service,
        top_service=top_service,
        config=config,
    )
    
    # -----------------------------------------------
    # 3. Utils & Shared
    # -----------------------------------------------
    logger = providers.Singleton(
        lambda: logging.getLogger('sisu_bot')
    )