import asyncio
import yaml
import time
from datetime import datetime
from bybit_api import BybitClient
from telegram_bot import TelegramNotifier
from logger import log_info
from arbitrage_blocks import get_spot_futures_arbitrage, get_margin_futures_arbitrage

EXCHANGE_NAME = "Bybit"

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

bybit = BybitClient(config['bybit']['api_key'], config['bybit']['api_secret'])
notifier = TelegramNotifier(config['telegram']['bot_token'], config['telegram']['chat_id'])

symbols_cache = {"symbols": [], "last_update": 0}
cache_ttl = 600  # 10 хвилин кешу
prev_top_spot = []
prev_top_margin = []

async def check_arbitrage():
    global prev_top_spot, prev_top_margin

    # Красиве стартове повідомлення
    start_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    start_msg = (
        f"🌐 Біржа: {EXCHANGE_NAME}\n\n"
        f"✅ Бот Bybit Arbitrage успішно ЗАПУЩЕНО!\n\n"
        f"🔍 Пошук арбітражу між спотом, маржею і ф’ючерсами розпочато.\n"
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
            if current_time - symbols_cache["last_update"] > cache_ttl or not symbols_cache["symbols"]:
                symbols_cache["symbols"] = bybit.get_spot_symbols(config['bybit'].get('min_volume', 100000))
                symbols_cache["last_update"] = current_time
                log_info(f"Оновлено кеш символів ({len(symbols_cache['symbols'])})")
            symbols = symbols_cache["symbols"]

            # Отримуємо топ-5 spot-futures та margin-futures через окремі блоки
            top_spot = await get_spot_futures_arbitrage(bybit, symbols, config)
            top_margin = await get_margin_futures_arbitrage(bybit, symbols, config)

            msg = f"🌐 Біржа: {EXCHANGE_NAME}\n\n"
            updated = False

            if top_spot and top_spot != prev_top_spot:
                updated = True
            if top_margin and top_margin != prev_top_margin:
                updated = True

            if updated:
                msg += "🚨 ТОП-5 арбітражів СПОТ - Ф'ЮЧЕРСИ:\n\n"
                if top_spot:
                    for i, res in enumerate(top_spot, 1):
                        emoji = "🚀" if res.get('is_special') else "💹"
                        special = "⚡️ <b>SPECIAL ALERT!</b> ⚡️\n" if res.get('is_special') else ""
                        msg += (
                            f"{emoji} {i}) {res['symbol']}\n"
                            f"   Спот: {res['spot_price']}\n"
                            f"   Ф'ючерси: {res['futures_price']}\n"
                            f"   Різниця: {res['difference']:.2f}%\n"
                            f"{special}"
                            f"   Обсяг 24h: {int(res['volume']):,} USDT\n\n"
                        )
                else:
                    msg += "   Немає монет з арбітражем понад поріг\n\n"

                msg += f"====================\n"
                msg += f"🚨 ТОП-5 арбітражів МАРЖА - Ф'ЮЧЕРСИ:\n\n"
                if top_margin:
                    for i, res in enumerate(top_margin, 1):
                        emoji = "🔥" if res.get('is_special') else "💹"
                        special = "⚡️ <b>SPECIAL ALERT!</b> ⚡️\n" if res.get('is_special') else ""
                        msg += (
                            f"{emoji} {i}) {res['symbol']}\n"
                            f"   Маржа: {res['margin_price']}\n"
                            f"   Ф'ючерси: {res['futures_price']}\n"
                            f"   Різниця: {res['difference']:.2f}%\n"
                            f"{special}"
                            f"   Обсяг 24h: {int(res['volume']):,} USDT\n\n"
                        )
                else:
                    msg += "   Немає монет з арбітражем понад поріг\n\n"

                # Якщо серед топ-арбітражів є SPECIAL, надсилаємо гучну нотифікацію
                loud = any(r.get('is_special') for r in top_spot + top_margin)
                await notifier.send_message(msg, loud=loud)
                log_info(msg)
                prev_top_spot = top_spot.copy()
                prev_top_margin = top_margin.copy()
            else:
                log_info("Топи не змінилися — алерт не надсилаємо")

            await asyncio.sleep(config['bybit']['request_interval'])

    except Exception as e:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        error_msg = (
            f"🌐 Біржа: {EXCHANGE_NAME}\n\n"
            f"⛔️ Бот Bybit Arbitrage ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено через помилку.\n"
            f"⏰ {stop_time}\n\n"
            f"Помилка: {str(e)}"
        )
        await notifier.send_message(error_msg)
        log_info(error_msg)
        raise

    except KeyboardInterrupt:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        stop_msg = (
            f"🌐 Біржа: {EXCHANGE_NAME}\n\n"
            f"⛔️ Бот Bybit Arbitrage ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено вручну.\n"
            f"⏰ {stop_time}\n\n"
            f"Бот коректно зупинено за запитом користувача."
        )
        await notifier.send_message(stop_msg)
        log_info(stop_msg)

    finally:
        stop_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        final_msg = (
            f"🌐 Біржа: {EXCHANGE_NAME}\n\n"
            f"⛔️ Бот Bybit Arbitrage ЗУПИНЕНО!\n\n"
            f"🛑 Моніторинг арбітражу вимкнено.\n"
            f"⏰ {stop_time}\n\n"
            f"Перевір роботу, якщо зупинка була неочікуваною!"
        )
        await notifier.send_message(final_msg)
        log_info(final_msg)

if __name__ == "__main__":
    asyncio.run(check_arbitrage())
