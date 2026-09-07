"""Minimal CDP driver for QA of the Ready Timer app (Chrome at 127.0.0.1:9222)."""
import asyncio, base64, json, urllib.request

DEBUG_HOST = 'http://127.0.0.1:9222'
APP_URL = 'http://127.0.0.1:8123/'

def _targets():
    with urllib.request.urlopen(DEBUG_HOST + '/json', timeout=5) as r:
        return json.load(r)

def new_target(url):
    req = urllib.request.Request(DEBUG_HOST + '/json/new?' + urllib.parse.urlencode({'url': url}), method='PUT')
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.load(r)

class CDP:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.events = []
        self._mid = 0

    async def __aenter__(self):
        import websockets
        self.ws = await websockets.connect(self.ws_url, max_size=50*1024*1024)
        await self._send('Runtime.enable')
        await self._send('Page.enable')
        return self

    async def __aexit__(self, *a):
        await self.ws.close()

    async def _send(self, method, params=None):
        self._mid += 1
        mid = self._mid
        await self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=30)
            msg = json.loads(raw)
            if msg.get('id') == mid:
                if 'error' in msg:
                    raise RuntimeError(method + ': ' + json.dumps(msg['error']))
                return msg.get('result', {})
            if 'method' in msg:
                self.events.append(msg)

    async def eval_js(self, expr):
        r = await self._send('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': True})
        res = r.get('result', {})
        if res.get('subtype') == 'error':
            return {'__error__': res.get('description', 'js error')}
        return res.get('value')

    async def screenshot(self, path):
        r = await self._send('Page.captureScreenshot', {'format': 'png'})
        with open(path, 'wb') as f:
            f.write(base64.b64decode(r['data']))
        return path

    async def wait(self, s):
        await asyncio.sleep(s)

def open_app():
    """Open a fresh app tab; returns (ws_url, target_id)."""
    t = new_target(APP_URL)
    return t['webSocketDebuggerUrl'], t['id']

def run(coro_fn):
    return asyncio.run(coro_fn())