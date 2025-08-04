import asyncio
import yaml
from bybit_api import BybitClient
from telegram_bot import TelegramNotifier
from logger import log_info

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

bybit = BybitClient(config['bybit']['api_key'], config['bybit']['api_secret'])
notifier = TelegramNotifier(config['telegram']['bot_token'], config['telegram']['chat_id'])

async def check_arbitrage():
    while True:
        symbols = bybit.get_spot_symbols()
        for symbol in symbols:
            spot_price = bybit.get_price(symbol, category="spot")
            futures_price = bybit.get_price(symbol, category="linear")

            if spot_price and futures_price:
                difference = abs(futures_price - spot_price) / spot_price * 100
                if difference >= config['bybit']['arbitrage_difference']:
                    msg = (
                        f"🚨 Арбітраж {symbol}!\n"
                        f"Спот: {spot_price}\n"
                        f"Ф'ючерси: {futures_price}\n"
                        f"Різниця: {difference:.2f}%"
                    )
                    await notifier.send_message(msg)
                    log_info(msg)
        await asyncio.sleep(config['bybit']['request_interval'])

if __name__ == "__main__":
    asyncio.run(check_arbitrage())

