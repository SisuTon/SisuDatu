import pytest
from unittest.mock import AsyncMock, patch, mock_open
from sisu_bot.bot.services.tts_service import (
    can_use_tts,
    register_tts_usage,
    save_motivation_tts,
    MOTIVATION_PHRASES,
    handle_tts_request,
    send_tts_motivation
)

def test_can_use_tts():
    """Test TTS usage permissions"""
    # Test regular user
    user_id = 123
    assert can_use_tts(user_id) == True  # Initial state
    
    # Test usage limit
    for _ in range(3):
        register_tts_usage(user_id)
    assert can_use_tts(user_id) == False  # Should be at limit
    
    # Test superadmin (should always be allowed)
    superadmin_id = 999
    with patch('sisu_bot.bot.services.tts_service.is_superadmin', return_value=True):
        assert can_use_tts(superadmin_id) == True

def test_register_tts_usage():
    """Test TTS usage registration"""
    user_id = 456
    
    # Test initial usage
    register_tts_usage(user_id)
    assert can_use_tts(user_id) == True
    
    # Test multiple usages
    for _ in range(2):
        register_tts_usage(user_id)
    assert can_use_tts(user_id) == False
    
    # Test superadmin usage (should not count)
    superadmin_id = 999
    with patch('sisu_bot.bot.services.tts_service.is_superadmin', return_value=True):
        register_tts_usage(superadmin_id)
        assert can_use_tts(superadmin_id) == True

@patch('builtins.open', new_callable=mock_open)
def test_save_motivation_tts(mock_file):
    """Test saving motivation phrases"""
    # Test saving empty list
    global MOTIVATION_PHRASES
    MOTIVATION_PHRASES = []
    save_motivation_tts()
    mock_file.assert_called_once()
    
    # Test saving with phrases
    MOTIVATION_PHRASES = ["Мотивация 1", "Мотивация 2"]
    save_motivation_tts()
    assert mock_file.call_count == 2

@pytest.mark.asyncio
async def test_handle_tts_request():
    """Test TTS request handling"""
    # Mock message object
    message = AsyncMock()
    
    # Test successful TTS
    with patch('sisu_bot.bot.services.tts_service.synthesize_sisu_voice') as mock_synth:
        mock_synth.return_value = b"fake_voice_data"
        await handle_tts_request(message, "тестовый текст")
        message.answer_voice.assert_called_once()
    
    # Test TTS failure
    message.reset_mock() # Reset mock calls before testing failure case
    with patch('sisu_bot.bot.services.tts_service.synthesize_sisu_voice') as mock_synth:
        mock_synth.side_effect = Exception("TTS failed")
        await handle_tts_request(message, "тестовый текст")
        message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_send_tts_motivation():
    """Test sending motivation TTS"""
    # Mock message object
    message = AsyncMock()
    
    # Scenario 1: No motivation phrases
    with patch('sisu_bot.bot.services.tts_service.MOTIVATION_PHRASES', []):
        await send_tts_motivation(message)
        message.answer.assert_called_once_with("У меня пока нет мотивационных фраз 😔")
        message.answer_voice.assert_not_called()
    
    # Reset mocks for the next scenario
    message.reset_mock()
    
    # Scenario 2: With motivation phrases
    with patch('sisu_bot.bot.services.tts_service.MOTIVATION_PHRASES', ["Мотивация 1"]):
        with patch('sisu_bot.bot.services.tts_service.synthesize_sisu_voice') as mock_synth:
            mock_synth.return_value = b"fake_voice_data"
            await send_tts_motivation(message)
            message.answer_voice.assert_called_once()
            message.answer.assert_not_called() 