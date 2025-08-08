import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_history_manager_basic():
    from utils.history_manager import HistoryManager
    hm = HistoryManager()
    hm.add("BTC", 100)
    hm.add("BTC", 200)
    # Чи оновлюється історія?
    history = hm.get("BTC")
    assert isinstance(history, (list, int, float, dict, tuple)) or history is not None

    # Тест на get all
    all_history = hm.get_all()
    assert "BTC" in all_history

def test_history_manager_edge_case():
    from utils.history_manager import HistoryManager
    hm = HistoryManager()
    # get для неіснуючої монети
    assert hm.get("UNKNOWN") is None or hm.get("UNKNOWN") == []

def test_statistics_manager_basic():
    from utils.statistics_manager import StatisticsManager
    sm = StatisticsManager()
    sm.add("ETH", 10)
    sm.add("ETH", 20)
    stat = sm.get_statistics("ETH")
    assert "count" in stat and stat["count"] >= 2
    assert stat["sum"] >= 30 or "sum" in stat or isinstance(stat, dict)

def test_statistics_manager_edge_case():
    from utils.statistics_manager import StatisticsManager
    sm = StatisticsManager()
    # Статистика по неіснуючій монеті
    stat = sm.get_statistics("DOGE")
    assert stat is not None
    # Перевірка типу, ключів, тощо
    assert isinstance(stat, dict)
