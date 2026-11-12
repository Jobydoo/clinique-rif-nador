// Service Worker pour PWA Clinique Médico-Chirurgicale du Rif - Nador
const CACHE_NAME = 'clinique-rif-nador-v1';
const STATIC_ASSETS = [
  '/',
  '/static/vendor/tailwindcss.js',
  '/static/vendor/react.js',
  '/static/vendor/react-dom.js',
  '/static/js/i18n.js',
  '/static/js/app.js',
  '/static/css/custom.css',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => console.log('Offline cache warm:', err));
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Ignorer les requêtes d'API dynamiques pour toujours avoir le temps réel si connecté
  if (event.request.url.includes('/api/')) {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).catch(() => {
        // Mode déconnecté
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
      });
    })
  );
});
