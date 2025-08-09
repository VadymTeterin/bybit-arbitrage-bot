import asyncio
import time
import zlib
import websockets
import orjson

class WSClient:
    def __init__(self, url, make_subscribe_msg, on_json, name, ping_interval=20):
        self.url = url
        self.make_subscribe_msg = make_subscribe_msg
        self.on_json = on_json
        self.name = name
        self.ping_interval = ping_interval
        self._stop = False

    async def _inflate(self, raw):
        if isinstance(raw, (bytes, bytearray)):
            try:
                return zlib.decompress(raw, 16 + zlib.MAX_WBITS).decode()
            except Exception:
                return raw.decode(errors="ignore")
        return raw

    async def run(self):
        backoff = 1
        while not self._stop:
            try:
                async with websockets.connect(self.url, max_queue=2048) as ws:
                    await ws.send(self.make_subscribe_msg())

                    async def pinger():
                        while True:
                            await asyncio.sleep(self.ping_interval)
                            try:
                                await ws.ping()
                            except:
                                return
                    asyncio.create_task(pinger())

                    while True:
                        raw = await ws.recv()
                        text = await self._inflate(raw) if isinstance(raw, (bytes, bytearray)) else raw
                        try:
                            data = orjson.loads(text)
                        except:
                            continue
                        await self.on_json(self.name, data)

                backoff = 1
            except Exception as e:
                print(f"[WS] {self.name} error: {e}; reconnect in {backoff}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    def stop(self):
        self._stop = True
