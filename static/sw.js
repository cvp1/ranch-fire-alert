// sw.js - Service Worker for Ranch Fire Alert PWA
const CACHE_NAME = 'ranch-fire-alert-v1.0.0';
const urlsToCache = [
    '/',
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache opened');
                return cache.addAll(['/']);
            })
            .catch((error) => {
                console.log('Cache failed:', error);
            })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') {
        return;
    }
    
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }
    
    // Handle API requests - always go to network
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return new Response(
                        JSON.stringify({ 
                            error: 'You are offline. Please check your connection.',
                            offline: true
                        }),
                        {
                            status: 503,
                            headers: { 'Content-Type': 'application/json' }
                        }
                    );
                })
        );
        return;
    }
    
    // Handle other requests - cache first, then network
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version if available
                if (response) {
                    return response;
                }
                
                // Otherwise fetch from network
                return fetch(event.request)
                    .then((response) => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response for caching
                        const responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // If request fails and it's a navigation request, return cached homepage
                        if (event.request.destination === 'document') {
                            return caches.match('/');
                        }
                        
                        // For other requests, return a generic offline response
                        return new Response('Offline content not available', {
                            status: 503,
                            statusText: 'Service Unavailable',
                            headers: new Headers({
                                'Content-Type': 'text/plain'
                            })
                        });
                    });
            })
    );
});

// Handle background sync (when connection is restored)
self.addEventListener('sync', (event) => {
    console.log('Background sync event:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // You can add background sync logic here
            // For example, send queued fire alerts when connection is restored
            console.log('Background sync completed')
        );
    }
});

// Handle push notifications (when Firebase sends notifications)
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body || 'New fire alert notification',
            icon: '/static/icons/icon-192.png',
            badge: '/static/icons/icon-192.png',
            vibrate: [200, 100, 200],
            requireInteraction: true,
            tag: 'fire-alert',
            data: data.data || {},
            actions: [
                {
                    action: 'view',
                    title: 'View Alert',
                    icon: '/static/icons/icon-192.png'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss',
                    icon: '/static/icons/icon-192.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification(
                data.title || '🔥 Ranch Fire Alert',
                options
            )
        );
    }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification click received:', event);
    
    event.notification.close();
    
    if (event.action === 'view') {
        // Open the app when user clicks "View Alert"
        event.waitUntil(
            clients.openWindow('/')
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        return;
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Handle messages from the main app (for badge updates)
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'UPDATE_BADGE') {
        const count = event.data.count || 0;
        
        // Update app badge if supported
        if ('setAppBadge' in navigator) {
            navigator.setAppBadge(count).catch(error => {
                console.log('Failed to set app badge:', error);
            });
        }
        
        // Update notification badge
        if (count > 0) {
            // Set badge on the app icon
            self.registration.update();
        }
    }
});

console.log('Service Worker loaded - Ranch Fire Alert PWA');