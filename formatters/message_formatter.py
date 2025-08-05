# formatters/message_formatter.py (для v3.0m_05-08-25)
def format_exchange_report(exch_name, top_spot, top_margin):
    msg = f"🌐 Біржа: {exch_name.capitalize()}\n\n"
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
    return msg
