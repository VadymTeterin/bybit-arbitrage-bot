def format_as_html(exchange_name, top_spot, top_margin):
    html = f"<b>Біржа: {exchange_name}</b><br>"
    html += "<b>ТОП-5 арбітражів СПОТ-Ф'ЮЧЕРСИ:</b><br><table border='1'><tr><th>#</th><th>Монета</th><th>Спот</th><th>Ф’ючерс</th><th>Різниця</th></tr>"
    for i, res in enumerate(top_spot, 1):
        html += f"<tr><td>{i}</td><td>{res['symbol']}</td><td>{res['spot_price']}</td><td>{res['futures_price']}</td><td>{res['difference']:.2f}%</td></tr>"
    html += "</table><br>"

    html += "<b>ТОП-5 арбітражів МАРЖА-Ф'ЮЧЕРСИ:</b><br><table border='1'><tr><th>#</th><th>Монета</th><th>Маржа</th><th>Ф’ючерс</th><th>Різниця</th></tr>"
    for i, res in enumerate(top_margin, 1):
        html += f"<tr><td>{i}</td><td>{res['symbol']}</td><td>{res.get('margin_price', '-')}</td><td>{res['futures_price']}</td><td>{res['difference']:.2f}%</td></tr>"
    html += "</table><br>"
    return html
