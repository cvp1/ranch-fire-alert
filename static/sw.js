// sw.js - Service Worker for PWA and push notifications
const CACHE_NAME = 'fire-alert-v1.0.0';
const urlsToCache = [
    '/',
    '/manifest.json'
    // Remove the CSS and JS references since they're inline
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache opened');
                return cache.addAll(urlsToCache.filter(url => url !== '/'));
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
    // Only handle GET requests
    if (event.request.method !== 'GET') {
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
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (event.request.destination === 'document') {
                            return caches.match('/');
                        }
                    });
            })
    );
});

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Push message received:', event);
    
    let notificationData = {
        title: 'Fire Alert',
        body: 'Emergency notification received',
        icon: '/icon-192.png',
        badge: '/badge-72.png',
        vibrate: [200, 100, 200],
        requireInteraction: true,
        actions: [
            {
                action: 'open',
                title: 'Open App',
                icon: '/icon-192.png'
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
                            title: 'View Request',
                            icon: '/icon-192.png'
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
        clients.matchAll({ type: 'window' }).then((clientList) => {
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
            // Attempt to sync any pending actions when connection is restored
            syncPendingActions()
        );
    }
});

// Sync pending actions when coming back online
async function syncPendingActions() {
    try {
        // Check if there are any pending actions stored in IndexedDB
        // This would be where you'd sync any offline actions like:
        // - Livestock requests made while offline
        // - Alert acknowledgments
        // - User updates
        
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

// Periodic background sync for critical updates
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'check-fire-alerts') {
        event.waitUntil(
            // Check for new fire alerts periodically
            checkForCriticalAlerts()
        );
    }
});

async function checkForCriticalAlerts() {
    try {
        // This would check for new critical alerts
        // and show notifications if needed
        console.log('Checking for critical fire alerts...');
    } catch (error) {
        console.error('Error checking for critical alerts:', error);
    }
}