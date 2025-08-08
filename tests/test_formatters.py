import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_message_formatter_basic():
    from formatters.message_formatter import format_message
    msg = format_message("BTC", 100, 101)
    assert "BTC" in msg
    assert "100" in msg or "101" in msg

def test_html_formatter():
    from formatters.html_formatter import format_html
    html = format_html("ETH", 123, 124)
    assert "ETH" in html
    assert "<" in html and ">" in html  # бо форматування HTML

# Edge-case: великі числа, невалідні символи
def test_message_formatter_edge_cases():
    from formatters.message_formatter import format_message
    msg = format_message("DOGE$", 0, -1e9)
    assert "DOGE" in msg
    assert "0" in msg
    assert "-" in msg
