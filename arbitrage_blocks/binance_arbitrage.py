# arbitrage_blocks/binance_arbitrage.py
# Production-блок із intersection для spot-futures/margin-futures на Binance

import asyncio

async def get_spot_futures_arbitrage(binance, symbols, config):
    results = []
    spot_symbols_set = set([s["symbol"] for s in symbols])
    futures_symbols_set = set(binance.get_futures_symbols())
    # Intersection тільки тих символів, які є і на споті, і на ф’ючерсах
    common_symbols = spot_symbols_set & futures_symbols_set
    filtered_symbols = [s for s in symbols if s["symbol"] in common_symbols]

    for symbol_data in filtered_symbols:
        symbol = symbol_data["symbol"]
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
    spot_symbols_set = set([s["symbol"] for s in symbols])
    futures_symbols_set = set(binance.get_futures_symbols())
    common_symbols = spot_symbols_set & futures_symbols_set
    filtered_symbols = [s for s in symbols if s["symbol"] in common_symbols]

    for symbol_data in filtered_symbols:
        symbol = symbol_data["symbol"]
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
