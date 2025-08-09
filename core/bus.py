import asyncio
from dataclasses import dataclass

@dataclass(slots=True)
class Tick:
    exch: str
    symbol: str
    bid: float
    ask: float
    ts: float

class EventBus:
    def __init__(self, maxsize=100_000):
        self.q = asyncio.Queue(maxsize=maxsize)

    async def publish(self, x):
        await self.q.put(x)

    async def subscribe(self):
        return self.q
