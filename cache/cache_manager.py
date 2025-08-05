# cache/cache_manager.py (для v3.0m_05-08-25)
import time
from logger import log_info

class CacheManager:
    def __init__(self, cache_ttl=600):
        self.cache = {}
        self.cache_ttl = cache_ttl

    def get_symbols(self, exch_name, client, min_volume):
        now = time.time()
        if exch_name not in self.cache:
            self.cache[exch_name] = {"symbols": [], "last_update": 0}
        cache = self.cache[exch_name]

        if now - cache["last_update"] > self.cache_ttl or not cache["symbols"]:
            cache["symbols"] = client.get_spot_symbols(min_volume)
            cache["last_update"] = now
            log_info(f"{exch_name.capitalize()}: Оновлено кеш символів ({len(cache['symbols'])})")
        return cache["symbols"]
