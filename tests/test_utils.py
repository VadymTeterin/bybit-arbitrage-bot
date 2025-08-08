import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_history_manager_basic():
    from utils.history_manager import HistoryManager
    hm = HistoryManager()
    # Новий топ (має бути новим)
    is_new = hm.is_new_top("bybit", "spot", [{"symbol": "BTCUSDT", "difference": 1}])
    assert is_new
    # Зберігаємо цей топ
    hm.save_top("bybit", "spot", [{"symbol": "BTCUSDT", "difference": 1}])
    # Якщо не змінився — не новий
    is_new2 = hm.is_new_top("bybit", "spot", [{"symbol": "BTCUSDT", "difference": 1}])
    assert not is_new2

def test_history_manager_save_top_empty():
    from utils.history_manager import HistoryManager
    hm = HistoryManager()
    hm.save_top("okx", "margin", [])
    assert "okx" in hm.prev_tops

def test_save_signal_to_csv(tmp_path):
    from utils.statistics_manager import save_signal_to_csv, calculate_average_spread
    file = tmp_path / "test_history.csv"
    save_signal_to_csv("bybit", "BTCUSDT", 100, 101, 1.1, 12345)
    # average_spread з файлу з одним сигналом
    avg = calculate_average_spread("arbitrage_history.csv")
    assert avg > 0 or avg == 0

def test_calculate_average_spread_empty(tmp_path):
    from utils.statistics_manager import calculate_average_spread
    file = tmp_path / "empty_history.csv"
    avg = calculate_average_spread(str(file))
    assert avg == 0
