# Алгоритми для пошуку арбітражу SPOT-Ф'ЮЧЕРСИ та МАРЖА-Ф'ЮЧЕРСИ на OKX
import asyncio

async def get_spot_futures_arbitrage(okx, symbols, config):
    """
    Повертає топ-5 монет з найбільшим арбітражем між спотом та ф'ючерсами на OKX.
    """
    results = []
    for symbol_data in symbols:
        symbol = symbol_data["symbol"]
        spot_price = okx.get_price(symbol, category="spot")
        futures_price = okx.get_price(symbol, category="linear")
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

async def get_margin_futures_arbitrage(okx, symbols, config):
    """
    Повертає топ-5 монет з найбільшим арбітражем між маржею та ф'ючерсами на OKX.
    """
    results = []
    for symbol_data in symbols:
        symbol = symbol_data["symbol"]
        margin_price = okx.get_price(symbol, category="margin")
        futures_price = okx.get_price(symbol, category="linear")
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
