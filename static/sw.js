// AGRI-VISE Service Worker for Android PWA Installation
const CACHE_NAME = 'agrivise-pwa-v1';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
    // Pass live sensor and stream requests directly to network without caching
    if (event.request.url.includes('/video_feed') || 
        event.request.url.includes('/sensor_data') || 
        event.request.url.includes('/forward') || 
        event.request.url.includes('/backward') || 
        event.request.url.includes('/left') || 
        event.request.url.includes('/right') || 
        event.request.url.includes('/stop') || 
        event.request.url.includes('/scan')) {
        return;
    }
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});

