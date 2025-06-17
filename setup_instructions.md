# Ranch Fire Alert PWA Setup Guide

## Prerequisites
- Python 3.8+
- Firebase project for push notifications
- SSL certificate (required for PWA features)

## Python Dependencies

Create `requirements.txt`:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
firebase-admin==6.2.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

## Firebase Setup

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project
   - Enable Cloud Messaging

2. **Get Configuration**:
   - In Project Settings > General, copy your web app config
   - In Project Settings > Service Accounts, generate a private key (save as `firebase-key.json`)
   - In Project Settings > Cloud Messaging, copy your VAPID key

3. **Update Configuration**:
   Replace these values in the PWA frontend:
   ```javascript
   const firebaseConfig = {
       apiKey: "your-actual-api-key",
       authDomain: "your-project.firebaseapp.com",
       projectId: "your-actual-project-id",
       storageBucket: "your-project.appspot.com",
       messagingSenderId: "your-sender-id",
       appId: "your-app-id"
   };
   ```

   And add your VAPID key:
   ```javascript
   vapidKey: 'your-vapid-key-here'
   ```

## Installation Steps

1. **Clone/Setup Project**:
   ```bash
   mkdir ranch-fire-alert
   cd ranch-fire-alert
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Project Structure**:
   ```
   ranch-fire-alert/
   ├── app.py
   ├── requirements.txt
   ├── firebase-key.json
   ├── templates/
   │   └── index.html
   ├── static/
   │   ├── sw.js
   │   ├── manifest.json
   │   └── icons/
   │       ├── icon-72.png
   │       ├── icon-192.png
   │       └── icon-512.png
   └── fire_alerts.db (created automatically)
   ```

3. **Create Template Directory**:
   ```bash
   mkdir templates static static/icons
   ```

4. **Move Files**:
   - Save the Python backend code as `app.py`
   - Save the HTML as `templates/index.html`
   - Save the service worker as `static/sw.js`
   - Save the manifest as `static/manifest.json`
   - Add your Firebase service account key as `firebase-key.json`

5. **Create App Icons**:
   Create fire/alert themed icons in various sizes:
   - icon-72.png (72x72)
   - icon-192.png (192x192)
   - icon-512.png (512x512)

## Environment Configuration

Create `.env` file:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///fire_alerts.db
```

## Running the Application

1. **Development**:
   ```bash
   python app.py
   ```
   Visit: http://localhost:5000

2. **Production with HTTPS** (required for PWA):
   ```bash
   gunicorn --bind 0.0.0.0:443 --certfile=cert.pem --keyfile=key.pem app:app
   ```

## SSL Certificate (Required)

PWAs require HTTPS. Options:

1. **Development**: Use ngrok or similar
   ```bash
   pip install pyngrok
   python -c "from pyngrok import ngrok; print(ngrok.connect(5000))"
   ```

2. **Production**: Use Let's Encrypt, Cloudflare, or your hosting provider

## Testing Push Notifications

1. Register a user on the PWA
2. Use the admin tab to send a test alert
3. Test with app in background/foreground
4. Verify notifications work on different devices

## Database Schema

The app creates these tables automatically:
- **Ranch**: Ranch locations and coverage areas
- **User**: Registered users with FCM tokens
- **FireAlert**: Active fire alerts
- **LivestockRequest**: Help requests during emergencies

## Production Considerations

1. **Security**:
   - Use environment variables for secrets
   - Implement user authentication
   - Add rate limiting
   - Validate all inputs

2. **Scalability**:
   - Use PostgreSQL instead of SQLite
   - Add Redis for caching
   - Use task queue for notifications

3. **Monitoring**:
   - Add error logging
   - Monitor notification delivery rates
   - Track user engagement

## Customization

1. **Ranch Areas**: Add your ranch coordinates in the database
2. **Styling**: Modify CSS in the HTML for your brand
3. **Features**: Add more livestock types, contact methods, etc.
4. **Integrations**: Connect to weather APIs, emergency services

## Troubleshooting

- **Notifications not working**: Check VAPID key and Firebase config
- **PWA not installing**: Ensure HTTPS and valid manifest
- **Database errors**: Check file permissions and SQLite installation
- **Firebase errors**: Verify service account key and project settings

## Support

This system replaces SMS text trees with:
- ✅ Free push notifications (no SMS costs)
- ✅ Rich content (images, maps, detailed info)
- ✅ Two-way communication
- ✅ Offline capability
- ✅ Instant updates
- ✅ Better coordination tools

Perfect for rural ranch communities needing reliable emergency communication!