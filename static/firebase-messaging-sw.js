// Firebase Messaging Service Worker
// Save as: static/firebase-messaging-sw.js

importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging-compat.js');

// Initialize Firebase in service worker
firebase.initializeApp({
    apiKey: "AIzaSyCWIvA2I6kzqokVpq5gjGlMj03Gp3Hwe3E",
    authDomain: "dmr-fns.firebaseapp.com", 
    projectId: "dmr-fns",
    storageBucket: "dmr-fns.firebasestorage.app",
    messagingSenderId: "668810466125",
    appId: "1:668810466125:web:aeb977be6046bc45d3dd04"
});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Received background message:', payload);
    
    const notificationTitle = payload.notification?.title || 'Fire Alert';
    const notificationOptions = {
        body: payload.notification?.body || 'New alert received',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/icon-72.png',
        tag: 'fire-alert',
        requireInteraction: true,
        data: payload.data
    };

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    // Open the app when notification is clicked
    event.waitUntil(
        clients.matchAll().then((clientList) => {
            for (const client of clientList) {
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow('/');
            }
        })
    );
});