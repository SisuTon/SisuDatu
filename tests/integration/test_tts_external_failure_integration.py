import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from sisu_bot.bot.services import yandex_speechkit_tts

@pytest.mark.asyncio
async def test_tts_yandex_api_failure():
    # Создаем мок для ответа с ошибкой
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.text = AsyncMock(return_value="Internal Server Error")
    mock_response.read = AsyncMock(return_value=b'')
    
    # Создаем мок для ClientSession
    mock_session = AsyncMock()
    mock_session.post = AsyncMock(return_value=mock_response)
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        with pytest.raises(Exception) as excinfo:
            await yandex_speechkit_tts.synthesize_sisu_voice("Привет, мир!", voice="jane")
        assert "SpeechKit TTS error" in str(excinfo.value) or "Internal Server Error" in str(excinfo.value)

@pytest.mark.asyncio
async def test_tts_yandex_api_timeout():
    # Создаем мок для ClientSession с timeout
    mock_session = AsyncMock()
    mock_session.post = AsyncMock(side_effect=asyncio.TimeoutError("Connection timeout!"))
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        with pytest.raises(Exception) as excinfo:
            await yandex_speechkit_tts.synthesize_sisu_voice("Привет, мир!", voice="jane")
        assert "Network error" in str(excinfo.value) or "Timeout" in str(excinfo.value) 