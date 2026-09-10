// Service Worker for China Landscape Atlas
const CACHE_NAME = "landscape-cache-v2";
const STATIC_ASSETS = [
  "./",
  "index.html",
  "data.js",
  "manifest.json",
  "icon-192.png",
  "icon-512.png",
  "og-cover.jpg"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;

  // Network-first for HTML/JS so updates are instantaneous on refresh
  if (req.mode === "navigate" || req.url.endsWith(".html") || req.url.endsWith(".js")) {
    event.respondWith(
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
        return res;
      }).catch(() => caches.match(req))
    );
    return;
  }

  // Cache-first for images & icons
  event.respondWith(
    caches.match(req).then(cached => {
      if (cached) return cached;
      return fetch(req).then(res => {
        if (res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
        }
        return res;
      });
    })
  );
});
