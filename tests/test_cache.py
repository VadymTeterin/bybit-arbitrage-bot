import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

def test_disk_cache_write_and_read(tmp_path):
    from cache.disk_cache import DiskCache
    cache_file = tmp_path / "test_cache.pkl"
    cache = DiskCache(str(cache_file))
    # Запис
    cache.set("BTC", 12345)
    # Зчитування
    value = cache.get("BTC")
    assert value == 12345
    # Видалення
    cache.delete("BTC")
    assert cache.get("BTC") is None

def test_cache_manager_add_and_get():
    from cache.cache_manager import CacheManager
    cache = CacheManager()
    cache.set("ETH", 555)
    assert cache.get("ETH") == 555
    cache.delete("ETH")
    assert cache.get("ETH") is None

# Якщо в CacheManager або DiskCache реалізовано TTL — можна додати тест:
import time

def test_cache_ttl(tmp_path):
    from cache.disk_cache import DiskCache
    cache_file = tmp_path / "test_cache_ttl.pkl"
    # TTL = 1 секунда
    cache = DiskCache(str(cache_file), ttl=1)
    cache.set("LTC", 77)
    assert cache.get("LTC") == 77
    time.sleep(2)
    assert cache.get("LTC") is None
