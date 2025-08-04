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
        print("Бот запущено, шукаю арбітраж...")

        symbols = bybit.get_spot_symbols()
        results = []

        for symbol in symbols:
            spot_price = bybit.get_price(symbol, category="spot")
            futures_price = bybit.get_price(symbol, category="linear")

            if spot_price and futures_price:
                difference = abs(futures_price - spot_price) / spot_price * 100
                if difference >= config['bybit']['arbitrage_difference']:
                    results.append({
                        "symbol": symbol,
                        "spot_price": spot_price,
                        "futures_price": futures_price,
                        "difference": difference
                    })
            await asyncio.sleep(0.1)  # мінімізуємо навантаження на API

        # Залишаємо тільки ТОП-5 монет з найбільшим арбітражем
        top_results = sorted(results, key=lambda x: x['difference'], reverse=True)[:5]

        if top_results:
            msg = "🚨 ТОП-5 арбітражних монет на Bybit:\n\n"
            for i, res in enumerate(top_results, start=1):
                msg += (
                    f"{i}) {res['symbol']}\n"
                    f"   Спот: {res['spot_price']}\n"
                    f"   Ф'ючерси: {res['futures_price']}\n"
                    f"   Різниця: {res['difference']:.2f}%\n\n"
                )
            await notifier.send_message(msg)
            log_info(msg)
        else:
            log_info("Немає монет із арбітражем понад поріг")

        await asyncio.sleep(config['bybit']['request_interval'])

if __name__ == "__main__":
    asyncio.run(check_arbitrage())
