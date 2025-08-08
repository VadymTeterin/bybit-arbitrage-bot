# exchange_manager.py
from exchanges.bybit_api import BybitClient
from exchanges.binance_api import BinanceClient
from exchanges.okx_api import OKXClient
from exchanges.kucoin_api import KucoinClient
from exchanges.gateio_api import GateioClient
from exchanges.bingx_api import BingxClient
from exchanges.mexc_api import MexcClient
from exchanges.htx_api import HtxClient

CLIENTS = {
    'bybit': BybitClient,
    'binance': BinanceClient,
    'okx': OKXClient,
    'kucoin': KucoinClient,
    'gateio': GateioClient,
    'bingx': BingxClient,
    'mexc': MexcClient,
    'htx': HtxClient,
}

class ExchangeManager:
    def __init__(self, config):
        self.config = config
        self.exchanges = {}
        self._init_exchanges()

    def _init_exchanges(self):
        for exch_name, exch_cfg in self.config.get('exchanges', {}).items():
            if (
                exch_cfg.get('enabled', False)
                and exch_cfg.get('api_key')
                and exch_cfg.get('api_secret')
                and exch_name in CLIENTS
            ):
                self.exchanges[exch_name] = CLIENTS[exch_name](
                    exch_cfg['api_key'], exch_cfg['api_secret']
                )

    def get_active_exchanges(self):
        return self.exchanges

    def get_exchange(self, name):
        return self.exchanges.get(name)

    def get_config(self, name):
        return self.config['exchanges'].get(name, {})

    def reload(self):
        self.exchanges = {}
        self._init_exchanges()
