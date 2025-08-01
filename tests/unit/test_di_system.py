from app.core.container import Container

def test_di_container_games():
    container = Container()
    games_service = container.games_service()
    assert games_service is not None
    assert hasattr(games_service, 'bulk_add_emoji_movies')
    assert hasattr(games_service, 'get_random_emoji_movie')
    assert hasattr(games_service, 'check_emoji_movie_answer') 