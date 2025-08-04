import asyncio
import yaml
import time
from bybit_api import BybitClient
from telegram_bot import TelegramNotifier
from logger import log_info

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

bybit = BybitClient(config['bybit']['api_key'], config['bybit']['api_secret'])
notifier = TelegramNotifier(config['telegram']['bot_token'], config['telegram']['chat_id'])

symbols_cache = {"symbols": [], "last_update": 0}
cache_ttl = 600  # 10 хвилин кешу
prev_top = []

async def check_arbitrage():
    while True:
        print("Бот запущено, шукаю арбітраж...")

        # --- Кешування списку монет ---
        current_time = time.time()
        if current_time - symbols_cache["last_update"] > cache_ttl or not symbols_cache["symbols"]:
            symbols_cache["symbols"] = bybit.get_spot_symbols()
            symbols_cache["last_update"] = current_time
            log_info(f"Оновлено кеш символів ({len(symbols_cache['symbols'])})")
        symbols = symbols_cache["symbols"]

        results = []

        for symbol in symbols:
            spot_price = bybit.get_price(symbol, category="spot")
            futures_price = bybit.get_price(symbol, category="linear")

            if spot_price and futures_price:
                difference = abs(futures_price - spot_price)
