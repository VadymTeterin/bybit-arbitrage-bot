# utils/history_manager.py (для v3.0m_05-08-25)
class HistoryManager:
    def __init__(self):
        # Структура: {exch_name: {'spot': [...], 'margin': [...]}}
        self.prev_tops = {}

    def is_new_top(self, exch_name, market_type, top):
        if exch_name not in self.prev_tops:
            self.prev_tops[exch_name] = {"spot": [], "margin": []}
        prev = self.prev_tops[exch_name][market_type]
        # Списки топів можуть містити dict-и: перевіряємо по symbol/difference
        if top and top != prev:
            return True
        return False

    def save_top(self, exch_name, market_type, top):
        self.prev_tops[exch_name][market_type] = top.copy() if top else []
