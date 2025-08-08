import sys
import os
sys.path.append(os.path.abspath('.'))

import pytest
import asyncio
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

@pytest.mark.asyncio
@patch("exchanges.bybit_api.HTTP")
def test_get_spot_symbols_success(mock_http):
    from exchanges.bybit_api import BybitClient
    # Мокаємо відповідь біржі
    mock_http.return_value.get_tickers.return_value = {
        "result": {"list": [{"symbol": "BTCUSDT"}, {"symbol": "ETHUSDT"}]}
    }
    client = BybitClient("key", "secret")
    symbols = client.get_spot_symbols()
    assert "BTCUSDT" in symbols

@patch("exchanges.bybit_api.HTTP")
def test_get_spot_symbols_api_error(mock_http):
    from exchanges.bybit_api import BybitClient
    # Провокуємо помилку
    mock_http.return_value.get_tickers.side_effect = Exception("fail")
    client = BybitClient("key", "secret")
    symbols = client.get_spot_symbols()
    assert symbols == []

@patch("exchanges.bybit_api.HTTP")
def test_get_price_success(mock_http):
    from exchanges.bybit_api import BybitClient
    mock_http.return_value.get_tickers.return_value = {
        "result": {"list": [{"lastPrice": "23456"}]}
    }
    client = BybitClient("key", "secret")
    price = client.get_price("BTCUSDT")
    assert price == 23456.0

@patch("exchanges.bybit_api.HTTP")
def test_get_price_api_error(mock_http):
    from exchanges.bybit_api import BybitClient
    mock_http.return_value.get_tickers.side_effect = Exception("fail")
    client = BybitClient("key", "secret")
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
    mock_instance.send_message.assert_called_once_with(chat_id=1111, text="Test")

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

# ⚠️ Поки що integration test може не працювати через patch — залиш основні unit тести для стабільності!
# Якщо хочеш тестувати інтеграцію — краще зроби окремий тест і вкажи його явно.
