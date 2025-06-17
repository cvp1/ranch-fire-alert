# 🔥 Ranch Fire Alert PWA

A Progressive Web App (PWA) emergency notification system designed for rural ranch communities to coordinate fire alerts and livestock evacuation during emergencies.

## 🚨 Features

### Emergency Communication
- **Real-time fire alerts** with severity levels (Low, Medium, High, Critical)
- **Push notifications** that work even when the app is closed
- **Offline capability** - app works without internet connection
- **Ranch-specific alerts** - only receive notifications for your area

### Livestock Coordination
- **Request livestock help** during emergencies
- **Coordinate evacuations** with neighboring ranchers
- **Track help requests** and status updates
- **Animal-specific details** (cattle, horses, sheep, etc.)

### Modern PWA Features
- **Install on mobile** - works like a native app
- **Offline functionality** - cached content available without internet
- **Background sync** - pending actions sync when connection returns
- **Rich notifications** - images, actions, and detailed information

## 🛠️ Technology Stack

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: Vanilla JavaScript with PWA features
- **Database**: SQLite (development) / PostgreSQL (production)
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Caching**: Service Worker with Cache API

## 📱 Screenshots

*Note: Add screenshots of the app in action*

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Firebase project for push notifications
- SSL certificate (required for PWA features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ranch-fire-alert.git
   cd ranch-fire-alert
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create directory structure**
   ```bash
   mkdir templates static static/icons
   ```

4. **Move application files**
   - Save `app.py` in the root directory
   - Save HTML content as `templates/index.html`
   - Save service worker as `static/sw.js`
   - Save manifest as `static/manifest.json`

5. **Firebase setup**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Cloud Messaging
   - Download service account key as `firebase-key.json`
   - Get your VAPID key from Project Settings > Cloud Messaging
   - Update Firebase configuration in the HTML file

6. **Create app icons**
   Create fire/alert themed icons in `static/icons/`:
   - icon-72.png (72x72)
   - icon-192.png (192x192)
   - icon-512.png (512x512)

7. **Run the application**
   ```bash
   python app.py
   ```
   Visit: http://localhost:5000

## 🔧 Configuration

### Firebase Configuration

Replace the placeholder values in `templates/index.html`:

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

Add your VAPID key:
```javascript
vapidKey: 'your-vapid-key-here'
```

### Environment Variables

Create a `.env` file:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///fire_alerts.db
```

## 📊 Database Schema

The application automatically creates these tables:

- **Ranch**: Ranch locations and coverage areas
- **User**: Registered users with FCM tokens
- **FireAlert**: Active fire alerts with severity levels
- **LivestockRequest**: Help requests during emergencies

## 🌐 Production Deployment

### SSL Certificate (Required)
PWAs require HTTPS. Options include:

1. **Development**: Use ngrok
   ```bash
   pip install pyngrok
   python -c "from pyngrok import ngrok; print(ngrok.connect(5000))"
   ```

2. **Production**: Use Let's Encrypt, Cloudflare, or your hosting provider

### Production Server
```bash
gunicorn --bind 0.0.0.0:443 --certfile=cert.pem --keyfile=key.pem app:app
```

## 🧪 Testing

1. Register a user on the PWA
2. Use the admin tab to send a test alert
3. Test notifications with app in background/foreground
4. Verify offline functionality by disconnecting internet
5. Test on multiple devices and browsers

## 🎯 Use Cases

### Perfect for:
- **Rural ranch communities** needing reliable emergency communication
- **Replacing SMS text trees** with modern push notifications
- **Coordinating livestock evacuations** during wildfires
- **Emergency preparedness** for agricultural communities

### Benefits over traditional methods:
- ✅ **Free push notifications** (no SMS costs)
- ✅ **Rich content** (images, maps, detailed information)
- ✅ **Two-way communication** capabilities
- ✅ **Offline functionality** when cell towers are down
- ✅ **Instant updates** to all community members
- ✅ **Better coordination tools** for emergency response

## 🔒 Security Considerations

For production use, implement:

- User authentication and authorization
- Input validation and sanitization
- Rate limiting for API endpoints
- Environment variables for all secrets
- Database access controls
- CSRF protection

## 🚀 Future Enhancements

- [ ] Integration with weather APIs for fire risk assessment
- [ ] GPS tracking for livestock and evacuation routes
- [ ] Integration with emergency services (911, local fire departments)
- [ ] Multi-language support
- [ ] Voice notifications for accessibility
- [ ] Mapping integration for visual fire tracking
- [ ] Analytics dashboard for ranch administrators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section in the setup guide
2. Verify Firebase configuration and VAPID keys
3. Ensure HTTPS is properly configured
4. Check browser console for JavaScript errors
5. Open an issue on GitHub with detailed error information

## 📞 Emergency Use Disclaimer

This app is designed to supplement, not replace, official emergency communication channels. Always follow local emergency services guidance and have backup communication methods available.

---

**Built with ❤️ for rural communities and ranch safety**