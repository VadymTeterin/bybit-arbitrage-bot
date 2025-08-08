import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_format_exchange_report_basic():
    from formatters.message_formatter import format_exchange_report
    spot = [
        {"symbol": "BTCUSDT", "spot_price": 100, "futures_price": 101, "difference": 1.1, "volume": 12345},
    ]
    margin = [
        {"symbol": "ETHUSDT", "margin_price": 98, "futures_price": 100, "difference": 2.0, "volume": 54321}
    ]
    msg = format_exchange_report("bybit", spot, margin)
    assert "BTCUSDT" in msg and "ETHUSDT" in msg

def test_format_exchange_report_empty():
    from formatters.message_formatter import format_exchange_report
    msg = format_exchange_report("binance", [], [])
    assert "Немає монет з арбітражем понад поріг" in msg

def test_format_as_html():
    from formatters.html_formatter import format_as_html
    spot = [
        {"symbol": "BTCUSDT", "spot_price": 100, "futures_price": 101, "difference": 1.1, "volume": 12345},
    ]
    margin = [
        {"symbol": "ETHUSDT", "margin_price": 98, "futures_price": 100, "difference": 2.0, "volume": 54321}
    ]
    html = format_as_html("bybit", spot, margin)
    assert "<b>Біржа:" in html and "BTCUSDT" in html and "ETHUSDT" in html
