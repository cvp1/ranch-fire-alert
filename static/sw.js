// sw.js - Service Worker for Ranch Fire Alert PWA
const CACHE_VERSION = '1.0.1';
const CACHE_NAME = `ranch-fire-alert-v${CACHE_VERSION}`;
const STATIC_CACHE = `ranch-fire-alert-static-v${CACHE_VERSION}`;
const DYNAMIC_CACHE = `ranch-fire-alert-dynamic-v${CACHE_VERSION}`;

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/images/dmr-ranch-backfground.jpg'
];

// Assets to cache on demand
const DYNAMIC_ASSETS = [
    '/api/alerts',
    '/api/config'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
    console.log(`Service Worker installing... Version ${CACHE_VERSION}`);
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE)
                .then((cache) => {
                    console.log('Static cache opened');
                    return cache.addAll(STATIC_ASSETS);
                })
                .catch((error) => {
                    console.error('Static cache failed:', error);
                }),
            
            // Pre-cache dynamic assets
            caches.open(DYNAMIC_CACHE)
                .then((cache) => {
                    console.log('Dynamic cache opened');
                    return cache.addAll(DYNAMIC_ASSETS);
                })
                .catch((error) => {
                    console.error('Dynamic cache failed:', error);
                })
        ])
    );
    
    // Force the waiting service worker to become the active service worker
    self.skipWaiting();
});

// Activate event - clean up old caches and claim clients
self.addEventListener('activate', (event) => {
    console.log(`Service Worker activating... Version ${CACHE_VERSION}`);
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (!cacheName.includes(CACHE_VERSION)) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // Claim all clients immediately
            self.clients.claim()
        ])
    );
});

// Fetch event - optimized caching strategy
self.addEventListener('fetch', (event) => {
    const { request } = event;
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip cross-origin requests
    if (!request.url.startsWith(self.location.origin)) {
        return;
    }
    
    const url = new URL(request.url);
    
    // Handle API requests with network-first strategy
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }
    
    // Handle static assets with cache-first strategy
    if (isStaticAsset(url.pathname)) {
        event.respondWith(handleStaticRequest(request));
        return;
    }
    
    // Handle navigation requests with stale-while-revalidate strategy
    if (request.destination === 'document') {
        event.respondWith(handleNavigationRequest(request));
        return;
    }
    
    // Default: network-first strategy
    event.respondWith(handleDefaultRequest(request));
});

// API request handler - network first, cache fallback
async function handleApiRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('API request failed, trying cache:', error);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response
        return new Response(
            JSON.stringify({ 
                error: 'You are offline. Please check your connection.',
                offline: true,
                timestamp: new Date().toISOString()
            }),
            {
                status: 503,
                headers: { 
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            }
        );
    }
}

// Static asset handler - cache first, network fallback
async function handleStaticRequest(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Static asset fetch failed:', error);
        return new Response('Asset not available offline', {
            status: 404,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Navigation request handler - stale-while-revalidate
async function handleNavigationRequest(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    // Start network request in background
    const networkPromise = fetch(request).then((response) => {
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(() => cachedResponse);
    
    // Return cached response immediately if available
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // Otherwise wait for network
    return networkPromise;
}

// Default request handler - network first
async function handleDefaultRequest(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return new Response('Content not available offline', {
            status: 503,
            headers: { 'Content-Type': 'text/plain' }
        });
    }
}

// Check if URL is a static asset
function isStaticAsset(pathname) {
    return pathname.includes('/static/') || 
           pathname.includes('/icons/') || 
           pathname.includes('/images/') ||
           pathname.endsWith('.css') ||
           pathname.endsWith('.js') ||
           pathname.endsWith('.png') ||
           pathname.endsWith('.jpg') ||
           pathname.endsWith('.jpeg') ||
           pathname.endsWith('.gif') ||
           pathname.endsWith('.svg');
}

// Handle background sync (when connection is restored)
self.addEventListener('sync', (event) => {
    console.log('Background sync event:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Sync any pending data when connection is restored
            syncPendingData()
        );
    }
});

// Sync pending data when connection is restored
async function syncPendingData() {
    try {
        // Get any pending alerts or data from IndexedDB
        const pendingData = await getPendingData();
        
        if (pendingData.length > 0) {
            console.log('Syncing pending data:', pendingData.length, 'items');
            
            // Send pending data to server
            for (const data of pendingData) {
                try {
                    await fetch(data.url, {
                        method: data.method,
                        headers: data.headers,
                        body: data.body
                    });
                    
                    // Remove from pending data
                    await removePendingData(data.id);
                } catch (error) {
                    console.error('Failed to sync item:', error);
                }
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

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
            ],
            // Add timestamp for better UX
            timestamp: Date.now()
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

// Handle messages from the main app
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    try {
        const { type, data } = event.data || {};
        
        switch (type) {
            case 'UPDATE_BADGE':
                // Handle both old format {type: 'UPDATE_BADGE', count: 2} 
                // and new format {type: 'UPDATE_BADGE', data: {count: 2}}
                const count = data?.count || event.data.count || 0;
                console.log('Updating app badge with count:', count);
                updateAppBadge(count);
                break;
                
            case 'SKIP_WAITING':
                console.log('Skipping waiting service worker');
                self.skipWaiting();
                break;
                
            case 'CACHE_DATA':
                console.log('Caching data:', data);
                cacheData(data);
                break;
                
            case 'GET_VERSION':
                console.log('Sending version:', CACHE_VERSION);
                if (event.ports && event.ports[0]) {
                    event.ports[0].postMessage({ version: CACHE_VERSION });
                }
                break;
                
            default:
                console.log('Unknown message type:', type);
        }
    } catch (error) {
        console.error('Error handling service worker message:', error);
    }
});

// Update app badge
async function updateAppBadge(count) {
    try {
        // Validate count
        const badgeCount = parseInt(count) || 0;
        console.log('Setting app badge to:', badgeCount);
        
        // Update app badge if supported
        if ('setAppBadge' in navigator) {
            await navigator.setAppBadge(badgeCount);
            console.log('App badge updated successfully');
        } else {
            console.log('App badge API not supported');
        }
        
        // Update notification badge
        if (badgeCount > 0) {
            try {
                await self.registration.update();
                console.log('Service worker registration updated');
            } catch (error) {
                console.log('Failed to update service worker registration:', error);
            }
        }
    } catch (error) {
        console.error('Failed to update app badge:', error);
    }
}

// Cache data for offline use
async function cacheData(data) {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const response = new Response(JSON.stringify(data.content), {
            headers: { 'Content-Type': 'application/json' }
        });
        await cache.put(data.url, response);
    } catch (error) {
        console.error('Failed to cache data:', error);
    }
}

// IndexedDB helpers for pending data
async function getPendingData() {
    // Implementation would depend on your IndexedDB setup
    return [];
}

async function removePendingData(id) {
    // Implementation would depend on your IndexedDB setup
    return;
}

console.log(`Service Worker loaded - Ranch Fire Alert PWA v${CACHE_VERSION}`);