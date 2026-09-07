const C = 'ready-timer-v3';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== C).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});
// Navigations (index.html): network-first so updates land on the next launch;
// fall back to cache offline. Everything else: stale-while-revalidate.
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.mode === 'navigate' || (req.destination === 'document')) {
    e.respondWith((async () => {
      try {
        const n = await fetch(req);
        const c = await caches.open(C);
        try { c.put(req, n.clone()); } catch (_) {}
        return n;
      } catch (_) {
        const c = await caches.open(C);
        return (await c.match(req)) || Response.error();
      }
    })());
    return;
  }
  e.respondWith((async () => {
    const c = await caches.open(C);
    const hit = await c.match(req);
    const net = fetch(req).then(n => {
      if (n && n.ok && req.method === 'GET') {
        try { c.put(req, n.clone()); } catch (_) {}
      }
      return n;
    }).catch(() => hit);
    return hit || net;
  })());
});