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

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Background message received:', payload);
    
    const notificationTitle = payload.notification?.title || 'Fire Alert';
    const notificationOptions = {
        body: payload.notification?.body || 'Emergency notification',
        icon: '/icon-192.png',
        badge: '/icon-192.png',
        vibrate: [200, 100, 200],
        requireInteraction: true,
        tag: 'fire-alert'
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});