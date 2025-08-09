from collections import defaultdict
import time

class ArbitrageEngine:
    def __init__(self, fee_bp=8.0, min_edge_bp=12.0, ttl=1.5):
        self.last = defaultdict(dict)
        self.fee_bp = float(fee_bp)
        self.min_edge_bp = float(min_edge_bp)
        self.ttl = float(ttl)

    def on_tick(self, t):
        self.last[t.exch][t.symbol] = (t.bid, t.ask, t.ts)

    def _best_quotes(self, symbol):
        now = time.time()
        best_bid = (-1.0, None)
        best_ask = (10**18, None)
        for exch, book in self.last.items():
            row = book.get(symbol)
            if not row:
                continue
            bid, ask, ts = row
            if now - ts > self.ttl:
                continue
            if bid > best_bid[0]:
                best_bid = (bid, exch)
            if ask < best_ask[0]:
                best_ask = (ask, exch)
        if best_bid[1] and best_ask[1]:
            return best_bid + best_ask
        return None

    def calc_edge(self, symbol):
        r = self._best_quotes(symbol)
        if not r:
            return None
        bid, bid_ex, ask, ask_ex = r
        raw_bp = (bid - ask) / ask * 10_000.0
        net_bp = raw_bp - self.fee_bp
        return {
            "symbol": symbol,
            "buy_ex": ask_ex,
            "sell_ex": bid_ex,
            "buy": ask,
            "sell": bid,
            "raw_bp": raw_bp,
            "net_bp": net_bp,
        }
