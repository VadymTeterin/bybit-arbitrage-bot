import csv
from datetime import datetime

def save_signal_to_csv(exchange, symbol, spot_price, futures_price, difference, volume):
    with open('arbitrage_history.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now(), exchange, symbol, spot_price, futures_price, difference, volume])

def calculate_average_spread(csv_file='arbitrage_history.csv'):
    try:
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            spreads = [float(row[5]) for row in reader if len(row) > 5]
            return sum(spreads) / len(spreads) if spreads else 0
    except Exception:
        return 0
