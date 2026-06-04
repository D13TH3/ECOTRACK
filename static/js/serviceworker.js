self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open('ecotrack-cache-v1').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/css/ui.css',
        '/static/src/input.css',
        '/static/img/Ecotrack.png',
        '/static/img/Ecotrack.png'
      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});
