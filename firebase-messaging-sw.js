// firebase-messaging-sw.js
// Import Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// REPLACE WITH YOUR ACTUAL FIREBASE CONFIG
// Get from Firebase Console > Project Settings > General > Your apps
const firebaseConfig = {
            apiKey: "AIzaSyCWIvA2I6kzqokVpq5gjGlMj03Gp3Hwe3E",
            authDomain: "dmr-fns.firebaseapp.com",
            projectId: "dmr-fns",
            storageBucket: "dmr-fns.firebasestorage.app",
            messagingSenderId: "668810466125",
            appId: "1:668810466125:web:aeb977be6046bc45d3dd04"
        };

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Get messaging instance
const messaging = firebase.messaging();

// Handle background messages with maximum aggressiveness
messaging.onBackgroundMessage((payload) => {
    console.log('Background message received:', payload);
    
    const notificationTitle = payload.notification?.title || '🔥 EMERGENCY FIRE ALERT 🔥';
    const notificationOptions = {
        body: payload.notification?.body || 'CRITICAL FIRE ALERT - IMMEDIATE ACTION REQUIRED',
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        tag: 'fire-alert-emergency',
        requireInteraction: true, // Forces user to interact
        silent: false, // Ensures sound plays
        vibrate: [1000, 500, 1000, 500, 1000, 500, 1000], // Aggressive vibration pattern
        data: {
            ...payload.data,
            timestamp: Date.now(),
            priority: 'high',
            urgency: 'critical'
        },
        actions: [
            {
                action: 'view',
                title: '🚨 VIEW ALERT',
                icon: '/icon-192.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/icon-192.png'
            }
        ],
        // Additional options for maximum visibility
        renotify: true, // Always show even if same tag
        dir: 'ltr',
        lang: 'en-US'
    };

    // Show multiple notifications for critical alerts
    const severity = payload.data?.severity || 'critical';
    if (severity === 'critical' || severity === 'high') {
        // Show primary notification
        self.registration.showNotification(notificationTitle, notificationOptions);
        
        // Show additional urgent notification after 2 seconds
        setTimeout(() => {
            self.registration.showNotification('🚨 URGENT: FIRE ALERT ACTIVE 🚨', {
                body: 'Check your device immediately for critical fire information',
                icon: '/icon-192.png',
                badge: '/icon-192.png',
                tag: 'fire-alert-urgent',
                requireInteraction: true,
                silent: false,
                vibrate: [2000, 1000, 2000, 1000, 2000],
                data: { type: 'urgent-reminder' }
            });
        }, 2000);
    } else {
        return self.registration.showNotification(notificationTitle, notificationOptions);
    }
});

// Handle notification clicks with maximum urgency
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    // Play alert sound
    if (event.notification.data?.urgency === 'critical') {
        // Create audio context for emergency sound
        const audioContext = new (self.AudioContext || self.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.2);
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }
    
    // Open the app immediately with maximum focus
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            // Try to focus existing window first
            for (const client of clientList) {
                if (client.url.includes(self.location.origin)) {
                    client.focus();
                    // Navigate to alerts tab if possible
                    client.postMessage({ type: 'showAlertsTab' });
                    return;
                }
            }
            
            // If no existing window, open new one
            if (clients.openWindow) {
                return clients.openWindow('/');
            }
        })
    );
});

// Handle notification close events
self.addEventListener('notificationclose', (event) => {
    console.log('Notification closed:', event);
    
    // For critical alerts, show another notification after 30 seconds if not acknowledged
    if (event.notification.data?.urgency === 'critical') {
        setTimeout(() => {
            // Check if app is focused
            clients.matchAll().then(clientList => {
                const hasFocusedClient = clientList.some(client => client.focused);
                if (!hasFocusedClient) {
                    self.registration.showNotification('⚠️ FIRE ALERT STILL ACTIVE ⚠️', {
                        body: 'Critical fire alert requires your immediate attention',
                        icon: '/icon-192.png',
                        badge: '/icon-192.png',
                        tag: 'fire-alert-reminder',
                        requireInteraction: true,
                        silent: false,
                        vibrate: [1500, 750, 1500, 750, 1500],
                        data: { type: 'reminder' }
                    });
                }
            });
        }, 30000);
    }
});