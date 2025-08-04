import asyncio
import yaml
import time
from datetime import datetime
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
    global prev_top

    # Красиве стартове повідомлення
    start_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    start_msg = (
        f"✅ Бот Bybit Arbitrage успішно ЗАПУЩЕНО!\n\n"
        f"🔍 Пошук арбітражу між спотом і ф’ючерсами розпочато.\n"
        f"⏰ {start_time}\n\n"
        f"Мінімальний обсяг торгів (24h): {config['bybit'].get('min_volume', 100000)} USDT\n"
        f"Бажаю прибуткових сигналів! 🚀"
    )
    await notifier.send_message(start_msg)
    log_info("Бот запущено")

    try:
        while True:
            print("Бот запущено, шукаю арбітраж...")

            current_time = time.time()
            # --- Отримуємо монети з обсягом > min_volume ---
            if current_time - symbols_cache["last_update"] > cache_ttl or not symbols_cache["symbols"]:
                symbols_cache["symbols"] = bybit.get_spot_symbols(config['bybit'].get('min_volume', 100000))
                symbols_cache["last_update"] = current_time
                log_info(f"Оновлено кеш символів ({len(symbols_cache['symbols'])})")
            symbols = symbols_cache["symbols"]

            results = []

            for symbol_data in symbols:
                symbol = symbol_data["symbol"]
                # volume = symbol_data["volume"]  # якщо захочеш додати у повідомлення
                spot_price = bybit.get_price(symbol, category="spot")
                futures_price = bybit.get_price(symbol, category="linear")

                if spot_price and futures_price:
                    difference = abs(futures_price - spot_price) / spot_price * 100
                    if difference >= config['bybit']['arbitrage_difference']:
                        results.append({
                            "symbol": symbol,
                            "spot_price": spot_price,
                            "futures_price": futures_price,
                            "difference": difference,
                            "volume": symbol_data["volume"]
                        })
                await asyncio.sleep(0.1)

            top_results = sorted(results, key=lambda x: x['difference'], reverse=True)[:5]

            if top_results and top_results != prev_top:
                msg = "🚨 ТОП-5 арбітражних монет на Bybit:\n\n"
                for i, res in enumerate(top_results, start=1):
                    msg += (
                        f"{i}) {res['symbol']}\n"
                        f"   Спот: {res['spot_price']}\n"
                        f"   Ф'ючерси: {res['futures_price']}\n"
                        f"   Різниця: {res['difference']:.2f}%\n"
                        f"   Обсяг 24h: {int(res['volume']):,} USDT\n\n"
                    )
                await notifier.send_message(msg)
                log_info(msg)
                prev_top = top_results.copy()
            elif not top_results:
                log_info("Немає монет із арбітражем понад поріг")
                prev_top = []
            else:
                log_info("Топ-5 не змінився — алерт не надсилаємо")

            await asyncio.sleep(config['bybit']['request_interval'])

    except Exception as e:
        # Аварійна зупинка з інформативним повідомленням
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        error_msg = (
            f"⛔️ Бот Bybit Arbitrage ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено через помилку.\n"
            f"⏰ {stop_time}\n\n"
            f"Помилка: {str(e)}"
        )
        await notifier.send_message(error_msg)
        log_info(error_msg)
        raise

    except KeyboardInterrupt:
        # Ручна зупинка
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        stop_msg = (
            f"⛔️ Бот Bybit Arbitrage ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено вручну.\n"
            f"⏰ {stop_time}\n\n"
            f"Бот коректно зупинено за запитом користувача."
        )
        await notifier.send_message(stop_msg)
        log_info(stop_msg)

    finally:
        # Повідомлення про зупинку у будь-якому разі (як резерв)
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        final_msg = (
            f"⛔️ Бот Bybit Arbitrage ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено.\n"
            f"⏰ {stop_time}\n\n"
            f"Перевір роботу, якщо зупинка була неочікуваною!"
        )
        await notifier.send_message(final_msg)
        log_info(final_msg)

if __name__ == "__main__":
    asyncio.run(check_arbitrage())

