import pytest
from datetime import datetime
from sisu_bot.bot.db.models import User
from sisu_bot.bot.services.points_service import add_points
from sisu_bot.core.config import SUPERADMIN_IDS, ADMIN_IDS

@pytest.mark.usefixtures("session")
def test_admin_add_points(session):
    user = User(id=2002, points=0)
    session.add(user)
    session.commit()
    add_points(user.id, 100)
    user = session.query(User).filter(User.id == 2002).first()
    assert user.points == 100 