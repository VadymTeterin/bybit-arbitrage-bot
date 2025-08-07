# Алгоритми для пошуку арбітражу SPOT-Ф'ЮЧЕРСИ та МАРЖА-Ф'ЮЧЕРСИ на Binance (v3.0m_05-08-25)
import asyncio

async def get_spot_futures_arbitrage(binance, symbols, config):
    results = []
    futures_symbols = binance.get_futures_symbols()
    for symbol_data in symbols:
        symbol = symbol_data["symbol"]
        if symbol not in futures_symbols:
            continue
        spot_price = binance.get_price(symbol, category="spot")
        futures_price = binance.get_price(symbol, category="linear")
        if spot_price and futures_price:
            difference = (futures_price - spot_price) / spot_price * 100
            is_special = difference >= 2
            if difference >= config['arbitrage_difference']:
                results.append({
                    "symbol": symbol,
                    "spot_price": spot_price,
                    "futures_price": futures_price,
                    "difference": difference,
                    "volume": symbol_data["volume"],
                    "is_special": is_special
                })
        await asyncio.sleep(0.1)
    return sorted(results, key=lambda x: x['difference'], reverse=True)[:5]

async def get_margin_futures_arbitrage(binance, symbols, config):
    results = []
    futures_symbols = binance.get_futures_symbols()
    for symbol_data in symbols:
        symbol = symbol_data["symbol"]
        if symbol not in futures_symbols:
            continue
        margin_price = binance.get_price(symbol, category="margin")
        futures_price = binance.get_price(symbol, category="linear")
        if margin_price and futures_price:
            difference = (futures_price - margin_price) / margin_price * 100
            is_special = difference >= 2
            if difference >= config['arbitrage_difference']:
                results.append({
                    "symbol": symbol,
                    "margin_price": margin_price,
                    "futures_price": futures_price,
                    "difference": difference,
                    "volume": symbol_data["volume"],
                    "is_special": is_special
                })
        await asyncio.sleep(0.1)
    return sorted(results, key=lambda x: x['difference'], reverse=True)[:5]