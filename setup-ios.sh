#!/bin/bash

# Ranch Fire Alert iOS App Setup Script
echo "🔥 Setting up Ranch Fire Alert iOS App..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v18 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"

# Install Expo CLI globally
echo "📦 Installing Expo CLI..."
npm install -g @expo/cli

# Install project dependencies
echo "📦 Installing project dependencies..."
npm install

# Create assets directory if it doesn't exist
if [ ! -d "assets" ]; then
    echo "📁 Creating assets directory..."
    mkdir -p assets
fi

# Create placeholder app icons
echo "🎨 Creating placeholder app icons..."
cat > assets/icon.png << 'EOF'
# This is a placeholder for the app icon
# Replace with your actual 1024x1024 app icon
EOF

cat > assets/splash.png << 'EOF'
# This is a placeholder for the splash screen
# Replace with your actual splash screen image
EOF

cat > assets/adaptive-icon.png << 'EOF'
# This is a placeholder for the adaptive icon
# Replace with your actual adaptive icon
EOF

cat > assets/favicon.png << 'EOF'
# This is a placeholder for the favicon
# Replace with your actual favicon
EOF

# Create .env file template
echo "⚙️ Creating environment configuration..."
cat > .env.example << 'EOF'
# API Configuration
API_BASE_URL=https://your-backend-url.com

# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
FIREBASE_APP_ID=your_firebase_app_id
FIREBASE_VAPID_KEY=your_firebase_vapid_key
EOF

echo "📝 Created .env.example - Copy to .env and update with your values"

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Expo
.expo/
dist/
web-build/

# Native
*.orig.*
*.jks
*.p8
*.p12
*.key
*.mobileprovision

# Metro
.metro-health-check*

# Debug
npm-debug.*
yarn-debug.*
yarn-error.*

# macOS
.DS_Store
*.pem

# local env files
.env*.local
.env

# typescript
*.tsbuildinfo

# IDE
.vscode/
.idea/

# Temporary files
*.log
*.tmp
*.temp

# Build outputs
build/
ios/build/
android/build/

# EAS
.easignore

# Testing
coverage/

# Flipper
ios/Pods/
android/.gradle
EOF
fi

# Check if Xcode is installed (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v xcodebuild &> /dev/null; then
        echo "✅ Xcode detected"
    else
        echo "⚠️  Xcode not detected. Install Xcode from the App Store for iOS development."
    fi
fi

# Check if iOS Simulator is available
if command -v xcrun &> /dev/null; then
    if xcrun simctl list devices | grep -q "iPhone"; then
        echo "✅ iOS Simulator detected"
    else
        echo "⚠️  iOS Simulator not found. Install Xcode to get iOS Simulator."
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and update with your configuration"
echo "2. Update API_BASE_URL in src/services/apiService.ts"
echo "3. Add your app icons to the assets/ directory"
echo "4. Run 'npm start' to start the development server"
echo "5. Run 'npm run ios' to open in iOS Simulator"
echo ""
echo "📚 For more information, see README-iOS.md"
echo ""
echo "Happy coding! 🔥" 