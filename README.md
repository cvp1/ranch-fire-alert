# 🔥 Dragoon Mountain Ranch Fire Alert PWA

A Progressive Web App (PWA) emergency notification system designed specifically for the Dragoon Mountain Ranch community to coordinate fire alerts and livestock evacuation during emergencies.

## 🚨 Features

### Emergency Communication
- **Real-time fire alerts** with severity levels (Low, Medium, High, Critical)
- **Push notifications** that work even when the app is closed
- **Offline capability** - app works without internet connection
- **Community-wide alerts** for the Dragoon Mountain Ranch area

### Livestock Coordination
- **Request livestock help** during emergencies
- **Coordinate evacuations** with neighboring ranchers
- **Track help requests** and status updates
- **Animal-specific details** (cattle, horses, sheep, goats, pigs, etc.)

### User Management
- **Smart login/registration** - enter email or phone to get started
- **Optional password protection** for enhanced security
- **Admin controls** for ranch coordinators
- **User-friendly interface** optimized for mobile and desktop

### Modern PWA Features
- **Install on mobile** - works like a native app
- **Offline functionality** - cached content available without internet
- **Background sync** - pending actions sync when connection returns
- **Rich notifications** - images, actions, and detailed information

## 🛠️ Technology Stack

- **Backend**: Python Flask with SQLAlchemy 2.0+
- **Frontend**: Vanilla JavaScript with PWA features
- **Database**: SQLite with persistent storage
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Caching**: Service Worker with Cache API
- **Authentication**: Simple email/phone-based system with optional passwords

## 🏔️ Ranch Configuration

The system is configured specifically for:
- **Ranch**: Dragoon Mountain Ranch
- **Location**: 31.9190°N, 109.9673°W (Arizona)
- **Coverage Area**: 10-mile radius
- **Default Admin**: `admin@ranch.local` / `admin123`

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker (optional, but recommended)
- Firebase project for push notifications (optional)

### Option 1: Docker Setup (Recommended)

#### Quick Start with Docker Runner Script

The easiest way to run the application is using the provided Docker runner script:

```bash
# Clone the repository
git clone https://github.com/yourusername/ranch-fire-alert.git
cd ranch-fire-alert

# Make the script executable
chmod +x docker-run.sh

# Start the application
./docker-run.sh start

# View logs
./docker-run.sh logs

# Stop containers
./docker-run.sh stop

# Show help
./docker-run.sh help
```

#### Manual Docker Setup

1. **Clone and start with Docker**:
   ```bash
   git clone https://github.com/yourusername/ranch-fire-alert.git
   cd ranch-fire-alert
   docker-compose up -d
   ```

2. **Visit the application**:
   - Desktop: http://localhost:8088
   - Mobile: http://YOUR_IP:8088

### Docker Configuration

The application uses SQLite by default for simplicity and ease of deployment:

- **Database**: SQLite with persistent storage
- **Services**: Flask app + Redis
- **Data persistence**: Docker volumes for database and backups
- **Management**: Convenient `docker-run.sh` script

#### Docker Runner Script (`docker-run.sh`)
A convenient script that handles all Docker operations:

```bash
# Available commands:
./docker-run.sh start      # Start the application
./docker-run.sh stop       # Stop all containers
./docker-run.sh clean      # Remove containers and volumes
./docker-run.sh logs       # View logs
./docker-run.sh status     # Show container status
./docker-run.sh backup     # Create database backup
./docker-run.sh restore    # Restore from backup
./docker-run.sh help       # Show help
```

### Option 2: Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ranch-fire-alert.git
   cd ranch-fire-alert
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create required directories**:
   ```bash
   mkdir templates static static/icons
   ```

4. **Add the application files**:
   - Save `app.py` in the root directory
   - Save HTML content as `templates/index.html`
   - Save service worker as `static/sw.js`
   - Save Firebase service worker as `static/firebase-messaging-sw.js`
   - Save manifest as `static/manifest.json`

5. **Create app icons** (place in `static/icons/`):
   - icon-72.png (72x72)
   - icon-192.png (192x192)
   - icon-512.png (512x512)

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Visit**: http://localhost:8088

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=8088

# Database (SQLite only - no configuration needed)
# Database file will be created at ./data/fire_alerts.db

# Firebase (Optional - for push notifications)
FIREBASE_API_KEY=your-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=your-app-id
FIREBASE_VAPID_KEY=your-vapid-key
```

### Firebase Setup (Optional)

For push notifications:

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project
   - Enable Cloud Messaging

2. **Get Configuration**:
   - Project Settings > General: Copy web app config
   - Project Settings > Service Accounts: Generate private key → `firebase-key.json`
   - Project Settings > Cloud Messaging: Copy VAPID key

3. **Update .env file** with your Firebase values

## 📁 Project Structure

```
ranch-fire-alert/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env                           # Environment configuration
├── docker-compose.yml             # Docker configuration (SQLite)
├── docker-run.sh                  # Docker management script
├── railway.json                   # Railway deployment configuration
├── templates/
│   └── index.html                 # Main application UI
├── static/
│   ├── sw.js                      # Service Worker
│   ├── firebase-messaging-sw.js   # Firebase Service Worker
│   ├── manifest.json              # PWA manifest
│   └── icons/                     # App icons
│       ├── icon-72.png
│       ├── icon-192.png
│       └── icon-512.png
├── firebase-key.json              # Firebase service account (optional)
└── fire_alerts.db                 # SQLite database (auto-created)
```

## 👥 User Guide

### Getting Started
1. **Visit the app** on your device
2. **Enter your email or phone** to get started
3. **Create account** for Dragoon Mountain Ranch
4. **Set optional password** for added security
5. **Install the app** when prompted (mobile/desktop)

### For Ranch Members
- **View fire alerts** in real-time
- **Request livestock help** during emergencies
- **Offer help** to neighbors in need
- **Receive push notifications** for critical alerts

### For Ranch Coordinators (Admins)
- **Send fire alerts** to the community
- **Manage alert severity** levels
- **View system statistics**
- **Coordinate emergency response**

## 🚀 Production Deployment

### Railway Deployment (Recommended)

1. **Connect your GitHub repository** to Railway
2. **Railway will automatically detect** the Flask app
3. **Set environment variables** in Railway dashboard:
   ```bash
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   PORT=8088
   HOST=0.0.0.0
   ```
4. **Create a volume** in Railway and mount it to `/app/data`
5. **Deploy** - Railway will handle the rest!

### Railway Configuration

The `railway.json` file is already configured for optimal deployment:
- **Health check**: `/api/status`
- **Volume mount**: `/app/data` for database persistence
- **Start command**: `python app.py`

### Other Cloud Platforms
1. **Heroku**: `git push heroku main`
2. **DigitalOcean**: App Platform supports Flask
3. **Render**: Connect GitHub, auto-deploy

### Production Checklist
- [ ] HTTPS enabled (required for PWA features)
- [ ] SQLite database with proper backups
- [ ] Firebase notifications configured
- [ ] Environment variables set
- [ ] SSL certificates installed
- [ ] Performance monitoring enabled

## 🔒 Security Notes

This system includes:
- ✅ Simple email/phone authentication
- ✅ Optional password protection
- ✅ SQLAlchemy 2.0+ with proper query syntax
- ✅ Input validation and error handling
- ✅ HTTPS support for production

For production use, consider adding:
- Rate limiting
- Enhanced password hashing (bcrypt)
- Session management
- CSRF protection
- Input sanitization

## 🆘 Troubleshooting

### Common Issues

**Database Errors**:
```bash
# Reset database (loses data)
rm fire_alerts.db
python app.py
```

**Firebase Errors**:
- Check Firebase configuration in .env
- Ensure `firebase-messaging-sw.js` exists in `/static/`
- Verify VAPID key is correct

**Docker Issues**:
```bash
# Restart services
docker-compose restart

# View logs
docker-compose logs -f web

# Reset everything
docker-compose down -v && docker-compose up -d

# Using the runner script
./docker-run.sh logs
./docker-run.sh status
```

**Port Conflicts**:
- Change `PORT=8088` in .env file

**Railway Issues**:
- Ensure volume is mounted to `/app/data`
- Check environment variables are set
- Verify health check endpoint returns 200

### Development Mode

For HTTP development (no PWA features):
- Notifications won't work without HTTPS
- PWA install prompt won't appear
- Service Worker features limited

### Production Mode

For full PWA features:
- HTTPS required
- Valid SSL certificate needed
- Firebase configuration required for notifications

## 📊 System Requirements

### Minimum Requirements
- **Server**: 1 CPU, 512MB RAM
- **Database**: SQLite with persistent storage
- **Network**: HTTP/HTTPS access
- **Browser**: Modern browser with Service Worker support

### Recommended for Production
- **Server**: 2 CPU, 2GB RAM
- **Database**: SQLite with regular backups
- **Network**: HTTPS with valid SSL certificate
- **CDN**: For static asset delivery
- **Monitoring**: Application and database monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Emergency Use Disclaimer

⚠️ **Important**: This app is designed to supplement, not replace, official emergency communication channels. Always follow local emergency services guidance and have backup communication methods available.

For actual emergencies, call 911 immediately.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your configuration files
3. Check browser console for JavaScript errors
4. Review server logs for backend errors
5. Open an issue on GitHub with detailed error information

### Admin Access
- **Email**: admin@ranch.local
- **Password**: admin123
- **Features**: Send alerts, view statistics, manage system

---

**Built with ❤️ for the Dragoon Mountain Ranch community and rural ranch safety**

### Recent Updates
- ✅ Enhanced user authentication system
- ✅ Fixed SQLAlchemy 2.0+ compatibility
- ✅ Added Firebase service worker support
- ✅ Improved error handling and validation
- ✅ Added Docker support with SQLite for easy deployment
- ✅ Enhanced livestock coordination features
- ✅ Simplified database setup with SQLite-only configuration
- ✅ Railway deployment with volume persistence
- ✅ Streamlined Docker management with runner script