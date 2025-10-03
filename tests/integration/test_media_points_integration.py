import pytest
from datetime import datetime
from sisu_bot.bot.db.models import User
from sisu_bot.bot.services.points_service import add_points
from sqlalchemy.orm import Session

def test_media_points(session: Session):
    """Test points for media content."""
    # Create test user
    user = User(
        id=1,
        username="test_user",
        first_name="Test User",
        points=0,
        rank="новичок",
        active_days=0,
        referrals=0,
        message_count=0,
        is_supporter=False,
        role="user",
        supporter_tier="none",
        photo_count=0,
        video_count=0,
        is_banned=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(user)
    session.commit()

    # Test photo points
    user.photo_count += 1
    add_points(user.id, 5)  # Points for photo
    session.commit()
    session.refresh(user)

    assert user.photo_count == 1
    assert user.points == 5

    # Test video points
    user.video_count += 1
    add_points(user.id, 10)  # Points for video
    session.commit()
    session.refresh(user)

    assert user.video_count == 1
    assert user.points == 15  # 5 (photo) + 10 (video) 