from .gamification.points import *
from .gamification.ranks import *
from .gamification.video import *
from .gamification.photo import *
from .gamification.text import *
from .gamification.top import *
from .gamification.checkin import *
from .triggers.core import *
from .triggers.stats import *
from .motivation_service import *
from .games_service import *
from .user_service import *
from .excuse import *
from .state import *
from .ton import *
from .command_menu import *
from .games import *
from .mood import *
from .quiz import *
from .user import *
from .motivation import *
from .default_commands import *
from .admin_commands import *
from .superadmin_commands import *

# Экспорт points_service для обратной совместимости
import app.domain.services.gamification.points as points_service
import app.domain.services.gamification.top as top_service
