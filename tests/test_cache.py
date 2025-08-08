import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_save_and_load_cache_disk(tmp_path):
    from cache.disk_cache import save_cache_to_disk, load_cache_from_disk
    test_file = tmp_path / "test_cache.json"
    test_dict = {"BTC": [1,2,3]}
    save_cache_to_disk(test_dict, str(test_file))
    loaded = load_cache_from_disk(str(test_file))
    assert loaded == test_dict

def test_load_cache_file_not_found(tmp_path):
    from cache.disk_cache import load_cache_from_disk
    fake_file = tmp_path / "no_file.json"
    data = load_cache_from_disk(str(fake_file))
    assert data == {}

def test_cache_manager_get_symbols(monkeypatch):
    from cache.cache_manager import CacheManager
    # Мокаємо клієнта з get_spot_symbols
    class DummyClient:
        def get_spot_symbols(self, min_volume):
            return ["BTCUSDT", "ETHUSDT"]
    cache = CacheManager(cache_ttl=0)
    result = cache.get_symbols("bybit", DummyClient(), min_volume=0)
    assert "BTCUSDT" in result
    # Перевірка кешу
    result2 = cache.get_symbols("bybit", DummyClient(), min_volume=0)
    assert result2 == result
