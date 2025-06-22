# 🍎 Ranch Fire Alert iOS App

A native iOS app built with React Native and Expo for the Ranch Fire Alert system.

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (v18 or higher)
2. **npm** or **yarn**
3. **Expo CLI**
4. **Xcode** (for iOS development)
5. **iOS Simulator** or **physical iOS device**

### Installation

1. **Install Expo CLI globally:**
   ```bash
   npm install -g @expo/cli
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Run on iOS Simulator:**
   ```bash
   npm run ios
   ```

## 📱 App Features

### 🔥 Fire Alerts
- Real-time fire alert notifications
- Alert severity levels (Critical, High, Medium, Low)
- Location-based alerts
- Alert history and status tracking

### 🐄 Livestock Management
- Livestock evacuation requests
- Shelter and feed requests
- Medical assistance requests
- Request status tracking

### 👨‍💼 Admin Panel
- User management (add, edit, delete users)
- Alert management
- System monitoring
- Analytics dashboard

### 🔐 Authentication
- Secure login/registration
- Email or phone number login
- Password protection
- Session management

### 📍 Location Services
- GPS location tracking
- Geofencing for ranch boundaries
- Location-based alerts
- Emergency contact integration

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
├── context/            # React Context providers
├── screens/            # App screens
├── services/           # API and external services
├── theme/              # Design system and styling
├── types/              # TypeScript type definitions
└── utils/              # Utility functions

assets/                 # Images, icons, and static files
```

## 🎨 Design System

The app uses a consistent design system with:

- **Colors**: Blue primary theme with fire alert severity colors
- **Typography**: Inter font family with consistent sizing
- **Spacing**: 8px grid system
- **Components**: Material Design 3 components via React Native Paper

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
API_BASE_URL=https://your-backend-url.com
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
FIREBASE_APP_ID=your_firebase_app_id
FIREBASE_VAPID_KEY=your_firebase_vapid_key
```

### Backend Integration

Update the API base URL in `src/services/apiService.ts`:

```typescript
const API_BASE_URL = 'https://your-backend-url.com';
```

## 📦 Building for Production

### iOS App Store

1. **Configure app.json:**
   - Update `bundleIdentifier`
   - Set version and build numbers
   - Configure app icons and splash screen

2. **Build for iOS:**
   ```bash
   npm run build:ios
   ```

3. **Submit to App Store:**
   - Use Expo Application Services (EAS)
   - Or build with Xcode and submit manually

### EAS Build (Recommended)

1. **Install EAS CLI:**
   ```bash
   npm install -g @expo/eas-cli
   ```

2. **Login to Expo:**
   ```bash
   eas login
   ```

3. **Configure EAS:**
   ```bash
   eas build:configure
   ```

4. **Build for iOS:**
   ```bash
   eas build --platform ios
   ```

## 🔔 Push Notifications

The app supports push notifications for:

- Fire alerts
- Livestock requests
- System updates
- Emergency notifications

### Setup

1. **Configure Firebase:**
   - Set up Firebase project
   - Add iOS app to Firebase
   - Download `GoogleService-Info.plist`

2. **Configure Expo:**
   - Add Firebase configuration to `app.json`
   - Configure notification settings

3. **Test Notifications:**
   ```bash
   expo push:ios:send --to <device-token> --title "Test" --body "Test notification"
   ```

## 📍 Location Services

The app uses location services for:

- Accurate fire alert locations
- Geofencing for ranch boundaries
- Emergency response coordination

### Permissions

The app requests these location permissions:

- **When In Use**: For active location tracking
- **Always**: For background location updates (optional)

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Data Encryption**: All sensitive data is encrypted
- **Secure Storage**: Credentials stored in iOS Keychain
- **Network Security**: HTTPS-only API communication

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
npm run test:e2e
```

### Manual Testing
- Test on different iOS versions
- Test on different device sizes
- Test offline functionality
- Test notification delivery

## 🐛 Debugging

### Development Tools

1. **React Native Debugger**
2. **Flipper** (Facebook's debugging platform)
3. **Expo DevTools**

### Common Issues

1. **Metro bundler issues:**
   ```bash
   npx expo start --clear
   ```

2. **iOS Simulator issues:**
   ```bash
   npx expo run:ios --clear
   ```

3. **Dependency issues:**
   ```bash
   rm -rf node_modules && npm install
   ```

## 📊 Analytics

The app includes analytics for:

- User engagement
- Alert effectiveness
- Feature usage
- Error tracking

## 🔄 Updates

### Over-the-Air Updates

The app supports OTA updates via Expo Updates:

```bash
eas update --branch production --message "Bug fixes"
```

### App Store Updates

For major updates, submit to App Store:

```bash
eas submit --platform ios
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔗 Links

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [React Native Paper](https://callstack.github.io/react-native-paper/)
- [Expo Notifications](https://docs.expo.dev/versions/latest/sdk/notifications/)

---

**Built with ❤️ for ranch safety and emergency response** 