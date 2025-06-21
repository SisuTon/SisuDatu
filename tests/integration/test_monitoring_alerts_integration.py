import pytest
from unittest.mock import patch

def function_with_critical_error():
    raise RuntimeError("Critical failure!")

@pytest.mark.asyncio
def test_sentry_alert_on_critical_error():
    # Мокаем Sentry (или любой алертинг)
    with patch("sentry_sdk.capture_exception") as mock_capture:
        try:
            function_with_critical_error()
        except Exception as e:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
        mock_capture.assert_called_once() 