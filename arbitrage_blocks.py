# arbitrage_blocks.py
import asyncio

async def get_spot_futures_arbitrage(bybit, symbols, config):
    results = []
    for symbol_data in symbols:
        symbol = symbol_data["symbol"]
        spot_price = bybit.get_price(symbol, category="spot")
        futures_price = bybit.get_price(symbol, category="linear")
        if spot_price and futures_price:
            # ТІЛЬКИ якщо ф'ючерс дорожчий за спот!
            difference = (futures_price - spot_price) / spot_price * 100
            if difference >= config['bybit']['arbitrage_difference']:
                results.append({
                    "symbol": symbol,
                    "spot_price": spot_price,
                    "futures_price": futures_price,
                    "difference": difference,
                    "volume": symbol_data["volume"]
                })
        await asyncio.sleep(0.1)
    return sorted(results, key=lambda x: x['difference'], reverse=True)[:5]

async def get_margin_futures_arbitrage(bybit, symbols, config):
    results = []
    for symbol_data in symbols:
        symbol = symbol_data["symbol"]
        margin_price = bybit.get_price(symbol, category="margin")
        futures_price = bybit.get_price(symbol, category="linear")
        if margin_price and futures_price:
            # ТІЛЬКИ якщо ф'ючерс дорожчий за маржу!
            difference = (futures_price - margin_price) / margin_price * 100
            if difference >= config['bybit']['arbitrage_difference']:
                results.append({
                    "symbol": symbol,
                    "margin_price": margin_price,
                    "futures_price": futures_price,
                    "difference": difference,
                    "volume": symbol_data["volume"]
                })
        await asyncio.sleep(0.1)
    return sorted(results, key=lambda x: x['difference'], reverse=True)[:5]
