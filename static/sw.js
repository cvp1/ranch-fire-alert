// sw.js - iPhone-compatible Service Worker
const CACHE_NAME = 'fire-alert-v1.1.0';
const urlsToCache = [
    '/',
    '/manifest.json'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache opened');
                // Only cache essential resources that definitely exist
                return cache.addAll(['/'])
                    .catch((error) => {
                        console.log('Cache failed for some resources:', error);
                        // Don't fail the entire install if some resources can't be cached
                        return Promise.resolve();
                    });
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
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }
    
    // API requests should go to network first
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Update connection status in clients
                    self.clients.matchAll().then((clients) => {
                        clients.forEach((client) => {
                            client.postMessage({
                                type: 'NETWORK_STATUS',
                                online: true
                            });
                        });
                    });
                    return response;
                })
                .catch((error) => {
                    console.log('API request failed, user is offline');
                    // Notify clients about offline status
                    self.clients.matchAll().then((clients) => {
                        clients.forEach((client) => {
                            client.postMessage({
                                type: 'NETWORK_STATUS',
                                online: false
                            });
                        });
                    });
                    
                    // Return a basic offline response for API calls
                    return new Response(
                        JSON.stringify({ 
                            error: 'You are offline. Please check your connection.' 
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
    
    // For other resources, try cache first, then network
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
                        
                        // Clone response for caching
                        const responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                try {
                                    cache.put(event.request, responseToCache);
                                } catch (error) {
                                    console.log('Failed to cache response:', error);
                                }
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (event.request.destination === 'document') {
                            return caches.match('/');
                        }
                        
                        // For other requests, return a generic offline response
                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Push notification handling (iOS 16.4+ support)
self.addEventListener('push', (event) => {
    console.log('Push message received:', event);
    
    let notificationData = {
        title: 'Fire Alert',
        body: 'Emergency notification received',
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        vibrate: [200, 100, 200],
        requireInteraction: true,
        actions: [
            {
                action: 'open',
                title: 'Open App'
            },
            {
                action: 'dismiss',
                title: 'Dismiss'
            }
        ]
    };
    
    if (event.data) {
        try {
            const payload = event.data.json();
            console.log('Push payload:', payload);
            
            if (payload.notification) {
                notificationData.title = payload.notification.title;
                notificationData.body = payload.notification.body;
            }
            
            if (payload.data) {
                notificationData.data = payload.data;
                
                // Customize notification based on type
                if (payload.data.type === 'fire_alert') {
                    const severity = payload.data.severity || 'medium';
                    notificationData.tag = 'fire-alert';
                    notificationData.renotify = true;
                    
                    // Different urgency based on severity
                    if (severity === 'critical') {
                        notificationData.vibrate = [300, 100, 300, 100, 300];
                        notificationData.silent = false;
                    } else if (severity === 'high') {
                        notificationData.vibrate = [200, 100, 200];
                    }
                    
                } else if (payload.data.type === 'livestock_request') {
                    notificationData.tag = 'livestock-help';
                    notificationData.actions = [
                        {
                            action: 'open',
                            title: 'View Request'
                        },
                        {
                            action: 'dismiss',
                            title: 'Dismiss'
                        }
                    ];
                }
            }
        } catch (error) {
            console.error('Error parsing push payload:', error);
        }
    }
    
    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'dismiss') {
        return;
    }
    
    // Open the app
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            // If app is already open, focus it
            for (const client of clientList) {
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            
            // Otherwise open new window
            if (clients.openWindow) {
                let url = '/';
                
                // Navigate to specific tab based on notification type
                if (event.notification.data) {
                    if (event.notification.data.type === 'livestock_request') {
                        url = '/?tab=livestock';
                    } else if (event.notification.data.type === 'fire_alert') {
                        url = '/?tab=alerts';
                    }
                }
                
                return clients.openWindow(url);
            }
        })
    );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            syncPendingActions()
        );
    }
});

// Sync pending actions when coming back online
async function syncPendingActions() {
    try {
        console.log('Syncing pending actions...');
        
        // Notify all clients that sync is complete
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'SYNC_COMPLETE'
            });
        });
        
    } catch (error) {
        console.error('Error during background sync:', error);
    }
}

// Listen for messages from main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Handle errors gracefully
self.addEventListener('error', (event) => {
    console.error('Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
    console.error('Service Worker unhandled rejection:', event.reason);
});

console.log('Service Worker loaded - iPhone compatible version');