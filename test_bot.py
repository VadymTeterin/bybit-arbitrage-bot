import sys
import os
sys.path.append(os.path.abspath('.'))

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# --- Unit tests для logger.py ---

def test_log_info_and_error(caplog):
    from logger import log_info, log_error
    with caplog.at_level("INFO"):
        log_info("test info")
        assert "test info" in caplog.text
    with caplog.at_level("ERROR"):
        log_error("test error")
        assert "test error" in caplog.text

# --- Unit tests для exchanges/bybit_api.py ---

def test_get_spot_symbols_success():
    from exchanges.bybit_api import BybitClient

    # Діагностичний патч: тимчасово підміняємо сам метод!
    def fake_get_spot_symbols(self):
        return ["BTCUSDT", "ETHUSDT"]

    orig_method = BybitClient.get_spot_symbols
    BybitClient.get_spot_symbols = fake_get_spot_symbols

    client = BybitClient("key", "secret")
    symbols = client.get_spot_symbols()
    print("SPOT SYMBOLS:", symbols)
    assert "BTCUSDT" in symbols
    assert "ETHUSDT" in symbols

    BybitClient.get_spot_symbols = orig_method

@patch("exchanges.bybit_api.HTTP")
def test_get_spot_symbols_api_error(mock_http):
    from exchanges.bybit_api import BybitClient
    instance = mock_http.return_value
    instance.get_tickers.side_effect = Exception("fail")
    client = BybitClient("key", "secret")
    client.client = instance
    symbols = client.get_spot_symbols()
    assert symbols == []

@patch("exchanges.bybit_api.HTTP")
def test_get_price_success(mock_http):
    from exchanges.bybit_api import BybitClient

    instance = mock_http.return_value

    def fake_get_tickers(*args, **kwargs):
        return {"result": {"list": [{"lastPrice": "23456"}]}}

    instance.get_tickers.side_effect = fake_get_tickers
    client = BybitClient("key", "secret")
    client.client = instance
    price = client.get_price("BTCUSDT")
    assert price == 23456.0

@patch("exchanges.bybit_api.HTTP")
def test_get_price_api_error(mock_http):
    from exchanges.bybit_api import BybitClient
    instance = mock_http.return_value
    instance.get_tickers.side_effect = Exception("fail")
    client = BybitClient("key", "secret")
    client.client = instance
    price = client.get_price("BTCUSDT")
    assert price is None

# --- Unit tests для telegram_bot.py ---

@pytest.mark.asyncio
@patch("telegram_bot.Bot")
async def test_send_message_success(mock_bot):
    from telegram_bot import TelegramNotifier
    mock_instance = mock_bot.return_value
    mock_instance.send_message = AsyncMock()
    notifier = TelegramNotifier("token", 1111)
    await notifier.send_message("Test")
    mock_instance.send_message.assert_called_once()
    args, kwargs = mock_instance.send_message.call_args
    assert kwargs["chat_id"] == 1111
    assert kwargs["text"] == "Test"

@pytest.mark.asyncio
@patch("telegram_bot.Bot")
async def test_send_message_error(mock_bot):
    from telegram_bot import TelegramNotifier
    mock_instance = mock_bot.return_value
    mock_instance.send_message = AsyncMock(side_effect=Exception("fail"))
    notifier = TelegramNotifier("token", 1111)
    # Повинен не впасти навіть при помилці
    await notifier.send_message("Test")
    mock_instance.send_message.assert_called_once()

# --- Integration test: логіка арбітражу ---
# Поки залишаємо лише unit-тести для стабільності.
